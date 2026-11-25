# N3_07_2025 editorial audit

The full-audit record below describes the 24 September completion. The dated 25 September follow-up at the end records current hashes, targeted ★-furigana restoration and the secondary principal assessment.

Status: **audited_with_uncertainty**. The complete written paper has been reviewed as a probable reconstruction, not an authenticated official original. Listening is excluded. The active user goal ends at N5_07_2025; the longer preparation inventory is retained outside this run's scope.

Baseline: `audit_work/editorial_before.json`, SHA-256 `724a229058d2ae4881e9b1e489f651b45b5e4c9b5cf9db3c90fccb551edd8a28`. Final editorial SHA-256: `25142abcf5ab945009a758fbfa36627f35c5fa7fce94cce6445e1f80e40f9ced`. Historical imported provenance and all 23 existing ledger records are preserved byte for byte. The new ledger appends 180 exact item/field changes, including one created instructional example. Three changes are medium confidence and have public provisional-fix cases; one retained question-boundary ambiguity is public and unresolved.

## Identity, sources and actual coverage

The principal written page headers identify `25-1-III` and the question sequence agrees across July2025 N3 reproductions. The cover in another compilation is distributor-added material, not authentication. Principal printed grammar labels jump from4 to6 at physical10, but question numbering, passages and the alternate complete witness establish continuous coverage: there is no missing written question in that jump.

Full paths, hashes and aliases are in the unchanged unit index. `audit_work/pdf_inventory.json` records exact PDF identities. Aliases with identical hashes are not independent evidence. All 42 indexed primary/alias paths were rehashed at finalization with no change (`source_hashes_final.json`).

| Witness | Identity and use | Actual review |
|---|---|---|
| 【试题】2025年7月JLPT日语N3真题 (`pdf_12`) | `c3b2c9b3b62d7e4580351369234108d550c11cece5be103f0325bef0d4f0ed11`; strongest complete scan-style layout, selected over initial tier order | Every original physical page1–23 visually read:1–5 vocabulary,6–23 grammar/reading. VisionOCR used only as an aid. Enlarged original crops checked physical15 and22 for underline/kana detail. |
| N3-T7-2025 完成版 — Yuuki Bùi (`pdf_1`) | `7dd31654059b1d3e30fc0c3ac15721e1d1d4970a777987adc8745a14cc21ec03`; materially different retype with branding substitutions | Every written original physical page1–23 visually read, including all options and the full final table. Its ancestry may overlap other retypes; independent corroboration is not assumed. |
| 2025年07月N3真题 with cover (`pdf_4`) | `c47c889b3a255a4b592e03dd5eabd5cb50fb5035c2c716a5b047553964de110d`; shares principal page bodies | OCR aligned for all physical2–24 against principal1–23. All deviations inspected: reading-order/ruby noise at physical5, a stray recognition dot at17, table cell order at24. Original physical1,2,4,5,9,10,13,17,23,24 visually checked, establishing shared layout and relevant disputed readings. |
| Munja native July2025 N3 | `5e20929eb85d76a8ecce4e030513e7bdf2b5ab110f1ac062ee04671a4d4af440` | All73 written questions aligned and every reported difference read (`munja_question_alignment.json`). All keys agree after converting zero-based answers. Root/section/question structure inspected: no reading passages exist in this JSON. |
| Original archived De Thi Tieng Nhat HTML | Vocabulary `80c14e63deeeefb01a04a5d7d512c28b75ccb45006b51b498302df450c569046`; reading `5c5bfc5e0848acd6a0aa0207998145988ad32be997f85e1d484b291d90fcc651` | Useful focused original-source checks for V22, R14/R17, email clause and R38 name. Historical import ancestry, not an independent vote. Working site HTML was not read or modified. |
| 高清打印版 recall (`pdf_10`) | `07d1283129e20f00d620fd0505ea5c145350b3d12e9b6bddb06d8e5b799f7fef` | Written OCR physical1–12 read. Original4,7,8,12 checked. Missing choices are literal ない/blanks, passages absent and last heading says XXX. Useful for answer fragments and R17 は, not full distractor/passage reconstruction. |
| Incomplete July2025 recall (`pdf_13`) | `b0b951e0170421f5aa5b0beafe901b66ffdf01152164ae62a9b2769f7caad93e` | All OCR physical1–11 read; original4,10,11 checked. Same incomplete recap content, ending at grammar18; no cloze/reading material. |
| Yuuki reference answers (`pdf_3`) | `657b43082c0be0a35d9fd9d3908758cee68907f5dd428e84534ddabf72bb9096` | All6 native pages' written answers read. All73 keys checked by answer text. R14 worked order has the final fragment wrongly numbered1; not adopted. |
| Chinese-distributed Japanese answers (`pdf_11`) | `795f51b42d15416336c88877abcae4d7c83ebb871bbb58a64bbc682d1198d990` | All5 original pages visually read. All73 worked answers agree; similar text/errors to Yuuki answers mean shared ancestry is possible. |
| Chinese reading translation (`pdf_7`) | `451f9a5316f6aeffcb56467f9fda3e907d8915a474dfd5e841e509c1eca9e6d4` | Focused original1 (ski/email),6 (final questions/name),7 (table). Semantic evidence only; cannot establish Japanese particles or kana size. |
| Three answer-chart images | `6db26125…`, `577342ea…`, `87e9f364…` (full hashes in index) | All three written tables visually read. Identical table content despite different hashes; one lineage. Conflicting entries are rejected below. |

