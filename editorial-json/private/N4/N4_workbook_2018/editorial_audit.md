# N4_07_2018 written-content audit

Completed 5 October 2026 in run `2026-10-05_N1_07_2018_to_N5_07_2017`.

Disposition: **workbook; complete written workbook coverage**. The content is *Japanese-Language Proficiency Test Official Practice Workbook Vol.2 — N4* (2018). The July 2018 sitting remains **unrecovered**, separately recorded in the public unit gap. Stable unit/item IDs, import metadata, source files and both indexes were preserved.

## Identity and evidence

The selected principal is the 24-page compact secondary reprint `2018年N4真题+答案+解析+听力原文.pdf`, indexed as `pdf_1670` in `N4_official_2018`. Canonical path: `src/日语JLPT历年真题/N4真题（2010-2025.12）/2018年N4/2018年N4真题+答案+解析+听力原文.pdf`. SHA-256: `74537e9825e5b1972c643e3dbf354d90e3563e01d093a0047146e438f7494fce`. Its complete written content, physical pages **3–10**, was visually read, including unchanged questions, all choices, seven contexts, instructions, underlines and missing examples. Metadata pages1–2 were also inspected. A byte-identical inspection copy retains the original filename in `principal/`.

The distinct 13-page `2018年07月日语N4真题试卷.pdf` (`pdf_1671`, SHA-256 `826bbe68cbac3cb80cbd24377e369bac51f58488accc1332d61895a21e4c7d6e`) was visually compared through all written pages3–9 and written key p13. It is less complete: its lost-property date is2006, its question omits3, and it shortens factory-tour times and other context. Its July title does not establish a sitting. The other canonical copies1668/1669/1673 share eight identical embedded written-page raster streams; focused discriminating pages were inspected, with the exact scope in [page review](audit_work/page_and_field_review.json). Principal1670 is a visually matching recompressed copy, not an identical-image hash match. No independent acquisition is claimed.

