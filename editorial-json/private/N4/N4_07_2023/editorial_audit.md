# N4 July 2023 editorial audit

Status: audited_with_uncertainty.

## Start (2026-09-26)

Confirmed live state after N3 July 2023 closure/reporting. Preserved byte baselines of editorial JSON, root fixlog and public cases before editing. Read the complete current index and baseline structure. No principal selected yet. Listening and generic scoring/answer templates are excluded from written reconstruction.

## Checkpoint: complete principal candidate and historical leads

The preserved baseline SHA-256 is 177fed87a9634fac87ec5c997e40af917dee37d8a88831a118c579cdb60d3c39. All nine indexed source identities and fifteen primary/alias paths hash correctly. The baseline contains 28 vocabulary and 29 grammar/reading questions (228 options), seven blocks and eleven section headings.

Read all 64 written candidate rows (R001–R050, V001–V014) and all 26 local historical records. No listening candidate rows were loaded. Routine spacing/parser diagnostics are reviewed; the consequential leads are V6 choice1, V17 stray kana, V20 walking/exercise spelling, V21 dakuten, V24 duplicated printed choice label, the worked ★ example and the notice contact name. Earlier claims that a PDF already printed some corrected readings are not accepted: actual originals visibly preserve several errors.

The complete candidate principal, pdf_6 (52e4cce69aa7c1cf4fa45cd8296a7ac1b0574217b62bd8d86120726e66b76591), has been visually reviewed on every physical written page 1–14. Listening pages 15–23 are excluded. All stems, 228 options, seven blocks, eleven headings, underlines, ★ slots, names, dates, fares and reservation cells were checked. No furigana is printed on these written pages. Its native text was compared with the other full 23-page edition (pdf_2) over written pages 1–14; most differences are text-layer ordering/font omissions. The raster pdf_3 has only pages 1–12 and stops after reading27, lacking the final two questions and travel notice; its complete available written review is ongoing.

Read all written native explanations/keys on physical pages 1–3 of both pdf_1 and pdf_4. They agree on all 57 answer numbers and the four ★ orders 3241, 4312, 3421, 4231. They also share the nonliteral paraphrase 海には for cloze20, whereas the actual second option is にも; therefore they are not independent verbatim witnesses. Visual confirmation of their tables/line associations remains in progress. Yuuki pdf_2 p14 directly prints Yuuki旅行 with phone 081-666-7711; pdf_6 prints ABC旅行 with the same phone. The personalized agency variant requires disclosure even though ABC remains preferable.

No root editorial/log/cases edits yet. Next: finish raster/answer page review, compare immutable archived HTML, enlarge malformed distractors and decide repairs, then prepare/validate an auditable proposal.

## Reviewed result

Selected principal: `src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N4真题/2023年7月/2023年7月日语N4真题.pdf`, SHA-256 `52e4cce69aa7c1cf4fa45cd8296a7ac1b0574217b62bd8d86120726e66b76591`, physical written pages1–14. It is complete and legible and retains the generic ABC contact. No source was selected merely for tier, scan appearance or agreement. The twelve-page raster copy is incomplete; the other complete edition personalizes the agency. The selected file has no authenticated acquisition chain; conspicuous local errors and digital typesetting alone do not establish a recollection-based reconstruction.

### Evidence actually inspected

