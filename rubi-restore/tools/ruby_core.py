"""Exact rich-text projection and immutable schema-v2 sidecar application."""
from __future__ import annotations
import copy
import hashlib
import html
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser

PROJECTION_VERSION = "html-base-codepoints-v1"
KANJI_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002ffff々〆〇]")
BLOCKS = {"p", "div", "li", "tr", "td", "th", "br", "hr", "h1", "h2", "h3", "h4"}
VOID = {"br", "hr", "img", "input", "meta", "link", "wbr", "area", "base", "embed", "source"}

def json_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()).hexdigest()

def file_hash(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def hira(value):
    return "".join(chr(ord(c)-0x60) if "\u30a1" <= c <= "\u30f6" else c for c in value)

class Projection(HTMLParser):
    """Offsets are Unicode code points; anchors may not cross HTML text nodes."""
    def __init__(self, value):
        super().__init__(convert_charrefs=False)
        self.is_html = isinstance(value, dict)
        self.raw = value["html"] if self.is_html else value
        self.chars, self.mapping, self.ruby, self.underlined = [], [], [], []
        self.stack, self.active_ruby = [], None
        self.node = 0
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer("\n", self.raw))
        if self.is_html:
            self.feed(self.raw)
            self.close()
            if self.active_ruby is not None:
                raise ValueError("Unclosed ruby")
        else:
            for i, c in enumerate(self.raw):
                self.chars.append(c)
                self.mapping.append((i, i+1, 0, False))
        self.text = "".join(self.chars)
    def pos(self):
        line, col = self.getpos()
        return self.lines[line-1] + col
    def hidden(self):
        return any(tag in {"rt","rp","script","style"} for tag, _ in self.stack)
    def boundary(self):
        if not self.hidden() and self.chars and self.chars[-1] != "\n":
            self.chars.append("\n")
            self.mapping.append(None)
    def handle_starttag(self, tag, attrs):
        if tag in BLOCKS:
            self.boundary()
        if tag == "ruby":
            if self.active_ruby is not None:
                raise ValueError("Nested ruby is unsupported")
            self.active_ruby = {"start":len(self.chars), "reading":"", "rt_count":0}
        if tag == "rt" and self.active_ruby is not None:
            self.active_ruby["rt_count"] += 1
        underline = tag == "u" or any(k == "style" and v and "underline" in v.lower() for k,v in attrs)
        if tag not in VOID:
            self.stack.append((tag,underline))
        self.node += 1
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if tag == "ruby" and self.active_ruby is not None:
            group = self.active_ruby
            group["end"] = len(self.chars)
            group["base"] = "".join(self.chars[group["start"]:group["end"]])
            self.ruby.append(group)
            self.active_ruby = None
        if tag in {t for t,_ in self.stack}:
            index = max(i for i,(t,_) in enumerate(self.stack) if t == tag)
            self.stack = self.stack[:index]
        if tag in BLOCKS:
            self.boundary()
        self.node += 1
    def append(self, text, start, end=None):
        if any(t == "rt" for t,_ in self.stack) and self.active_ruby is not None:
            self.active_ruby["reading"] += text
        if self.hidden():
            return
        under = any(u for _,u in self.stack)
        for i,c in enumerate(text):
            self.chars.append(c)
            self.mapping.append((start+i if end is None else start, start+i+1 if end is None else end, self.node, under))
    def handle_data(self, data):
        self.append(data,self.pos())
    def handle_entityref(self,name):
        raw = "&"+name+";"
        self.append(html.unescape(raw),self.pos(),self.pos()+len(raw))
    def handle_charref(self,name):
        raw = "&#"+name+";"
        self.append(html.unescape(raw),self.pos(),self.pos()+len(raw))
    def raw_span(self,start,end):
        if not 0 <= start < end <= len(self.text):
            raise ValueError("Span out of bounds")
        maps=self.mapping[start:end]
        if any(x is None for x in maps) or len({x[2] for x in maps}) != 1:
            raise ValueError("Span crosses structural/text-node boundary")
        if (start and self.mapping[start-1] and self.mapping[start-1][:2] == maps[0][:2]) or (end<len(self.mapping) and self.mapping[end] and self.mapping[end][:2] == maps[-1][:2]):
            raise ValueError("Span splits a multi-codepoint entity")
        return maps[0][0],maps[-1][1]
    def overlaps_ruby(self,start,end):
        return any(start<r["end"] and end>r["start"] for r in self.ruby)
    def is_underlined(self,start,end):
        return any(x and x[3] for x in self.mapping[start:end])

def field_role(level,section,slot,item=None):
    heading=Projection(section["heading"]).text.replace(" ","").replace("　","")
    if "読み方" in heading or "ひらがなでどう" in heading:
        task="reading_test"
    elif ("漢字で書" in heading or "漢字に" in heading or ("どうかきますか" in heading and "ひらがなで" not in heading)):
        task="orthography_test"
    elif "★" in heading or any("★" in Projection(i.get("stem","")).text for i in section["items"]):
        task="star"
    elif "文章全体" in heading or ("から" in heading and "文章の意味" in heading):
        task="cloze"
    elif any(i.get("type") in {"passage","table"} for i in section["items"]) or ("質問" in heading or "問い" in heading or "ぶんしょうを" in heading):
        task="reading"
    elif "使い方" in heading or "つかいかた" in heading:
        task="usage"
    elif "意味が最も近" in heading or "だいたいおなじ" in heading:
        task="paraphrase"
    elif "次の文" in heading or "つぎの文" in heading or (section["part"]=="reading" and level in {"N3","N4","N5"}):
        task="grammar"
    elif heading.strip():
        task="vocabulary"
    else:
        task="unknown"
    role="heading" if slot=="heading" else ("option" if slot.startswith("options/") else (item.get("type","stem") if item else "stem"))
    return task,role

