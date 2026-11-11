#!/usr/bin/env python3
"""Build theme data from the pinned, bundled Monkeytype source (no network).

Monkeytype colors are parsed independently from its upstream TypeScript data,
not copied from generated prototype CSS. The three astraJLPT design palettes
are explicitly local source data and are extracted from the supplied fixture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMIT = "09a8fd0a7a6e598890c5b557faf5851c1642a0ae"
SOURCE_URL = f"https://github.com/monkeytypegame/monkeytype/blob/{COMMIT}/frontend/src/ts/constants/themes.ts"
RAW_URL = f"https://raw.githubusercontent.com/monkeytypegame/monkeytype/{COMMIT}/frontend/src/ts/constants/themes.ts"
COLORS_URL = f"https://github.com/monkeytypegame/monkeytype/blob/{COMMIT}/frontend/src/ts/utils/colors.ts"
SOURCE_SHA256 = "9fc1493a06393fd4b6f0e9cb43800b1e965a17706b18fd094d256dba023ffc38"
PALETTE_FIELDS = ("bg", "main", "caret", "sub", "subAlt", "text", "error")
ALL_COLOR_FIELDS = set(PALETTE_FIELDS) | {"errorExtra", "colorfulError", "colorfulErrorExtra"}
ORIGINAL_FIELDS = ("bg", "paper", "raised", "text", "muted", "edge", "accent", "correct", "wrong")
HEX = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class ObjectLiteralParser:
    """Parse the narrow data-only TS object grammar, never execute source."""

    def __init__(self, text: str):
        self.text = text
        self.position = 0

    def skip(self):
        while True:
            match = re.match(r"\s+|//[^\n]*(?:\n|$)|/\*.*?\*/", self.text[self.position:], re.S)
            if match is None:
                return
            self.position += match.end()

    def take(self, character: str):
        self.skip()
        if not self.text.startswith(character, self.position):
            raise ValueError(f"Expected {character!r} at object offset {self.position}")
        self.position += len(character)

    def identifier(self):
        self.skip()
        match = re.match(r"[A-Za-z_$][A-Za-z0-9_$]*", self.text[self.position:])
        if match is None:
            raise ValueError(f"Expected a data property at object offset {self.position}")
        self.position += match.end()
        return match.group()

    def string(self):
        self.skip()
        value, length = json.JSONDecoder().raw_decode(self.text[self.position:])
        if not isinstance(value, str):
            raise ValueError("Only string literals are supported here")
        self.position += length
        return value

    def value(self):
        self.skip()
        character = self.text[self.position:self.position + 1]
        if character == "{":
            return self.object()
        if character == '"':
            return self.string()
        word = self.identifier()
        if word in ("true", "false"):
            return word == "true"
        raise ValueError("Unexpected executable/non-data value: " + word)

    def object(self):
        self.take("{")
        result = {}
        self.skip()
        while not self.text.startswith("}", self.position):
            key = self.string() if self.text.startswith('"', self.position) else self.identifier()
            self.take(":")
            if key in result:
                raise ValueError("Duplicate upstream property: " + key)
            result[key] = self.value()
            self.skip()
            if self.text.startswith(",", self.position):
                self.position += 1
                self.skip()
            elif not self.text.startswith("}", self.position):
                raise ValueError("Expected a comma or end of source object")
        self.take("}")
        return result


def parse_themes(source: str):
    start = re.search(r"export const themes:\s*Record<ThemeName, Theme>\s*=\s*", source)
    if start is None:
        raise ValueError("Could not locate the explicit upstream themes record")
    parser = ObjectLiteralParser(source[start.end():])
    themes = parser.object()
    parser.take(";")
    for name, theme in themes.items():
        if not isinstance(theme, dict) or set(theme) - ALL_COLOR_FIELDS - {"hasCss"}:
            raise ValueError("Unexpected upstream theme schema: " + name)
        if not ALL_COLOR_FIELDS.issubset(theme):
            raise ValueError("Incomplete upstream theme colors: " + name)
        if any(not isinstance(theme[key], str) or not HEX.fullmatch(theme[key]) for key in ALL_COLOR_FIELDS):
            raise ValueError("Invalid upstream hex color: " + name)
        if "hasCss" in theme and not isinstance(theme["hasCss"], bool):
            raise ValueError("Invalid upstream hasCss metadata: " + name)
    if len(themes) != 187:
        raise ValueError("The pinned snapshot must contain exactly 187 themes")
    return themes


def is_dark(background: str) -> bool:
    # Same decision as upstream utils/colors.ts isColorDark(hex): HSL L < 50.
    # Every background in this pinned snapshot is an opaque RGB color.
    value = background[1:]
    if len(value) == 3:
        value = "".join(character * 2 for character in value)
    if len(value) != 6:
        raise ValueError("This snapshot's classifier expects opaque RGB backgrounds")
    channels = [int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    lightness = round((max(channels) + min(channels)) * 50, 1)
    return lightness < 50


def originals(source: str):
    selectors = [
        ("jlpt_paper", r"body:has\(#theme-light:checked\)\{--bg:([^}]+)\}", False),
        ("astraJLPT_dark", r"body\{--bg:([^}]+)\}", True),
        ("astraJLPT_sepia", r"body:has\(#theme-sepia:checked\)\{--bg:([^}]+)\}", False),
    ]
    result = []
    for name, pattern, dark in selectors:
        match = re.search(pattern, source)
        if match is None:
            raise ValueError("Missing local design palette: " + name)
        values = dict(re.findall(r"--([\w-]+):([^;]+)", "--bg:" + match.group(1)))
        if any(key not in values or not HEX.fullmatch(values[key]) for key in ORIGINAL_FIELDS):
            raise ValueError("Invalid local design palette: " + name)
        result.append({"id": name, "name": name, "dark": dark, "colors": {key: values[key] for key in ORIGINAL_FIELDS}})
    return result


def compare_prototype(themes, prototype: str):
    """Verification only: imported values always originate in upstream TS."""
    old = {
        match.group(1): dict(re.findall(r"--mt-([\w-]+):(#[0-9a-fA-F]+)", match.group(2)))
        for match in re.finditer(r"body:has\(#theme-mt-([^:]+):checked\)\{([^}]+)\}", prototype)
    }
    if set(themes) != set(old):
        raise ValueError("The prototype and pinned upstream theme IDs differ")
    for name, values in themes.items():
        for field in PALETTE_FIELDS:
            old_field = "sub-alt" if field == "subAlt" else field
            if values[field] != old[name][old_field]:
                raise ValueError(f"Upstream/prototype color mismatch: {name}.{field}")
    return len(themes) * len(PALETTE_FIELDS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "vendor/monkeytype/themes.ts")
    parser.add_argument("--original-source", type=Path, default=ROOT / "vendor/design_lab_v13.html")
    parser.add_argument("--output", type=Path, default=ROOT / "data/themes.json")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/source_manifest.json")
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError("Bundled source checksum differs from the pinned Monkeytype snapshot")
    imported = parse_themes(source_bytes.decode("utf-8"))
    prototype = args.original_source.read_text(encoding="utf-8")
    compared = compare_prototype(imported, prototype)
    upstream = {"url": SOURCE_URL, "rawUrl": RAW_URL, "commit": COMMIT, "sha256": digest}
    output = {
        "version": 1,
        "upstream": upstream,
        "originals": originals(prototype),
        "monkeytype": [
            {"id": name, "name": name.replace("_", " "), "dark": is_dark(imported[name]["bg"]),
             "colors": {key: imported[name][key] for key in PALETTE_FIELDS}}
            for name in sorted(imported)
        ],
    }
    dark_count = sum(theme["dark"] for theme in output["monkeytype"])
    if dark_count != 124:
        raise ValueError("Pinned upstream light/dark classification changed unexpectedly")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8")) if args.manifest.exists() else {"version": 1}
    manifest["monkeytype"] = {
        **upstream,
        "bundledSource": "vendor/monkeytype/themes.ts",
        "license": "vendor/monkeytype/LICENSE",
        "importer": "tools/import_monkeytype.py",
        "themeCount": len(imported),
        "colorFields": list(PALETTE_FIELDS),
        "verifiedExactPrototypeColorStrings": compared,
        "classification": {
            "source": COLORS_URL,
            "method": "Upstream isColorDark(bg): HSL lightness below 50% is dark; at or above 50% is light.",
            "dark": dark_count,
            "light": len(imported) - dark_count,
            "intentionalDifference": "v13's undocumented static tags were 132 dark/55 light. v14 uses the upstream classifier (124/63); palette colors are unchanged.",
        },
        "localPaletteSource": "vendor/design_lab_v13.html; three explicit astraJLPT design palettes, not Monkeytype records",
        "originalOrder": [theme["id"] for theme in output["originals"]],
        "defaultTheme": "astraJLPT_dark",
        "mappingPolicy": "Untouched palette data are separate from the provisional astraJLPT role mapping in the application.",
    }
    for path, content in [(args.output, output), (args.manifest, manifest)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"monkeytype": len(imported), "originals": len(output["originals"]), "exactColorMatches": compared, "dark": dark_count, "light": len(imported) - dark_count}))


if __name__ == "__main__":
    main()