- Principal pdf_6: all14 written pages viewed in full; native text read across all14; enlarged original regions for vocabulary6/20 and cloze passage ending. The full native comparison with pdf_2 is retained privately. No listening pages15–23 audited.
- Raster pdf_3 (9412cfb…): all12 physical pages viewed, including every available stem/option/passage and enlarged vocabulary20/cloze crops. It has vocabulary1–28, grammar/reading1–27 and six blocks, then ends; it supplies no notice or questions28–29. Its page bodies/layout and conspicuous errors follow the complete source family, so it is not treated as an independent vote.
- Yuuki pdf_2 (244132b…): written native text compared on1–14; original pages2,3,8,9,10,14 viewed. The differently typeset p8 shows all four separated ★ slots especially clearly. Its agency is visibly Yuuki旅行, matching its publisher watermark; phone and every fare/date cell match the principal. It preserves the same major spelling errors. No full visual review of unlisted pages is claimed.
- Yuuki pdf_1 (ac3c111…): all written text on physical1–3 read and visually checked. Page3 also contains a listening-key graphic; that portion is excluded. Companion pdf_4 (9bd8eca…): written pages1–3 read and viewed; listening4–12 excluded. All57 written keys and four ★ orders agree. Identical short explanations, including 海には where actual cloze20 choice2 is にも, show that these are related answer witnesses and not literal reconstructions of all distractors.
- Immutable archived vocabulary/reading HTML: all57 question strings,228 choices,11 headings and six available blocks aligned against the baseline. Ten normalized differing fields are recorded in `archive_alignment.json`: four vocabulary inherited repairs, four equivalent ★ line representations, the doubled が repair and the added notice footer. The archive lacks the whole worked example. It preserves the malformed first distractor and other shared source errors, so it cannot independently certify them. No working HTML was read or modified.
- `rg --files` targeted July2023/N4 source discovery found only the indexed versions/aliases and the irrelevant archived listening page. The generic N4 answer card and archived DEAD listening page were excluded; all indexed primary/alias hashes were still verified. No new unit-specific independent source was found locally.

### Complete written coverage and decisions

Principal pages1–5 cover five vocabulary sections with counts7/5/8/4/4. Every stem target and all112 options were reviewed. Ordinary reading/kanji wrong choices are preserved, including あしりません, だりません, とあい, 侍って, 公湯 and 径検. No furigana is printed. Vocabulary17’s strayす,20’s さんぼ and21’s よこれ are clear task-stem corruptions whose prior repairs are retained. Vocabulary24’s fourth printed label repeats3; array position4 is retained with no reordering. Vocabulary21–28 supply32 missing option sentence stops. Usage headwords25–28 are plain in print, so their imported underlines are removed while every usage-option underline stays. The three missing instruction underline placeholders are restored.

The complete reading/grammar coverage is principal6–14:13 grammar items (6–7), worked example and four ★ items (8), cloze passage/four items (9), shop memo and baby-newspaper passages/items (10), speech email/item and start of violin passage (11), violin continuation/three items (12), two notice questions/memo (13), full travel notice (14). All116 options, seven blocks and six instructions were reviewed. Dialogue outside-stop errors in3/4/12/13 are removed. Printed terminal stops are restored on all choices22/23/26. The reference in25 ends at 引っ越しました, excludingか. The example now preserves four underlined solved fragments3–2–4–1, starred third fragment4, and answer-sheet choice4. The star instruction underline is restored. Scored orders3241/4312/3421/4231 and keys4/1/2/3 agree with both explanation versions, including the wrapped17 layout.

The full cloze byline ダワドルジ ホラン is preserved; its separating space is meaningful. The source’s すきでず was checked in enlarged originals of all three question copies and is recorded as an inherited ordinary repair to すきです. Keys3/1/2/4 fit past motivation, causal continuation, additive destinationにも, and planned future showing. The explanations’ には is not substituted for the actual printed optionにも. In the shop memo, the inherited deletion of repeatedが is retained. In the speech email, 中西/前川/高木/リム and the question’s distinct orthography 挨拶 are source-supported; the request is whether the student wants supervised practice, key3.

Unchanged anomalies were tested in context. Grammar12 choice2 帰られないといけません is a deliberate wrong construction, not something to normalize into a correct alternative. Grammar17’s 学校に木村さんは has marked but possible topic placement and is unchanged. The violin passage’s 思われたからです is printed consistently: it can refer to an earlier occasion when playing loudly disturbed neighbors, explaining present inability to play in the apartment. There is no independent contrary wording; do not rewrite the tense for fluency. Questions25/26/27 remain2/4/1 by distant workplace, the man’s guitar practice and freedom to play without bothering anyone. Legitimate inappropriate usage distractors in vocabulary25–28 remain untouched apart from printed punctuation.