Excluded by actual content/identity: listening PDFs2/5/6/9 and listening portions of mixed sources; listening native sections12 onward and10 listening-only images; archived listening HTML; shared blank answer card and generic scoring spreadsheet. They do not establish disputed written content. No outside-unit candidates or global historical candidate originals were loaded. Historical local notes remain untouched in `legacy_run/`.

## Complete content and answer review

Reviewed all12 section headings, all73 question stems,292 options,73 inherited keys,5 existing star-item explanations, all9 baseline content blocks and the restored example. Stable question IDs/order, option order, keys, import metadata and weights are unchanged. Evidence-derived totals are vocabulary35 (8/6/11/5/5) and grammar/reading38 (13/5/4/4/6/4/2). Final blocks: vocabulary0, reading10. New `reading-b010` is inserted before `reading-q014` in section2, with no fabricated historical `line`.

Principal content map: vocabulary1–8 physical1;9–14 physical2;15–25 physical3;26–30 physical4;31–35 physical5. Grammar1–6 physical6;7–13 physical7; worked example and14–16 physical8;17–18 physical9; cloze essay physical10 and19–22 choices11. Email/Q23 physical12; library/Q24 physical13; paper socks/Q25 physical14; pain/Q26 physical15; sisters/Q27–28 physical16 and29 physical17; crows/Q30–31 physical18 and32 physical19; fish/Q33 physical20 and34–36 physical21; sports questions37–38 physical22 and full notice/table physical23. The alternate complete witness's vocabulary pagination differs and was reviewed independently, not mapped by guessed page equality.

All73 answers were independently checked using readings, usage, grammar and passage logic. Key conflicts in the three chart images are V15–19 and27, grammar1–11 and14. For example, the view produces 感動 (choice4), a used car is 中古 (3), a list is リスト (2), defeat is くやしかった (1), and distance is 距離 (4). そっと means 静かに (1), not 急いで (3). Grammar choices require 世界中から／国によって／引っ越すって／どちらかというと／熱いうちに／食べたばかり／したくて／あげたら／持ってく／晴れるといい／ご参加になれます. The chart's initial grammar entries are displaced relative to the full text. Both worked-answer documents and Munja agree with the independently checked existing keys. R14's third slot is choice4 under every viable boundary alternative, disproving chart key1. These chart errors create no remaining key ambiguity.

Star orders are R14=1–3–4–2, R15=3–4–2–1, R16=4–2–1–3, R17=2–4–3–1, R18=3–2–4–1; every third slot matches its retained key. Cloze19–22 is それでも／滑れるようになりました／あの／わかりました: cold weather contrasted with practice, acquired ability, remembered trip, and learning from experience.