def iter_fields(doc):
    for si,s in enumerate(doc["sections"]):
        task,role=field_role(doc["unit"][:2],s,"heading")
        yield dict(owner=s["id"],section=s["id"],slot="heading",pointer=f"/sections/{si}/heading",value=s["heading"],task=task,role=role,part=s["part"])
        for ii,item in enumerate(s["items"]):
            for slot in ["stem","content"]:
                if slot in item:
                    task,role=field_role(doc["unit"][:2],s,slot,item)
                    yield dict(owner=item["id"],section=s["id"],slot=slot,pointer=f"/sections/{si}/items/{ii}/{slot}",value=item[slot],task=task,role=role,part=s["part"])
            for oi,value in enumerate(item.get("options",[])):
                task,role=field_role(doc["unit"][:2],s,f"options/{oi}",item)
                yield dict(owner=item["id"],section=s["id"],slot=f"options/{oi}",pointer=f"/sections/{si}/items/{ii}/options/{oi}",value=value,task=task,role=role,part=s["part"])

def protected(field,level,proj,start,end):
    if field["task"] == "unknown":
        return "unknown_task"
    if level in {"N4","N5"} and field["part"]=="vocab":
        return "lower_level_vocabulary_policy"
    if field["task"] in {"reading_test","orthography_test"}:
        if field["role"] in {"option","example"}:
            return "tested_reading_or_orthography"
        if proj.is_underlined(start,end):
            return "tested_target"
        # A missing underline is not permission to infer which word is tested.
        if field["role"]=="stem" and not any(x and x[3] for x in proj.mapping):
            return "unmarked_test_target"
    return None

def resolve(doc,pointer):
    parts=pointer.strip("/").split("/")
    node=doc
    for key in parts[:-1]:
        node=node[int(key)] if isinstance(node,list) else node[key]
    key=int(parts[-1]) if isinstance(node,list) else parts[-1]
    return node,key

def strip_added(value):
    """Not used to relocate anchors; only a renderer may choose to strip provenance tags."""
    return value

def apply_overlay(doc,overlay,editorial_sha256):
    if overlay["overlay_schema_version"] != 1 or overlay["projection_version"] != PROJECTION_VERSION:
        raise ValueError("Unsupported overlay/projection version")
    if overlay["unit_id"] != doc["unit"] or overlay["editorial_sha256"] != editorial_sha256:
        raise ValueError("Stale/wrong editorial identity")
    if overlay["editorial_content_sha256"] != json_hash(doc):
        raise ValueError("Stale editorial content")
    out=copy.deepcopy(doc)
    fields={f["pointer"]:f for f in iter_fields(doc)}
    groups={}
    seen=set()
    for a in overlay["annotations"]:
        if a["annotation_id"] in seen:
            raise ValueError("Duplicate annotation ID")
        seen.add(a["annotation_id"])
        if a["decision"]!="accepted" or a["origin"]!="project_rubi_restore":
            raise ValueError("Unaccepted or unsupported origin")
        groups.setdefault(a["pointer"],[]).append(a)
    for pointer,annotations in groups.items():
        if pointer not in fields:
            raise ValueError("Unknown field")
        field=fields[pointer]; value=field["value"]
        proj=Projection(value); inserts=[]; previous_end=-1
        for a in sorted(annotations,key=lambda a:a["start"]):
            if a["owner_id"]!=field["owner"] or a["section_id"]!=field["section"] or a["field"]!=field["slot"]:
                raise ValueError("Owner/field mismatch")
            if a["field_sha256"]!=json_hash(value):
                raise ValueError("Stale field hash")
            start,end=a["start"],a["end"]
            if not isinstance(start,int) or not isinstance(end,int) or start < 0 or end <= start or end > len(proj.text):
                raise ValueError("Invalid annotation bounds")
            if start<previous_end:
                raise ValueError("Overlapping annotations")
            previous_end=end
            if proj.text[start:end]!=a["base"] or not KANJI_RE.search(a["base"]):
                raise ValueError("Base mismatch")
            if not a["reading"] or re.search(r"[^\u3040-\u309f\u30fc]",a["reading"]):
                raise ValueError("Invalid reading")
            if proj.overlaps_ruby(start,end):
                raise ValueError("Existing ruby overlap")
            if protected(field,doc["unit"][:2],proj,start,end):
                raise ValueError("Protected task span")
            lo,hi=proj.raw_span(start,end)
            inserts.append((lo,hi,a))
        if not inserts:
            continue
        raw=proj.raw
        if not proj.is_html:
            # Convert a plain value without changing its decoded base text or whitespace.
            inserts=[(len(html.escape(raw[:lo],quote=False)),len(html.escape(raw[:hi],quote=False)),a) for lo,hi,a in inserts]
            raw=html.escape(raw,quote=False)
        for lo,hi,a in sorted(inserts,reverse=True,key=lambda row:row[0]):
            aid=html.escape(a["annotation_id"],quote=True)
            raw=raw[:lo]+f'<ruby data-rubi-origin="project_rubi_restore" data-rubi-id="{aid}">'+raw[lo:hi]+"<rt>"+html.escape(a["reading"])+"</rt></ruby>"+raw[hi:]
        parent,key=resolve(out,pointer);parent[key]={"html":raw}
        if Projection(parent[key]).text != proj.text:
            raise ValueError("Base projection changed")
        # Original markup is preserved byte-for-byte outside insertion points.
    return out

