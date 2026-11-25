# N1_2002 written audit — H25

The available written audit is complete as of 26 October 2026. The result is **incomplete: partial practice paper**, containing all **124 scored questions (65 vocabulary,59 reading/grammar),496 choices and16 contexts**, in13 sections. One known unscored vocabulary ProblemIV example is missing: the DOC/individual answer table lists `例=4`, but its prompt and four choices were not recovered. No example has been fabricated and the result must not be presented as a complete timed exam. PDF integration remains `pending_after_h23`.

All scored questions, choices, keys, instructions, required contexts, surviving notes and marks were reviewed. Four content fields depart from the principal; one repair is provisional. The11 public cases comprise that repair, eight passage-auxiliary uncertainties, the missing example and unavailable original covers. Listening and audio were excluded.

## Sources and actual coverage

The principal is `src/JLPT N1-N5, Past papers/N1/1995-2009.12日本语能力测试真题详解N1.pdf`, SHA-256 `e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00`. Its written headings establish2002 and1級. The [official2011 JLPT guide](https://www.jlpt.jp/reference/pdf/guide2011.pdf), physical2, establishes the annual December schedule through2008; the month does not come from the folder name alone.

| Witness | Inspected written regions |
|---|---|
| Principal collection | Vocabulary326–330 above listening; reading/grammar333–341 above keys; written keys341–343; vocabulary explanations343–346 above listening; reading explanations348 below the reading heading through355 above the listening script. |
| Principal front matter | Physical1–3, reused from the earlier exact-file inspection in this run. |
| Written DOC | All vocabulary1–8, reading17 below the reading heading–32, written key images33–34, Chinese reading translations47 below their heading–49 in the private49-page conversion. |
| Related individual PDF | The same full written regions1–8,17–34 and47–49, including all four graph options and both written key tables. |
| Separate translation PDF | Physical9 below阅读 through12: all eight reading translations and translated citations. |

The written DOC SHA-256 is `d3b6ac0d629afcc579a46cfbbe7a3df3939be16a62519390c75c5fcc59a35f3b`; the individual PDF is `ed2f9481353071b143aeecc77330a7d63a421bd1bb6446d9c3821f0be6530fa2`; the separate translation PDF is `b95ad6d16e96dcc610fe1ed8b3c4dec2e98e628d678bcdeb5d1e2495ac2bdb8e`. Exact indexed paths and derivative hashes are in [source_metadata.json](audit_work/source_metadata.json), [source_selection.json](audit_work/source_selection.json) and [inspection_derivatives.json](audit_work/inspection_derivatives.json). The two explicitly listening-only DOCs and listening-advice PDF were excluded without content auditing.

The DOC and individual PDF have the same normalized vocabulary text; their normalized reading text differs only by trailing答案. They are related retypes, not independent votes. Each was still read visually, including image keys and graphs; the DOC image keys are clearer. The collection was selected after actual comparison because it preserves fuller reference marks and instructions and includes explanations. Tier alone did not decide the principal. The private principal copy is byte-identical and retains its filename. Original source files remain unchanged.

Missing-editorial preflight passed on five consecutive complete vocabulary questions16–20 on individual physical2. Existing OCR supplied navigation only and was checked against source pixels; no fresh OCR was created. Candidate TSV rows are zero. The initial editorial was absent and case/fixlog prefixes were empty.

## Decisions and gaps

[Item-level review](audit_work/item_review.json) records all124 answer rationales and exact source-page associations. All124 keys agree with the inspected written tables and Japanese reasoning. The vocabulary explanations have substantial printed-number drift: their III21/22/24/25/26 concern questions24/26/28/29/33; IV27–31 concern36–40, V32–46 concern41–55, VI47–51 concern56–60, and VII52–56 concern61–65. They were matched by content, not by mislabeled numbering.

The four current departures are recorded in [principal_differences_N1_2002.jsonl](principal_differences_N1_2002.jsonl):

- Vocabulary36 option4: secondは→が, medium confidence. The principal and related local retypes say `彼はとても話し方は…`; a bounded retype saysが. Ordinary grammatical scope supports the repair, but double-topic contrast is possible and the original is unverified. The tested丁 and key1 do not change.
- Reading passage2: `駅前も`→`駅前の` and `我輩は猫である`→`吾輩は猫である`. A bounded retype supports both; the [National Diet Library title record](https://ndlsearch.ndl.go.jp/books/R100000002-I000000843182) independently establishes the book title. Both small corrections share one content field.
- Reading12 option3: `卒業`→`学業`, supported by the passage’s academic-work contrast, explanation350 and the focused retype. The distractor remains wrong because it concerns achievement rather than enjoyment; key1 is unchanged.
- Grammar46 stem: `見る物`→`見る者`, supported by the same grammar example in the [MLC publisher grammar list](https://www.mlcjapanese.co.jp/Download/N1_Grammar.pdf), physical21, entry377, and the focused retype. MLC text was inspected; screenshot retrieval failed. Key4 is unchanged.

The [bounded external retype](https://www.scribd.com/doc/23637086/2002) is unverified text with substantial OCR noise and no verified original-page custody. It was not admitted as a principal or counted as independent. It contains additional Japanese citations for all eight passages and additional lexical-note blocks for seven passages; the local principal only preserves the six notes in passage3. The separate Chinese translation supplies translated citations (passages1–2 on10,3–7 on11,8 on12), which corroborate passage identity but not exact Japanese wording or marker positions. These auxiliary gaps remain eight content-field cases; no uncertain original note wording or location was manufactured.

The original covers remain unavailable after local and bounded external investigation. No original timing, cover score, page count or complete-cover text has been invented. Raw weights visible in the DOC’s written key tables are retained as per-question section weights (vocabulary1/2, reading5/2), without treating raw totals90/187 or conversion annotations as authenticated cover facts.

The missing vocabularyIV example has a public unit-level gap case and drives the partial classification even though all scored questions survive. There are no recovered worked examples. [unresolved_cases_N1_2002.jsonl](unresolved_cases_N1_2002.jsonl) contains1 provisional fix and10 unresolved cases.

The principal reading21 key4 is correct: the Japanese pleasure passage contrasts non-instrumental pleasure with constant purpose-driven action. The individual/DOC Chinese translation wrongly emphasizes enjoyment as the point; collection explanation351, the separate translation and every key table support4. Grammar52’s principal explanation354 reverses the sense of negative option3; retain the actual option and key2. These supplementary translation/explanation defects are not silently imported into exam fields.

Preserved principal forms include `小さい共同体`, `やみくも`, `自分表現`, `明日`, `周囲から…されて`, `我慢できなかった` and `どんなことをしてでも助けた`. Earlier working suspicion about小さいな belonged to the comparator, not the principal. Vocabulary35 option4 is visually蚶虫; deliberate wrong orthography is retained. Vocabulary58 option2’s underline endsむいたら. Final targeted pixels show grammar43 option1が分けて and passage8’s26.7%へ減少; OCR omissions do not become editorial departures.

## Structure and figures

Eight vocabulary target groups retain their boxed references and tested spans. Underlines, double underlines, circled passage references, six surviving note calls/definitions and paragraph structure are preserved. No source-supported ordinary question ruby was recovered; explanation-only ruby was excluded. Old shared/level1 revision6 supplies ordinary presentation, with no local render overrides or chosen variants. All16 contexts bind to their question groups by exact content/question digests. Original writing direction remains unknown; the recorded level-profile fallback applies. Secondary page breaks are not forced.

Reading23 contains four source graph options. [graph_extractions.json](audit_work/graph_extractions.json) records exact source pages338–339, image xrefs1340/1344, lossless180-degree orientation correction, pixel crop coordinates and hashes. Every crop was viewed and retains the four sex/time row labels, hatched/black/dotted legend, full0–100% axis, ticks and border. Each image remains inside its own option with a byte-identical separate PNG. Choice4 matches all eight passage percentages. Wrong-choice bars and row assignments are retained exactly; no unprinted bar-end values are inferred. Later native artwork, if needed, and final source-versus-output image review remain deferred integration requirements.

## Principal assessment and validation

The completed method1 index is **127**:100 unverified provenance +10 for one missing example block +5 for one major field (reading12 option3) +4 for two minor fields (passage2 and grammar46) +8 for uncertain fields (vocabulary36 option4 and seven passage-content fields). Passage2’s auxiliary uncertainty is subsumed by its higher minor category. Covers do not add a fictitious content unit, and repeated concerns within a field are not counted twice. Separate explanation errors are reported above, not charged as exam fields. The collection’s publisher/authorization statements do not authenticate exact issuer custody; appearance and retypesetting alone do not establish known recollection reconstruction.

Canonical editorial/case/fixlog checks pass with `--expect vocab=65 --expect reading=59 --allow-incomplete`, no errors or warnings. Old3.9.0 JSON Schema, principal-index and current-departure checks pass. The183 ledger rows (39 section fields,140 item creations,4 repairs) replay exactly, as do root creation and the one later source-region binding correction. Question/choice/key counts, eight target groups,16 context bindings, four embedded asset hashes, source hashes and unchanged frozen dependencies pass available checks. The entire final text was read back; the audit note is reviewed before queue advancement.

Two pinned-runtime checks remain unavailable: `model.compose` and renderer collectors lack frozen `rubi-restore/tools/ruby_core.py`; publication identity rejects the immutable registry’s absolute live-source paths under the isolated root. No missing live helper, substitute module, parser change or registry change was introduced. These are explicit common integration requirements, not claimed passes. Available identity/profile/style/inferred-source checks pass. Receipts are in `preprocess/audit_runs/2026-10-26_handoff25_non_uars/validation/N1_2002/`.

All available required source checks are complete. Listening/audio, native exam-PDF composition and rendering, publication, live files and other handoffs were outside this audit.