Reading23 requests a second check this week;24 allows borrowing reserved books, returns and reservations;25 contrasts washable reusable socks with imagined disposables;26 describes attention shifting to another existing pain. Sisters27–29 contrast opposite approaches while both dislike homework, with the sister's invented holiday essay explaining punishment. Crows30–32 rely on people's observation alarming birds, not birds reading Japanese. Fish33 distinguishes mostly unusual dishes from exclusively unusual dishes;34 links declining catch with utilizing neglected fish;35 gives the parents' educational motive;36 proposes online purchasing research. For37, Thursday's elementary-school fee is free while the high-school table-tennis fee is150yen. For38, Tuesday basketball is children-only and Friday basketball ends before16:00; Thursday18:00–20:00 is the only eligible slot. Every fee, day/time cell, ×, ★ restriction and legend was compared with both complete original tables.

Preserved deliberately wrong distractors, source-supported spelling いつの間にか, benign terminal punctuation variants, byline チュラノン ソムチャイ and source-supported names instead of distributor branding. Question37's inherited zero weight is archive metadata, not a claim about official scaled scoring. No unsupported scoring reconstruction was attempted.

## Corrections and focused decisions

High-confidence substantive/formatting repairs: underline full 苦労した and 早退した; restore grammar5's speech quotes and grammar10's ね。; restore grammar17's 作り方は and clause comma; restore the omitted library introduction; extend both pain underlines from opening quote through と言う; restore three ski-essay paragraphs and the principal four-paragraph sister layout. Yuuki's extra paragraph before でも is a harmless retype layout variation; the principal's paragraph grouping is retained. R18 already had its final full stop: an earlier scratch suspicion was rejected, producing no edit.

The missing worked example now includes its complete instructions, four choices, order3–2–4–1, third-position star and filled fourth answer mark. Semantic HTML tables retain this meaning without making it a scored question. Principal physical8 and the same page body in compilation9 establish the content; Yuuki omitted the example.

Source-visible furigana restored in176 existing fields:324 ruby groups, plus6 groups in the created example. `ruby_review.tsv` and `ruby_application.json` record bases, readings, counts and physical pages. The ruby transformation skips existing markup and protects compounds; both 患者 and 治 occurrences in the pain passage are annotated. 嫌い receives きら and 嫌な receives いや. No vocabulary reading target is given its answer in ruby. The 25 September follow-up restores source-visible ruby in scored star stems under the additive rich-content rule, preserving their base text and exact four slots; see below.

Three public medium-confidence repairs follow completed focused investigation:

- V22 choice2: 引き受けて→引き受けた. Clear principal glyph and parallel attributive past forms favor た, but a deliberately malformed て distractor remains possible in the retyped lineage. Both remain semantically wrong with 方法, and key1 is unchanged. Full pages, native options, partial recalls and worked answers were checked; the latter do not supply this distractor.
- Email clause: remove ので in アドバイスをもらったグラフ. Prefer the principal relative clause; Yuuki/HTML causal ので is also good Japanese. Chinese translation weakly supports the relative interpretation but cannot settle the original particle. Munja and partial recalls have no passage. The complete request and all four choices preserve key1.
- R38 name: グェン→グエン at both occurrences. Enlarged principal and duplicate page show full-sized エ. Native sources mix グェン with branded ユーキ, and the translation cannot decide the glyph. Both kana spellings are possible; schedule logic leaves this arbitrary name unresolved historically.

One public retained ambiguity covers all coupled boundaries in R14: principal 比べると／去年の夏に versus Yuuki/native に比べると／去年の夏; incomplete recalls additionally put ずっと in option2. Full pages and both explanations were inspected, including their final-fragment numbering typo. Every alternative produces the same sentence and starred choice4, so Japanese reasoning cannot settle the historical split. Existing principal boundaries remain provisionally. Public cases contain exact current values, strongest alternatives, recognizable source identities, actual attempts and the evidence needed to settle each issue. No uninvestigated work is represented as a finished uncertainty case.

## Legacy candidates and historical decisions

