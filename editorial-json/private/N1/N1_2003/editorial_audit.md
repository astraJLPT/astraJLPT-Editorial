# N1_2003 written audit — H25

Completed 26 October 2026 with explicit textual uncertainty and two isolated-runtime validation limitations. The maintained Old 3.9.0 editorial contains **65 vocabulary questions, 58 reading/grammar questions, 492 choices and 18 required contexts** in 13 sections. All 123 keys are established; no worked example is present in the available written witnesses. PDF integration remains `pending_after_h23`.

This is a reconstruction of the available written content. Original booklet covers and original appearance are unestablished. No timing, score or original booklet page count has been invented. The separate listening regions were excluded.

## Evidence and coverage

The principal is the indexed `1995-2009.12日本语能力测试真题详解N1.pdf` under `src/JLPT N1-N5, Past papers/N1/`, SHA-256 `e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00`. Its year and 1級 heading establish the sitting identity. The [official 2011 JLPT guide](https://www.jlpt.jp/reference/pdf/guide2011.pdf), physical page 2, states the pre-2009 annual December schedule. The month is not inferred from the owner ID.

| Source region | Completed inspection |
|---|---|
| Collection physical 289–293 | All 65 vocabulary questions, shared target sentences, instructions, four choices and tested marks. Page 293 stops after question 65, above listening. |
| Collection physical 296–305 | All 22 reading questions, nine passages/graph contexts, 36 grammar questions, instructions and choices. Page 296 starts at the reading heading below listening; page 305 question review ends above the answer tables. |
| Collection physical 305–306 | Both written key tables, aligned by question and option order. |
| Collection physical 307–310 top; 311 bottom–319 | All vocabulary and reading/grammar explanatory regions. Listening explanations on mixed pages were excluded. |
| Collection physical 1–3 | Publication title, copyright/imprint and publisher claims, for provenance assessment only. |
| Indexed 2003 question-and-answer DOC | Complete written text and keys; all 19 pages of its private LibreOffice inspection conversion reviewed after initial comparison exposed poor alignment. |
| Indexed 2003 Chinese translation PDF | Physical 9 below the reading heading, 10 and 11. This supports passage meaning, not exact Japanese spelling or original layout. |

The DOC SHA-256 is `c24b0d9d48d2865a46a9695230d5292ab00e08617a008882a19d044bb0ed6f00`; the translation PDF SHA-256 is `085c5828475790b92a103c01235607f58402f6bdb941c668bb7d04d35b1e4f4a`. All three original hashes and private mirrors match. Aliases and the principal inspection copy are the same witnesses and add no independent corroboration.

The missing-editorial preflight passed on five consecutive complete non-example vocabulary questions 16–20, including their common instruction, on collection physical 289–290. Existing indexed OCR was used for navigation and then checked against the actual page images; no new preflight OCR was created. The frozen written candidate TSV has zero rows. The initial maintained editorial was absent, and the frozen fixlog/case prefixes were empty.

## Content decisions

The DOC omits vocabulary questions 7–8, loses the question-22 graph and contains damaged words/options. These were reconstructed from the collection, including vocabulary 30, 39, 40, 46 and 47 and grammar 23, 47, 51 and 54. The complete DOC was compared across both written parts. Shared errors suggest possible common ancestry; agreement between these witnesses is not treated as independent proof.

All answer mappings have item-specific reasoning in [item_review.json](audit_work/item_review.json). For example, the graph supports the broad relationship between lower reading volume and more phone ownership even though its final two categories are not monotone. Grammar 50 requires `べくもない`, despite the collection explanation discussing the positive-purpose form. The wage passage uses 1971, as printed in its Japanese text and the separate translation; the collection's explanatory Chinese 1979 does not replace that date.

Five current principal departures are in [principal_differences_N1_2003.jsonl](principal_differences_N1_2003.jsonl). They concern the first passage's victim/offender references and particle, the single child-language note number, the youth passage's duplicated character/author/double particle, reading 1 option 3, and grammar 56 option 3. Four departures contain medium-confidence repairs and link to public provisional cases. The reading-18 stem's DOC-only underline was removed during final comparison to match the principal; its passage target remains underlined. This is an editorial transcription correction, not a principal defect.

[unresolved_cases_N1_2003.jsonl](unresolved_cases_N1_2003.jsonl) contains four provisional repairs and three unresolved cases. The latter retain the anomalous wording of reading 10/3 and 15/3 and disclose the absent original covers. The first and youth passage cases also explain the remaining wording doubts in their retained spans. Deliberately wrong vocabulary/grammar forms remain wrong options; their nonstandard spellings were not normalized into correct answers.

Focused public text lookup used the [secondary 2003 retype](https://www.scribd.com/doc/23637089/2003) only for disputed spans. It is unverified and may share ancestry with local witnesses; it was not admitted as a principal or treated as original-layout evidence. The [National Diet Library book record](https://ndlsearch.ndl.go.jp/books/R100000002-I000001893884) supports the youth passage author's surname 菅原. The underlying book page was not openly available. No contact, general acquisition hunt or access-control bypass was performed.

## Structure, marks and figure

The nine vocabulary target groups preserve every numbered tested underline and association to their choices. Questions 36–40 retain the extra underline on the tested parenthesized syllable; 56–60 distinguish the headword's double underline from sentence-target marks. Reading callouts, relevant underlines, notes, paragraphs and citations remain content. No source-supported ruby was observed in this N1 written content.

The only written figure is the six-row phone-ownership/reading-volume graph on physical 303. [The exact graph asset](assets/N1_2003-reading-q022-source-graph.png) retains the six row labels, black/white legend, bars and 0–100% axis. A lossless 180-degree rotation of the extracted image restores the displayed page orientation before cropping. The verified crop is embedded as a data URI and retained separately; its hashes and crop coordinates are in [graph_extraction.json](audit_work/graph_extraction.json). No exact bar percentages are invented. Native artwork and before/after figure review are deferred to integration. Answer tables and excluded listening images are not counted as written exam figures.

Ordinary typography and reflow inherit Old shared/level-1 revision 6. There are no `render_overrides` or selected style variants. All 18 contexts use supported context-to-question associations and a conditional keep-if-it-fits role. No retype page breaks are forced. Original writing direction is marked unknown, with the level profile supplying the supported fallback. Both covers are explicitly unavailable. The graph stays before its question with the actual source citation; no fabricated citation prefix was added to use a specialized layout role.

## Principal assessment and validation

The completed method-1 assessment is **113**: 100 unverified provenance points, one major field, two minor fields and four uncertain fields. There are no metadata flags or missing scored/context units. Repeated occurrences within a field count once, and a field's confirmed defect takes precedence over its additional uncertainty. The missing original covers are disclosed but are not invented missing scored blocks.

The publisher credits the exam bodies and claims authorization. This does not tie the exact acquired bytes to issuer custody. Neither scan appearance nor retypesetting alone determines authentication or known-reconstruction status. The [principal copy](principal/1995-2009.12日本语能力测试真题详解N1.pdf) is byte-identical and retains the original filename.

The canonical content/schema validator, case/fixlog checks, principal-index validator and principal-difference validator pass without warnings. Exact replay of all section creation and subsequent item edits equals the final editorial. Root metadata creation and binding-refresh history also replay exactly. Source hashes, original/mirror equality, the preserved frozen log prefix, question/option/key counts, nine target groups, 18 context associations, supported cover absence, profile references and source-bound inferred regions pass the available checks. Pinned schemas, defaults and validator dependencies remain unchanged.

Two checks remain unavailable in the supplied isolated runtime and are explicitly recorded as integration requirements:

- `model.compose` and renderer collectors importing it cannot load because `rubi-restore/tools/ruby_core.py` is absent from the frozen `WORKING_INPUTS.json`. No live helper was copied and no substitute module was injected.
- Publication-identity resolution calls a registry parser that rejects the immutable registry's absolute `src` links when rooted in this mirror. The registry and parser were preserved. Admission/profile/cover checks and inferred source-binding APIs run independently and pass.

The detailed receipts are under `preprocess/audit_runs/2026-10-26_handoff25_non_uars/validation/N1_2003/`. Their pass claims apply to the named available checks, not the unavailable renderer checks. All required available source/content investigation is finished. No exam PDF was composed, released or visually accepted; no live catalogue, other task or website was changed.