The memo in29 is represented with three explicit name/date rows. Source absence of a stop after the last date is restored. The notice now separates its introduction, route lines, fare notes and reservation heading into paragraphs around the two existing semantic tables. All stations, times, prices, age categories, eight dates/statuses and phone digits are unchanged. High-school student from 今中駅 pays10000円 (28 key3); common free dates are12/19 and12 is unavailable, leaving19 (29 key4). Decorative fish illustration conveys no task information and is excluded as furniture. No meaningful diagram is lost. Numeric grouping commas, width variants and equivalent underline linework are harmless representation, not source departures.

### Historical lead dispositions

All64 written candidates and26 historical records were read without relying on their former confidence labels.

- R001–R020: retain ordinary within-word spacing repairs after reading complete contexts; the R008 doubledが repair is correct even though old notes incorrectly claimed the PDF already had oneが. R018’s past 思われた is left intact for the contextual reason above.
- R021: によると is legitimate largeよ, not a small-kana error.
- R022–R043: parser diagnostics concern historical HTML handling, not exam text; no corresponding invented editorial fixes.
- R044–R045: generic assessment rows supply no item-level correction.
- R046: ダワドルジ ホラン name-component separator retained. R047: the gap in reading28 lies between clauses and is not a corrupted word.
- R048: the earlier full worked-example recovery is verified and retained; layout and underlines now restored. Earlier intelligible こうなります remains an ordinary departure from printedこうなりです.
- R049–R050: the recovered ABC footer is source-supported, but the Yuuki variant remains a public historical-name uncertainty; phone is directly verified in both full copies.
- V001: retain ききました but downgrade the historical assertion from the old confident decision to an unresolved public case; all original first choices actually readききまいた.
- V002–V004: retain clear stem repairs人が少ない,さんぽ,よごれ; enlarged pages verify the corrupt source forms. V005–V010 are parser diagnostics; V011–V012 generic praise. V013 is harmless post-comma spacing. V014 is the duplicated printed option label, preserved in principal differences while correct array identity4 remains.
- History sequences1268–1291 and8632–8633: all26 inspected, retain the reviewed spacing/stem/example/footer changes with the revised confidence qualifications above. Historical bytes are not rewritten.

### Remaining uncertainty and exact changes

Three self-contained public cases record: new provisional うんどん→うんどう (medium), retained ききました versus printedききまいた, and ABC versus personalizedYuuki agency. The two distractors were checked in all question versions, enlarged where needed, the immutable archive and both explanations; their strongest intentional-wrong-form alternatives were considered. The exercise noun is preferred because this section selects lexical meaning in context, while せわ uniquely covers both feeding and walking. The reading distractor is more vulnerable to intentional nonword design and stays explicitly uncertain. The two answer keys do not settle exact distractor wording. ABC is preferred over the distributor’s own name without claiming historical authentication.

The private proposal has61 field edits:60 high,1 medium, including44 terminal option stops. No key, order, count, stable ID or import metadata changes. Nine principal departures include inherited differences, not merely this run’s edits; the agency case agrees with the principal and therefore has no departure row. The proposed final SHA-256 is `e5c4e91f8293d329499b5a070cc84c76fdc5a59af328c1e8b29b2f801dbd9b76`. Method1 assessment is120 =100 unverified +5 for one major field +12 for six minor fields +3 uncertain fields. Import-only omissions and purely representational changes add no points.

## Installed validation

The installed JSON passes with28 vocabulary and29 grammar/reading questions,228 options,seven blocks and eleven headings. All61 edits replay exactly; historical ledger bytes remain a prefix, stable IDs/import metadata and all57 keys are preserved. The12 option-change warnings correspond to44 source-supported terminal stops and the one provisional exercise spelling; no options moved. Four star orders, worked example, memo dates, both notice tables, reference underlines and source-supported absence of ruby were checked. All15 indexed paths were rehashed. Public values and principal links pass.