All46 written candidate rows were read in batches: reading R001–R035 and vocabulary V001–V011. Prefix is `2025-07-N3-` for every ID below. All23 root historical records were also read; the one listening-only record8440 is excluded from content decisions.

| Candidate IDs | Disposition after current source/context review |
|---|---|
| R001–R012 | Detector boundary flags are false positives; complete surrounding questions/passages present. |
| R013–R016 | Generic HTML5 wrapper findings, not exam-content corruption. |
| R017–R018, R035 | The historical closing-underline repair in the explanation is valid and present; balanced current markup retained. |
| R019–R020 | Scripts/advertising are not exam content. |
| R021–R022 | Existing semantic table is structurally and textually complete; every cell checked against physical23, printed19 (old page references were imprecise). |
| R023, V009 | User-facing answer requests in archived context do not identify an exam defect. |
| R024–R027 | Cloze stems 【19】–【22】 are valid references to passage blanks, not empty questions. |
| R028–R030 | Earlier 文書→文章, 安量→文章全体, 答→答え repairs upheld from original headings. |
| R031 | Earlier extraneous quote removal in R33 upheld. |
| R032 | Replacing distributor ユーキ with a consistent exam name was justified; exact エ/ェ revisited and now publicly provisional, not inherited as high confidence. |
| R033–R034 | Existing × cell/legend repairs upheld by both complete tables. |
| V001–V002 | にぎやか and によると are legitimate in their exact contexts; detector proposals rejected. |
| V003–V008 | HTML wrapper findings, not content edits. |
| V010–V011 | 拝見 and 帯 repairs upheld; native 拜見／带 reflects wrong-form transcription. |

Historical9511 removal of stray 笑 in the medical grammar blank is upheld;9512–14 option-boundary decisions are now the public retained R14 ambiguity.9515 comma after 稼ぐ removal is supported by the principal.9516/9522 byline refinement to チュラノン is confirmed on principal10, not replaced with Yuuki's branding.9517 R27 opening quote,9518 嫌ったから,9519 今までと,9520 未利用魚 and9521 R38 trailing punctuation are checked and retained. No old accepted/rejected/high-confidence label was treated as authority.

## Validation and completion evidence

`validate_editorial.py` ran on the final root editorial with this unit's public cases, main ledger, saved baseline, `--expect vocab=35 --expect reading=38`: **valid true**, no errors,35/38 questions,140/152 choices,0/10 blocks and no null keys. All 43 warnings are explained: the one restored example changes item membership; option objects changed through ruby markup, except the two explicitly logged base-text corrections V22 and R17. No option was reordered, no answer key changed, and no question was removed. The validator's18 regression tests also passed; tools were not modified.

Independent exact replay of all180 new records reconstructs the complete final JSON from the byte baseline, including the example's placement. The replay also verifies unchanged provenance, keys, existing IDs and ordering. Source hashes and historical ledger byte-prefix preservation pass. Artifacts: `validation_final.json`, `verification_final.json`, `source_hashes_final.json`, `new_edits.json`, `substantive_changes.json`, `ruby_application.json` in `audit_work/`. Validation establishes structure and record consistency; historical uncertainty remains in the four public cases.

Unit result is written to progress before advancing state to N4_07_2025. The next unit must start from its own live index and baseline; this finalizer must not be rerun against an already finalized root.


## Follow-up: scored ★-stem furigana — 25 September 2026

Revisited 5 scored ★ stems. Principal physical pages: 8, 9; complete comparison witness physical pages: 9. Exact paths, hashes, item/page maps and observed readings are in [the focused review](audit_work/star_furigana_20260925/review.json).

Selective placement follows the principal. The retype adds readings such as 昼食 and 作れる that the principal does not print. Q14's public whole-item current snapshot is synchronized to its new stem; the existing boundary ambiguity and its historical alternatives are unchanged.

Applied 5 high-confidence stem edits, adding 11 ruby groups. Exact base text (including whitespace), four-slot positions, all choices/keys, IDs, imported provenance and every unrelated field are unchanged. Original ledger bytes are preserved; the new records replay exactly from the new byte-preserved follow-up baseline. Original full-audit baselines/reports remain historical evidence.