The [official JLPT sample index](https://www.jlpt.jp/samples/sampleindex.html) identifies the publication as the2018 workbook. All70 questions were compared against the issuer-hosted [vocabulary PDF](https://www.jlpt.jp/samples/sample2018/pdf/N4V.pdf), [grammar PDF](https://www.jlpt.jp/samples/sample2018/pdf/N4G.pdf), and [reading PDF](https://www.jlpt.jp/samples/sample2018/pdf/N4R.pdf). Their fully inspected written ranges are V3–11, G3–9, R1–8; the V/G covers were also checked. Fresh downloads matched the earlier cached PDFs byte for byte. Hashes and acquisition records are in [official manifest](audit_work/official_download_manifest.json). All70 written keys were checked on the [official answer sheet](https://www.jlpt.jp/samples/sample2018/pdf/N4answer.pdf), p1 and the written portion at the top of p2. Listening was excluded.

The current unit's native munja written sections0–10 were fully reviewed, including all70 question fields and six textual passages/explanations. Native keys exactly matched the baseline's secondary-reprint order; this was not treated as authority for the workbook order. Native image-only notice content was recovered directly from the full principal/official table. The own-index blank answer card and additional answer-analysis companion were not used to establish question text. No claim of review is made for their unseen contents.

## Coverage and decisions

Final output: **70 scored questions, 280 scored choices, 7 contexts, 7 worked examples, 11 sections**. The historical `vocab` part contains35 vocabulary plus25 grammar/cloze questions; `reading` contains10. Printed visible labels are V1–35, grammar1–25 and reading26–35. New examples use unused block IDs `vocab-b101`–`vocab-b107`; all existing IDs and relative scored-question order remain intact.

The audit restores the official instructions, seven complete examples and answer-sheet demonstrations, exact selective ruby, full inflected underlines, punctuation, the spring schedule as meaningful HTML, and the official choice order. STAR16 has its star in the **second** slot, so order4-1-3-2 selects1 `できた`; the compact reprint's third-slot star selects3. The official answer sheet confirms the restoration. The reprint also prints an extra comma after its fourth slot; an enlarged crop corrected an initial private misreading before commitment. The original intentional wrong choices, including 誠会/誠合, remain unchanged.

Option permutations from the old order into the official order were checked explicitly:

| Stable item | Final choices drawn from old positions | Final key |
|---|---|---|
| vocab-q056 |4,2,1,3|3|
| vocab-q057 |2,1,4,3|1|
| vocab-q058 |1,3,2,4|4|
| vocab-q059 |1,4,2,3|2|
| vocab-q060 |2,3,1,4|3|
| reading-q001 |3,4,1,2|4|
| reading-q002 |3,4,2,1; restore 高い in final choice4|2|
| reading-q003 |4,3,2,1|3|
| reading-q004 |2,4,3,1|4|
| reading-q005 |3,2,4,1|3|
| reading-q006 |2,4,3,1|1|
| reading-q007 |1,2,4,3|2|
| reading-q008 |3,2,1,4|3|

The remaining option edits restore printed ruby or underline endpoints without reordering; reading-q010 restores circled schedule references. All answers were independently checked by Japanese syntax, vocabulary, passage logic or schedule constraints; see [70-item answer review](audit_work/answer_logic_review.json). Explanations were synchronized with changed key positions, restored dates/times/pool content, the actual katakana names, and the time-required meaning of のに. Selective readings were checked at each occurrence: official R5 leaves 次, its second 大丈夫 and passage 礼 unannotated; the R8 schedule annotates 市民体育 but not 館. No generic learner readings were added.

All **469** current-unit written candidates were loaded after excluding listening and reviewed, including17 accepted and452 rejected historical rows. The17 inherited repairs remain supported, while official order/annotations were independently restored. Routine spacing/layout proposals and malformed-pattern false positives were rejected after contextual review, not by their old status. [Candidate dispositions](audit_work/candidate_dispositions.json) cover every row. All18 existing written fixlog records were reviewed; their bytes remain unchanged as the prefix of the root ledger.

## Public records and source assessment

[Unresolved cases](unresolved_cases_N4_07_2018.jsonl): one unresolved unit-level historical-sitting gap, no provisional textual fixes. No written workbook content remains missing. This terminal workbook result does not fill the missing July2018 exam.

[Principal differences](principal_differences_N4_07_2018.jsonl): **74** current departures, including inherited stops and underlining, exact ruby, missing examples, restored wording, star position, order and schedule references. Compared with the exact selected principal, not merely with the baseline. Harmless spacing/reflow, equivalent glyph width/linework, distributor furniture, decorative flowers, import metadata and separate editorial explanations are excluded. No missing task or reading aid is hidden by those exclusions. The principal does not print inline keys; separately supplied keys are not counted as printed-content departures.

Method2 catalogue assessment: **known reconstruction,299**. Positive recomposition evidence is the compressed replacement typography/pagination, lost examples/ruby and altered STAR/option settings. The source is not authenticated merely because it derives from an official workbook. Components:1 timing-metadata group,7 missing worked examples,3 major fields,60 minor fields,0 uncertain fields. Arithmetic: `200 + min(99, 2 + 70 + 15 + 120) = 299`. The uncapped concern sum is207. Every event has its own item/field/page evidence. Pure option permutations in vocab-q056/q057/reading-q003 and equivalent circle rendering in reading-q010 add no defect points by themselves. The unrecovered sitting is not a workbook defect. See [assessment](audit_work/principal_assessment.json).

Four bounded ancestry observations were appended for the inspected source relationships. They do not establish issuer custody or independent corroboration.

## Validation and preservation

Baseline SHA-256: `feacc45ccdfd63b81f0666f5ea4043e4945649ddfa47795aee52aac7d23dd374`.
Final SHA-256: `1b55231897e215f409d51c25c762723c9d8af92b271ffb842b5f703b613ca2e4`.
Unit-index SHA-256 unchanged: `b9f106273794a981580fa97cbf4f9437248c16371d7947e1447ca0cb821e8fff`.
Canonical-index SHA-256 unchanged: `eb14ec8fe9a2a850b85d5324edc71fb534528b5bcc2fc4870c0c55a14b0dde0b`.

The root append-only ledger contains123 content edits and4 final section snapshots. These snapshots make the whole `/items` values reflect separately logged child explanation changes; they make no further content edits. Full replay of all127 appended records reproduces the entire final JSON, including inserted examples. Prior ledger prefix19,736bytes, SHA-256 `202eea48f5c8cb32c666ce6009d9ca408f23317e3079af0d622dd8322921824a`, remains intact. [Replay](audit_work/ledger_replay.json) and [commit summary](audit_work/commit_summary.json) preserve the checks.

All three required validators pass: editorial/cases/fixlog with baseline and expected counts60+10; principal differences74; principal catalogue65 entries. Editorial warnings concern the seven evidenced examples, changed list membership, option/key mappings and image-to-table block type; each is explained above. Initial validation caught stale whole-section ledger snapshots and a non-schema public evidence field. Append-only checkpoints and moving citations into permitted rationale fields resolved those record issues without altering the final editorial content. [Validation](audit_work/validation.json) retains both the failure explanation and final results. No validator or source tool was modified.

No content preflight was needed because editorial JSON existed. No source/index mutation, website rebuild, publication or housekeeping2 was performed. This unit's investigation is complete; continue with N5_07_2018.

## Official-workbook cleanup — 9 October 2026

The maintained owner remains N4_07_2018 for the 2018 N4 publication. Its complete pre-merge editorial, ledger prefix, public records and former principal assessment are frozen in audit_work/source_cleanup_20261009/before/ and previous_principal_entry.json. The contributing N4_12_2018 audit remains historical; its alias registration and local build integration are separate pending run steps.

The principal is now the actual issuer V/G/R source set, represented by principal_source_set_N4_07_2018.json and issuer_mapping_N4_07_2018.json. Exact member hashes, physical pages, printed-label mappings and separate key evidence are recorded there. Catalogue-linked issuer provenance authenticates the publication only, never July or December 2018. Method 2 remains unchanged: authenticated_workbook with zero recorded source concerns, score 0. All pages proposed for registry acceptance remain pending the user's review.

All 24 selected written question pages (V3–11, G3–9, R1–8) were freshly inspected in source pixels against all final printed fields: 70 scored questions, seven examples, seven contexts and eleven headings. All 70 keys were compared with the separate key's written regions on pages 1 and 2; listening was excluded. Source-cover/blank pages and decorative page furniture are outside the selected content scope. This comparison includes inherited unchanged fields, ruby, underline endpoints, punctuation, STAR slots, examples, required context/table ordering and all choices.

The pair's 220 mapped content-field differences were adjudicated in dedupe_field_adjudication.json. Eleven ordinary edits correct two 誡 distractors (not 誠), the comma in vocabulary Q25, 待 ruby, five STAR-slot underlines, the unsolved example underline, and three reading-context ruby occurrences plus below-underline reference placement. The owner's stable IDs, 70 one-point questions (35 vocabulary, 25 grammar, 10 reading), keys, category behavior and full editorial explanations are preserved. Five conflicting-looking STAR explanation variants were checked for identical intended sequences; the prior owner's full explanations remain editorial material, not issuer print.

The current principal difference register has zero rows after reconciliation, supported by the live-hash-bound 95-target mapping. All 74 former-principal departures remain preserved in the baseline and are explicitly retired against the changed principal in principal_difference_crosswalk.json; they were not rebound to the issuer or silently merged with alias records. The separate historical sitting-gap case remains open and unchanged. Source agreement does not close it.

Validation: the staged editorial/case/fixlog checks pass. Exact forward replay from the frozen baseline verifies 11 semantic edits plus four no-change section snapshot checkpoints under the established ledger convention. The options-change warning was adjudicated visually: only the two printed deliberate glyph distractors change, with all positions and key 4 retained. Regression checks exercise old single-file principals, real-member hashes/pages, complete source-set coverage, separate keys, stale bindings and reference registers. The current builder's source bundler was exercised against the actual staged set in an isolated layout. Full local rebuild and browser inspection remain pending in the run checkpoint.

### Source-cleanup closure — 9 October 2026

The scoped cleanup is complete. Exact baseline-to-current ledger replay, canonical/case/principal/reference validation, source/index preservation, final product build, review links and browser checks pass. [Run completion](../../audit_runs/2026-10-09_official_workbook_cleanup/audit_completion.md) and [page/Decisions proposals](../../audit_runs/2026-10-09_official_workbook_cleanup/registry_proposal.md) document the boundaries. Existing case verdicts remain in force. Page-specific user approval is pending; it is not a prerequisite to completion of this authorized audit.


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 8 maintained fields / 18 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N4_07_2018-DW20261013-001 through N4_07_2018-DW20261013-008 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.