## Separate reporting and queue closure

After recording the unit result, the actual principal was catalogued with method1 score120: unverified100 plus1 major,6 minor and3 uncertain fields; no metadata flags or missing units. The24-entry catalogue and9 departures pass both required CLI validators. Three bounded ancestry observations were appended. State advances to N5_07_2023, the inclusive endpoint.


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 14 maintained fields / 58 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N4_07_2023-DW20261013-001 through N4_07_2023-DW20261013-014 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.


## Housekeeping 2 — 5 November 2026

N4_07_2023-HK1-INST-vocab-s01: For N4 vocabulary the 2012 workbook and later genuine test print the entire reading-choice formula in kana. Keep ひらがな explicitly; the separate writing task omits it. The principal uses 書, 一番, 一つ and 選, a pattern its vocabulary booklet repeats.

N4_07_2023-HK1-INST-vocab-s02: Three genuine pages preserve the shorter question for writing rather than reading. Keep the existing kana instruction without inserting ひらがな from the preceding vocabulary task; the selected reconstruction uses a kanji-heavy selection formula.

N4_07_2023-HK1-INST-vocab-s03: The N4 workbook and two calendar originals distinguish vocabulary なにをいれますか from grammar 何を入れますか. Preserve that distinction even though this reconstruction prints kanji in both tasks; the key remains a vocabulary choice.

N4_07_2023-HK1-INST-vocab-s04: Workbook and December 2024 same-task headings write the complete description in kana, including ぶん and いみ. The selected copy converts those words to kanji in its reconstructed heading. Retain the reviewed passage-matching instruction.

N4_07_2023-HK1-INST-vocab-s05: Both genuine N4 editions say つかいかたで for this precise sentence-usage task, while the selected copy uses the more formal 使い方として最もよいのを. Earlier housekeeping changed only part of that construction. Complete the localized correction to the attested N4 formula; preserve its target and examples.

N4_07_2023-HK1-INST-reading-s01: The selected and partial copies already support kanji 何 and 入 in grammar, and the workbook and genuine 2024 grammar page match the current polite instruction. Its use of 一つ contrasts with vocabulary ひとつ and should remain.

N4_07_2023-HK1-INST-reading-s02: The 2012 workbook and December 2024 calendar booklet agree word for word on the question for this N4 STAR task. The selected/partial editions share an N3-like substitute; the first housekeeping change retained part of that construction and omitted the actual question. Restore the common N4 formula, keeping the underlined ★, the worked answer geometry and all choices intact.

N4_07_2023-HK1-INST-reading-s03: The selected copy wraps いちばん between lines; the partial copy, the 2012 workbook with 21–25 and the 2024 booklet with 18–21 confirm that it is one word. Join only that word, and keep the range, the cloze selectors and the four answers unchanged.

N4_07_2023-HK1-INST-reading-s04: The 2024 N4 genuine heading matches the three local texts as well as the command 答えてください. The workbook has the same command but four passages. The principal’s 選 rather than えら is a reconstruction-specific difference; retain the case-specific range.

N4_07_2023-HK1-INST-reading-s05: Across the workbook and two contemporary genuine N4 booklets the repeated command is for いちばんいいもの. The principal’s physical line break splits the two い in this adjective. Retain the single-passage instruction but join that word in the current reflowable text.

N4_07_2023-HK1-INST-reading-s06: Genuine N4 lookup tasks confirm the instruction and polite selection request, but their notices concern other classes or a factory tour. Retain the local travel-company description and right-hand relationship from the principal; do not substitute an unrelated notice.

Index 120 retained. The two internal line wraps and earlier partial template normalization affect the editorial; they do not create additional principal content defects. No changes to questions or gradability. 4 editorial fields changed. 1 public and 4 principal snapshots rebound to pre-existing field changes; not substantive reviews.

[Before/after decisions and receipts](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N4_07_2023/disposition.json).

Native generation rejected the old presentation boundaries. Reauthored and checked three heading records; previous stage and rejection retained.