Follow-up baseline SHA-256: `25142abcf5ab945009a758fbfa36627f35c5fa7fce94cce6445e1f80e40f9ced`. Current editorial SHA-256: `dd736cb0e3b982298488868a741ac542401157bc322b3e715a1656b932e4779c`.

The current structural validator passes with evidence-derived counts; no new baseline warnings. The 21 regression tests pass, including inverse rendering. Private previews were visually checked for source-supported ruby placement and slot/option visibility. The combined public-case/ledger check passes. The unit retains 4 public cases.

Separate catalogue assessment: principal `src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N3真题/2025年7月/【试题】2025年7月JLPT日语N3真题.pdf`, SHA-256 `c3b2c9b3b62d7e4580351369234108d550c11cece5be103f0325bef0d4f0ed11`, index **106** under [method 1](../../principal_uncertainty_method.md). This is unverified provenance plus the documented components in [the catalogue](../../principal_uncertainty_index.json), not authentication or a new evidence-priority rule.

See [scoped follow-up verification](../../pilot_followup_20260925/verification.json). The completed five-paper scope and queue state are unchanged.


## 2026-09-25 — principal-differences and ancestry reporting

Current reporting: 4 public departure record(s) in [principal_differences_N3_07_2025.jsonl](principal_differences_N3_07_2025.jsonl), 5 public uncertainty case(s), principal index **107**. The current exam JSON, source index and correction ledger are byte-for-byte unchanged by this reporting step. The catalogue is now [JSON](../../principal_uncertainty_index.json); [ancestry observations](../../ancestry_record.tsv) are separate low-effort historical evidence. Full comparison scope, fresh physical-page checks, exclusions, source/JSON hashes and validation are in [the reporting pilot](../../pilot_records_20260925/review.md). Its register covers observed current departures and does not certify exhaustive equality.

The newly recorded fisheries ending conflict (principal になるそうだ versus retained/alternate になるのだ) appears in both public files. One new uncertainty event raises the earlier catalogue score 106 to 107; the four previous public rows are preserved. This reporting step makes no new editorial repair.


## Reference scans finalization — 5 October 2026

Applied one heading-field edit: the printed star now has actual underline markup and the final 。 is restored. The meaningful source departure PD-001 is retired; equivalent digit width and ordinary spacing are excluded by the difference contract. Its public case remains OPEN with the corrected source reading/current value. PD-004 and all other decisions, questions, examples, options and keys are unchanged.

This is a bounded execution of the user-approved suggestions, not another full-paper audit. Reused the completed page review and rechecked physical pages 8 at the verified principal identity. No principal, source index, answer key, option order, item ID or import metadata changed.

The [frozen before manifest](audit_work/reference_scans_finalization/before/manifest.json) preserves the editorial, both public registers, root ledger, audit note, principal copy and catalogue/progress entries. All older baselines remain intact. The root ledger appends 1 `editorial_audit_v1` edit record(s) and one separate reconciliation acknowledgement; it retains all prior bytes. Retired difference IDs are historical and must not be recycled.

Final editorial SHA-256: `6eb53d8b03b2c1f736a5373347392860703d0913ed6071de4d4e055b2063707b`. Exact replay reproduces the complete final JSON. Editorial validation with this baseline, current cases, root ledger and evidence-derived counts (35 vocabulary / 38 grammar-reading questions) passed; principal-difference validation passed. Warnings: []. Source agreement does not close user-designated open cases.

[Run record](../../audit_runs/reference_scans_finalization/README.md) · [unit result](../../audit_runs/reference_scans_finalization/N3_07_2025_result.json) · [exact edits](../../audit_runs/reference_scans_finalization/editorial_changes_N3_07_2025.jsonl) · [validation](../../audit_runs/reference_scans_finalization/validation/N3_07_2025.json).


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 8 maintained fields / 25 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N3_07_2025-DW20261013-001 through N3_07_2025-DW20261013-008 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.


## Housekeeping 2 — 5 November 2026

