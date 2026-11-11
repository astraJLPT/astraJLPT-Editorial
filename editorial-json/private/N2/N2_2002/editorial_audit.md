# N2_2002 written audit — H25

The available written audit is complete with explicit uncertainty. The Old 3.9.0 editorial contains **122 scored questions (65 vocabulary, 57 reading/grammar), 488 choices, 25 contexts and 12 sections**. Every written key was checked against the tables and the question meaning. No worked example or known missing scored question was identified. PDF integration is `pending_after_h23`.

## Sources and completed scope

The principal is `src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/1991年-2009年/1995-2009.pdf`, SHA-256 `115e8c098ee3caed702d29a24d2ce0c883c3ad9152e21eee4200fc4e80f2a3fb`. Its written headings establish 2002 and 2級. The [official 2011 JLPT guide](https://www.jlpt.jp/reference/pdf/guide2011.pdf), physical page 2, establishes the annual December schedule through 2008; the month is not inferred solely from the owner ID.

The full written regions reviewed visually were principal physical 287–290 above listening for vocabulary; 292 below the reading heading through 302 for reading/grammar; written keys 302–303; vocabulary explanations 303–305; and reading/grammar explanations 307 below their heading through 314 above the listening script. Exact-file collection front matter 1–3 was already inspected during N2_2003. Both individual PDFs were compared throughout written pages 1–5 above listening, 23 below the reading heading through 35, vocabulary keys on 36 and reading/grammar keys on 37. No listening-region content was audited.

The Tier 1 individual PDF is `src/JLPT N1-N5, Past papers/N2/2002年/2002年日语能力考试2级真题及答案.pdf`, hash `95cf791403933e238c5a67cf3ddd6e97282acda9fa50dd49e9331569b08314a0`. The Tier 2 individual under 渠道一/日语N2真题/1991年-2009年/2002年 has hash `4673069d6a6da12a7cb3913484469fff9a30af1a64defe71c0981f681678d5ff`. They share retype layout and variants but are not byte-identical or independent witnesses. The actual Tier 2 first page has a garbled visible overlay; embedded-image similarity does not establish equivalence of visible PDF content. Its remaining inspected written pages are legible.

The indexed listening DOC, hash `a1ffa14bc7bc11963536130da8ac2089cc2fa27fb9c9504f48fa4343cf1f47e4`, was privately converted to 11 pages and classified from headings and tail boundaries as listening scripts and listening keys only. This was not a full content review. The indexed 1991-path HTML readme, hash `55b7975790d20d4e992a1cf3249bd5d03bc1e3a712beee76ec14f305fb39755c`, is generic promotional text without exam material; its links were not followed. Original sources, exact private mirrors and the principal copy retain their hashes and filename.

The missing-editorial preflight verified five consecutive complete non-example questions 1–5 on individual page 1, including instructions, tested words and all choices. One further spot check sufficed. Existing indexed OCR served as navigation and was checked against pixels; no fresh OCR was produced. The frozen candidate TSV has no rows. The baseline editorial was absent and both ledger/case prefixes were empty.

## Decisions and uncertainty

[item_review.json](audit_work/item_review.json) records item evidence and answer reasoning. The principal supplies complete instructions, A社, continuous question labels and all reading/grammar content. Full comparator review exposed omitted opening clauses in the baby passage, duplicated freeter text, a misplaced mathematics reference, missing grammar 37, incomplete grammar 54 and different grammar 36/51 options. These related omissions did not replace complete principal text.

Five changed fields appear in [principal_differences_N2_2002.jsonl](principal_differences_N2_2002.jsonl):

- Vocabulary section IV endpoint 52 becomes 55, and section V endpoint 57 becomes 60, matching the actual five-question groups and keys.
- Reading section II's final passage number becomes (3), matching its three complete passages.
- Reading passage 9 receives three minimal repairs in its single content field: `述べたものをである` → `述べたものである`, `約2200人「` → `約2200人に「`, and `38.8%倍以上` → `38.8%と倍以上`. Native principal image 1180 confirms the defects; both individual page-30 passages supply the grammatical wording. All percentages and the key remain unchanged.
- Reading 10's third choice changes `顔の方が好む` to `顔の方を好む`. 赤ん坊 is the subject of 好む, and the preferred face is its object. Both individual retypes repeat が; the exact historical wording remains unverified, so this is a medium-confidence provisional repair. The claim of a preference between vowels remains a false distractor, with key 4 unchanged.

[unresolved_cases_N2_2002.jsonl](unresolved_cases_N2_2002.jsonl) contains the provisional particle repair and two unresolved cases: the proverb passage citation and original written covers. The principal attribution is 沖ななも「伝える言葉・感じる言葉」『出版ダイジェスト』1999年11月20日号 出版ダイジェスト社. Both individual page-28 retypes instead give 「言葉の時代性」 and 2001年11月20日号. Focused title/date searches recovered no authoritative original issue. A related [18-page jlpt.info print retype](https://chuyenngoaingu.com/uploads/Ebooks/JLPT/chuyenngoaingu.com_2KYU2002.pdf), physical 13 extracted text, repeats the latter citation; a [Scribd copy](https://www.scribd.com/document/932168302/2002-2kyuu-N) repeats that same retype. They do not establish independent authority. PDF screenshot retrieval failed, so no external pixel review is claimed. The legible principal attribution is retained with its public uncertainty.

The external first-page template's timing, score and notes do not authenticate an original cover. Both covers remain unavailable. The individual key tables supply per-question weights: vocabulary 1–40 at 1 and 41–65 at 2 (sum 90); reading 1–21 at 5 and 22–57 at 2 (sum 177). Their printed reading total 172 is arithmetically inconsistent. Per-question weights are preserved as secondary evidence, while neither 172 nor any original cover score, timing or page count is adopted.

Principal variants retained include しにょう, 18歳未満, 住所ですか, 最も, 田中, the complete baby opening, the mathematics reference on これ, 解けなかった and the expanded proverb passage. Wrong orthographic alternatives and grammar distractors retain their actual glyphs, including vocab 30's 彼害/波害/破害/被害, vocab 33's 済ったら/終ったら/補ったら/整ったら, grammar 33's かは and grammar 45 option 2's 恥かしいはずがなかった. Disagreement or awkward distractors alone do not justify normalization.

Grammar 32's explanation incorrectly treats causal につき as equivalent to topical について; the actual office-closure sentence supports key 3. Reading 9's explanation overstates that しかも cannot be additive; the passage requires summarizing このように, key 4. These explanation defects are recorded without importing them into exam content. No answer key changed.

## Structure, figures and defaults

All 16 vocabulary target contexts and nine reading contexts are complete. The editorial retains tested underlines and inflections, boxed/circled references, paragraphs, eight citations, 39 lexical notes and 40 note-call occurrences (the letter's note 2 appears twice). The short 急がば回れ passage has no observed attribution or notes in the available witnesses; none was invented. Ordinary question ruby was not inferred from explanation text.

Reading 21 contains four source graph options. [graph_extractions.json](audit_work/graph_extractions.json) records principal physical 299, image xref 1184, lossless 180-degree rotation, exact crops and hashes. All four upright native crops were viewed. They retain four sex/time rows, 0–100% axes, ticks, borders and hatched/black/dotted 定年派/転職派/その他 legend. Ruby on 就職, 定年派 and 転職派 remains in source pixels. A native close-up resolved a suspected legend glyph as 派; no legend repair was needed. Choice 4 matches all eight passage percentages; incorrect graph arrangements remain exact, without invented bar-end values. Each embedded image matches its separate PNG asset. Later native artwork, if required, and final source-versus-output image comparison remain explicit integration requirements.

Old shared/level-2 revision 6 supplies ordinary presentation. No local render override or style variant is added. All 25 contexts have exact content/question digest bindings, source page/region evidence and conditional keep-together roles. Original writing direction and pagination remain unknown, with level-default fallback recorded. Retyped page breaks are not forced.

## Principal assessment and validation

The completed method-1 principal uncertainty index is **111**: 100 unverified provenance points, five minor fields worth 10 points and one uncertain citation field worth 1. There are no missing scored/context units, major fields or metadata flags. The three passage-9 typos count once in that content field. The clear grammar defect in reading 10 counts as minor while its exact repair remains provisional. Cover unavailability does not create an additional content unit. Supplementary explanation mistakes and comparator-only omissions are separately reported above.

The collection's China Aerospace Press 2011 imprint, exam-body credits and authorization claim do not authenticate issuer custody of these exact bytes. Retypesetting alone does not establish known recollection reconstruction.

Canonical content/schema, public cases, fixlog, principal index and current principal differences pass. The 188 exact ledger rows (36 section metadata fields, 147 question/context creations and five repairs) replay to the current editorial; root metadata creation also replays exactly. Counts, tested-target associations, context bindings, four embedded asset hashes, source identities and unchanged frozen dependencies pass available checks. The complete assembled text was read back after validation, including all questions, choices, keys and contexts.

Two pinned-runtime checks remain unavailable: model composition and renderer collectors lack the frozen dependency `rubi-restore/tools/ruby_core.py`; publication identity rejects the immutable registry's absolute live-source paths under the isolated root. No live helper, replacement module or parser/registry change was introduced. Available admission/profile/style/inferred-source checks pass. The limitations are common integration requirements, not claimed passes. Receipts are under `preprocess/audit_runs/2026-10-26_handoff25_non_uars/validation/N2_2002/`.

All available required written source/content checks are complete. Listening/audio, exam-PDF composition/rendering and publication remain deferred. Live files, other handoffs and originals were preserved.
