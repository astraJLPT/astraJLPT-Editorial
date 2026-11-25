# N2_2003 written audit — H25

Completed 26 October 2026 with explicit uncertainty and two isolated-runtime validation limitations. The maintained Old 3.9.0 editorial contains **65 vocabulary questions, 57 reading/grammar questions, 488 choices and 25 contexts** in 12 sections. All 122 keys were checked against the written tables and independently assessed. No worked example occurs in the available written witnesses. PDF integration remains `pending_after_h23`.

Original covers and original appearance are unestablished. No original timing, score or booklet page count has been invented. Listening regions and audio were excluded.

## Evidence and coverage

The principal is the indexed collection `src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/1991年-2009年/1995-2009.pdf`, SHA-256 `115e8c098ee3caed702d29a24d2ce0c883c3ad9152e21eee4200fc4e80f2a3fb`. Its 2003 and 2級 headings establish the year and historical level. The [official 2011 JLPT guide](https://www.jlpt.jp/reference/pdf/guide2011.pdf), physical page 2, establishes the pre-2009 annual December schedule; the month does not come solely from the owner ID.

| Source region | Completed inspection |
|---|---|
| Collection physical 254–257 | All 65 vocabulary questions, instructions, target sentences, choices and tested marks. Page 257 stops after question 65 above listening. |
| Collection physical 260–268 | All 21 reading questions, nine passages/graph contexts and 36 grammar questions. Page 260 starts at the reading heading below listening; page 268 question review stops above keys. |
| Collection physical 268–269 | Both written answer tables, matched by question and choice order. |
| Collection 269–272 top; 273 bottom–281 top | All written vocabulary and reading/grammar explanations; intervening listening explanations excluded. |
| Collection physical 1–3 | Title, imprint, credits and foreword, for provenance only. |
| Both individual question-and-answer PDFs | Complete written pages 1–4 and 7 below the reading heading through 16, plus the written key tables on 17–18. |
| Indexed `2003年听力原文+答案.doc` | Heading and tail classification only: listening transcript and listening keys, with no written exam material. Its conversion was for source classification, not a listening audit. |

The Tier 1 individual PDF has SHA-256 `01db506edc387dc789c13726c6045273935e6ceb21d8d7bb1fcd84bba681910c`; the Tier 2 individual PDF has SHA-256 `3d74d3c5087e989cd7eda1adfd4fb8b8abe3c478631bfacb52dd50c1226f86f4`. They share layout and creation metadata but differ slightly in decoded pixels. They are related variants, not independent confirmations. The principal preserves fuller instructions, underlines and reading references, so it was selected after actual comparison rather than by tier alone. All source originals and private mirrors match their indexed hashes. The principal inspection copy is byte-identical and retains its filename.

The missing-editorial preflight covered five consecutive complete non-example questions 1–5 and their common instruction, first on the individual PDF and then on collection physical 254. Existing indexed OCR was used for navigation and checked against pixels; no fresh OCR was created. The frozen written candidate TSV contains zero rows. The original editorial was absent and the frozen case/fixlog prefixes were empty.

## Content decisions

All questions and answers have item-level evidence and reasoning in [item_review.json](audit_work/item_review.json). The complete individual witnesses were compared after their omissions and differences became apparent. Their missing reference marks and shorter instructions did not replace the fuller principal structure.

Two current principal departures are recorded in [principal_differences_N2_2003.jsonl](principal_differences_N2_2003.jsonl):

- Reading 14 prints the fourth choice as number 5. The individual witnesses and the complete four-choice sequence support ordinal 4. The choice wording, order and key remain as printed.
- Grammar 52 prints `出かけたかと思おうと`, also present in the individual retypes. The explanatory grammar and sentence meaning support `出かけたかと思うと`; deleting the extra お is a medium-confidence provisional repair, with a public case.

[unresolved_cases_N2_2003.jsonl](unresolved_cases_N2_2003.jsonl) contains that provisional repair and one unresolved original-cover case. A bounded [public retype lookup](https://chuyenngoaingu.com/uploads/Ebooks/JLPT/chuyenngoaingu.com_2KYU2003.pdf) repeats the anomalous grammar-52 wording. It is unverified and may share ancestry; it supplies neither an independent vote nor authentic cover evidence. Its text was accessible, but screenshot retrieval failed. It was not admitted as a source.

Grammar 38's explanation reverses the descriptions of choices 1 and 2. The printed key is 1, the actual first choice is `もとに`, and the translation and sentence meaning support that key. The explanation defect is documented, not imported into the question. An apparent OCR-only grammar-40 key conflict was rejected by inspecting the actual tables: the answer is 1, `うかがった`.

Focused image checks establish the first glyph 責 in vocabulary 24's wrong options, and the exact underlined inflections in vocabulary 58 and 61. Deliberately wrong forms, including vocabulary 45's `すまなく`, are preserved. Principal variants such as vocabulary 55's `川の流れ`, vocabulary 56/2's `いらない`, reading passage 2's `ありがとね`, and grammar 34's `作り出された` are retained; disagreement alone is not treated as damage.

## Structure and figure

Sixteen vocabulary target groups preserve all numbered tested spans and their choice associations. Reading underlines, circled references, superscript note calls, paragraphs and citations remain content. No source-supported ruby occurs in the written exam fields; ruby confined to explanations was not imported.

The sole written figure is the phone-ownership/reading-volume graph on physical 265. [The source graph asset](assets/N2_2003-reading-q021-source-graph.png) retains all six rows, labels, black/white legend, bars and 0–100% axis. The extracted image requires a lossless 180-degree rotation to match the displayed page before cropping. The verified crop, coordinates and hashes are recorded in [graph_extraction.json](audit_work/graph_extraction.json); the embedded image matches the asset. The final two categories are not monotone, but the overall relationship supports key 2. No exact bar-end percentages are invented. Native artwork and figure review remain integration work.

Old shared/level-2 revision 6 supplies ordinary presentation. There are no local render overrides or chosen style variants. All 25 contexts have source-bound context-to-question associations and conditional keep-if-it-fits roles; retype page breaks are not forced. Original writing direction is unknown, with the level-default fallback recorded. Both covers are explicitly unavailable. The source graph precedes its question and retains the actual newspaper citation.

## Principal assessment and validation

The completed method-1 principal uncertainty index is **104**: 100 unverified provenance points and two minor fields, with no major fields, uncertain-only fields, metadata flags or missing scored/context units. The two defective fields are the reading-14 option label and the malformed grammar-52 connective. The exact historical grammar-52 repair remains provisional even though the printed defect is clear. Counts concern exam fields; the separate explanation-38 reversal is recorded above. Repeated defects within a field are counted once and the highest applicable category takes precedence.

The collection credits the exam bodies and its publisher claims permission. Its 2011 imprint and foreword do not establish issuer custody of these exact bytes. Neither appearance nor retypesetting alone establishes authenticity or known reconstruction.

Canonical content/schema, fixlog/case, principal-index and principal-difference validation pass. All 12 initial sections and two later repairs replay exactly to the current editorial, and root metadata creation replays exactly. Question, choice and key counts, 16 target groups, 25 context associations, inferred source bindings, unavailable covers, source hashes and unchanged frozen dependencies pass the available checks. The complete final text and audit note were read back after validation.

Two supplied-runtime checks remain unavailable and are explicit integration requirements:

- `model.compose` and its renderer collectors cannot import the absent frozen dependency `rubi-restore/tools/ruby_core.py`. No live helper or substitute module was added.
- Publication-identity resolution rejects the immutable approval registry's absolute `src` paths when rooted in this isolated workspace. Neither the parser nor registry was edited. The independently available admission, profile, cover and inferred-binding checks pass.

Detailed receipts are under `preprocess/audit_runs/2026-10-26_handoff25_non_uars/validation/N2_2003/`. All available required source and content checks are complete. No exam PDF was composed or accepted, and no live catalogue, other task or website was changed.