N3_07_2025-PD-001: resolved. Keep the current underlined star, つぎ and final 。. The entire approved worked example and five STAR questions confirm the intended task and the exact heading representation. The earlier missing-underline/full-stop allegation was already repaired and its departure retired. Close this source-agreement identity under final-housekeeping authority; do not extrapolate a generic heading style or change any option boundary.

N3_07_2025-PD-002: resolved. Retain the user's いつのまにか spelling. Approved Q16 visibly prints the all-kana form in option 4; the full stem and four choices produce the same order and starred answer as the current item. いつの間にか is a plausible orthographic alternative but has no support in these exact pixels. Resolve the source-agreement case without altering the distractor set, stem or answer.

N3_07_2025-PD-003: resolved. Retain the user's えらびなさい correction. The full approved cloze heading and ski composition show the kana imperative, the 19–22 range and the current task function. The earlier inspected official-workbook cloze heading independently supports this instruction form, while its own numbering is not imported. Resolve the exact source-agreement case; preserve ruby, line break, question range and all choices.

N3_07_2025-PD-004: unresolved. Retain the user's item-specific choice のだ and keep the conflict open. Newly inspected full approved pages print そうだ, and the complete distinct Yuuki retype prints のだ. The approved page has greater evidential weight, but approval is not issuer authentication, and retype/import agreement is not independent corroboration. The manager's explanation supports a reporting ending; the causal clause also permits a direct explanatory のだ. All four dependent questions retain the same answers under either ending, so neither grammatical fluency nor answer logic settles historical wording. Do not silently override the explicit retained choice or retire its principal departure.

N3_07_2025-reading-b008-reporting-ending: unresolved. This linked older case records the same unresolved のだ/そうだ disagreement as PD-004. Full approved and Yuuki pages, all adjacent paragraphs and questions 33–36 were inspected again. The approved source prints そうだ; the retype and user-retained current value use のだ. Reporting and causal explanation are both viable and preserve the tested propositions. Keep the low historical confidence and the principal departure; update the stored snapshot to the current v3 field without editing that field.

STAR instruction: the underlined star denotes the selected position in a four-part ordering, as the worked つくえ example demonstrates. Current Q14–18 answer positions 4/2/1/3/4 follow the complete orders. Q16 is いつのまにか／外が暗くなっていた／ので／驚いた, so the third-slot answer remains 1 regardless of ま versus 間. Cloze: the complete ski-trip narrative yields それでも, 滑れるようになりました, あの, わかりました, matching current keys 2/1/4/3; the heading correctly names blanks 19–22. Fish passage: the menu has very few familiar fish, falling catches motivate promoting unused fish, the parents want the narrator to appreciate their taste/purpose, and the narrator will seek products online (Q33–36 keys 3/1/1/3). The reporting frame 店長…説明してくれた licenses そうだ, while the causal ので…のだ can directly explain the benefit. Other paragraphs use reporting expressions too, but that local tendency cannot prove the disputed historical ending. The approved page is stronger evidence for そうだ; the user's specifically retained のだ remains an explicit, source-attested but historically uncertain choice. No count of aliases or retypes is used as an independence vote.

Unchanged 107. None of the three closed source-agreement cases is charged. The fish ending, Q14 boundaries and the three other uncertain fields remain, as does the pagination flag. Other N3 later cases were not substantively reviewed by this batch.

Rebound 1 older case snapshots to existing v3 typography only; these are not counted as substantive reviews.

No editorial, ruby or principal-departure content changed. Historical fixlog bytes and all case identities are retained. [Source hashes, before/after cases and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N3_07_2025/disposition.json).

Validation follow-up: rebound the fish-passage standing-departure snapshot to the existing fullwidth parentheses. Its principal comparison, retained のだ decision and uncertainty are unchanged. The prior failed diagnostic and before snapshot remain preserved.


HK2 additional written-page reviews, 5 November 2026: 4 record-only decisions, no canonical edits. Exact sources, competing evidence and all before/after records: [N3_07_2025](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/later-direct/N3_07_2025/report.json).
