# N2 July 2023 editorial audit

Status: audited_with_uncertainty.

## Start (2026-09-26)

Confirmed live state after N1 July 2023 closure/reporting. Preserved byte baselines of editorial JSON, root fixlog and public cases before editing. Read the complete current index and baseline structure. No principal selected yet. Listening and generic scoring/answer templates are excluded from written reconstruction.

## Reviewed result

Completed the evidence review of July 2023 N2: 51 vocabulary/grammar questions and 20 reading questions, 284 ordered choices, all 14 content blocks (including the worked example and park table), 14 instructions, five scored star arrangements and their explanations. The proposed result has 38 exact field edits: 34 high confidence and four medium-confidence passage fields. Fifteen public cases distinguish four provisional fixes and eleven investigated retained ambiguities. All answer keys are retained. The public principal register contains 28 current departures, including inherited differences and spelling variants. No scored written item, choice or passage remains missing.

Baseline SHA-256: `c403ad0175e5c503ac7ccbdd1559ea26d3e51c1472b6f500fed4c3c9f2c018e4`. Before bytes of the editorial JSON, root ledger and public cases were preserved before any root edit. The import sources, stable IDs, item ordering and archive scoring metadata remain unchanged. Proposal SHA-256 after verification: `8d112af49593090c01ac8852641ea94da6183dbed70e98d8c60d3b75aae71969`.

## Evidence identity, coverage and selection

The complete current index was read. All 23 indexed content hashes and 26 source/alias paths were verified; `audit_work/source_inventory.json`, `path_hash_verification.json` and `page_maps.json` preserve exact indexed identities. A focused July2023/N2 source-path search found no additional unindexed local question witness. July and N2 identification is consistent in the question headers and content. No document has an authenticated issuer chain of custody.

The selected principal is `src/Yuuki Bui/Đề thi N2 các năm Yuuki Bùi/N2 7-2023/Đề N2 T7-2023 (230710).pdf`, SHA-256 `a4ce4acdd77467de3b3ff99193646abd445b8b8c72252aed8fa511d75eb4f62e` (local pdf_3). Its physical pages 1–32 were all visually inspected, including the separator at7. Pages33–36 are listening and excluded. The full worked example, selective furigana and complete question41 make it a useful coverage principal, despite clear errors and meaningful variants. Choosing it does not authorize copying its errors or overriding better item-specific evidence.

Principal page map: 1 Q1–5; 2 Q6–10; 3 Q11–13; 4 Q14–20; 5 Q21–25; 6 Q26–30; 7 separator; 8 Q31–36; 9 Q37–42; 10 example and Q43–44; 11 Q45–47; 12 cloze passage; 13 Q48–51; 14 Q52; 15 Q53; 16 Q54; 17 Q55; 18 Q56; 19–20 library and Q57–58; 21 university/Q59–60; 22–23 honesty/Q61–62; 24–25 photography/Q63–64; 26–27 A/B and Q65–66; 28–30 astronaut and Q67–69; 31 Q70–71/memo; 32 complete park notice.

Other actual inspection and comparison:

| Indexed witness | Inspected scope and role |
|---|---|
| pdf_11, `【2】2023年07月N2 真题.pdf`, SHA `8457ec09de0d55801a29fbfa5431153fd7948d2b3c615dd49fb21b150b0ea9b5` | Full visual written review, all physical1–31. Substantively different wording and long-passage transition; useful alternative. Printed ruby leakage on p10 and p12, missing Q41 clause on p8, and no complete worked example prevent treating its Tier1 label as decisive. |
| pdf_4 compact, SHA `5433d4cb1696aaf6e5a76aeb6c2e25c4ed1edd6caf8a426c235d131a509c0fc2` | All written physical2–12 and written key regions on15 visually reviewed. Cover1 is not counted as viewed; listening13–14 excluded. MuPDF reported resource-xref errors on several pages, but the reviewed written content was legible and could be checked against alternate families. |
| pdf_9 compact, SHA `5d5194907f54e326967f01b4be4fd0b657651314e609fa7cd9b25bb07b0cd1ea` | Pagewise written OCR2–12 aligned with pdf_4; p15 written key visually checked. Key47 differs (2 versus3), despite closely shared question text. Rendered p2 is not claimed as visually reviewed. |
| pdf_13 native retype, SHA `7e846b449791735cc3580ac5dbf3590a3cf5993d1a3259904568546036aebeee` | Cover1 and written2–10,13–16 visually inspected. Written11–12 not claimed as visual coverage. Its cover explicitly cautions that the material is not a final perfect edition. Additional ruby varies; false readings/other typographical errors mean it is not a source for indiscriminate ruby expansion. |
| pdf_15 revised31-page reproduction, SHA `891589c0ed205d4118cdb47d988f3785bbf4b6ab37ed35d3c1c209fd8e384142` | Visual1–3,5,8,10–11,18,26,29–30; all31 written OCR pages aligned with pdf_11. The same printed leaks and omissions recur. Different file hashes and a revised label do not establish independence or better transcription. |
| pdf_2 Yuuki written solutions, SHA `c532a6c32aa3863c11eb128d80c28fb65415145e6a56430c959193d2fbdfa9b8` | Written regions of all physical1–4 viewed, including complete worked sentences. Listening region excluded. Its Q47 chart error is corrected by its own worked sentence. |
| pdf_6/pdf_14 36-page explanations | In-scope native written1–15 aligned programmatically; differences are mostly footer ordering. Focused Japanese passages on5,6,7,9,11 were read; pdf_6p7 also viewed. These explain grammar, but have a wrong Q43 order label. Later listening excluded. |
| pdf_10 shorter explanations | Written scope1–9 identified; p5 and p8 viewed for star order, cloze and reading reasoning. Other rendered pages are not claimed as visual coverage. |
| pdf_12/pdf_16 detailed explanations | Written scope1 and3–47 (p2 listening excluded). pdf_12 visually viewed1,22,23,30,37,38,44,45,46; paired written OCR reviewed and 36/46 rendered page fingerprints match exactly at40dpi. Same explanation family; not two independent votes. |
| pdf_7 reading translation | Identity and early page previews inspected; Chinese explanation/translation has low ability to settle the exact Japanese alternatives. Not a full visual comparison witness. |
| Munja JSON, SHA `2fe31776549b8179698f8dd448569f2438f9aa10c038b4e6bcc8fbe8033bf820` | All71 question objects/284 options and all13 textual passage blocks aligned and substantively reviewed; 0-based keys converted and checked individually,71/71 agree. Complete park notice and memo images both visually read. |
| Immutable archived vocabulary/reading HTML, SHA `edf0433b2df4571d4c82c60dfc873edcc5871aa3cf9e27a3b4ec18720a17c8a5` / `0f8313503ca609077a06568c9a5c7ac97d016de69221eb96d3e2ecda6a509d9b` | Questions, choices, cloze and reading blocks aligned against baseline; all material filtered differences reviewed. Used as historical transcription evidence, not selected principal. No working HTML was edited or used as an acceptance target. |

Listening-only question/translation files, listening regions of mixed PDFs, generic answer sheets and scoring spreadsheets are excluded. No listening audit was performed. An exploratory OCR pair report contains automatically extracted out-of-scope compact pages13–14; those entries were not reviewed or used for any written decision. Only in-scope alignments support the statements above.

The full structured alignment catches corruption such as くずれで, dropped に after 以上, omitted を after 外食, おかげた, 返事がきていない, 本に世界, 判断が基準, extra を in Q65, 取れて for photographs and 電話でする. These were rejected using the complete printed items and Japanese syntax, not copied. In particular, Munja itself contains 大学院以上 and 学生が: it does **not** corroborate the restored university passage. The archived passage, principal and alternate full retype instead support 大学以上/学生に.

## Reconstruction decisions and answer reasoning

Clear new corrections: Q6choice4 带→帯; terminal stop inQ14; removal of unprinted underlines on usage headwordsQ26–30 while preserving every option underline; semantic worked-example and answer-sheet tables; missing park-homepage instruction; university 大学院以上→大学以上 and 学生が→学生に; dream-support 夢の→夢を. Existing line-wrap whitespace inside なって was joined during library ruby restoration; it was a real newline, not a literal backslash-n defect.

Restored 67 printed ruby spans selectively: Q13four choices, Q16two options, 再確認/廊下/first鑑賞 in stems; six cloze香道 occurrences, first two香木 and繊細; two employee-email occurrences; ecology body/notes; first司書/身振/配慮; honesty and photography body/notes; 一緒/維持 options; eight of nine long-passage宇宙 occurrences plus exact partial readings such as 衛, 慰, 身振, 反射 in its note; Q67–68 choices. The first-spaceflight 宇宙 compound remains unannotated, as printed. The extra 輝 reading belongs only to the provisionally restored sentence and is directly printed in pdf_13p14. The accidental tiny numeric artifact near Q13choice3 is not a linguistic reading. The problem8 heading and worked-example instruction preserve the underlined star. Four scored slots and option order are unchanged.

Four provisional fields, each with exact before/current values and strongest alternatives in public cases:

1. `reading-b001/content`: prefer 期待を手放し over 期待することを手放し. Alternate retypes and a dated book excerpt favor the shorter direct object, but both are grammatical. Keep local exam 生きる, rather than importing the excerpt’s different いる.
2. `reading-b004/content`: prefer pcforest, matching PCフォレスト and alternate copies; peforest is still possible as an arbitrary address. Keep the complete principal polite closing; other copies omit it.
3. `reading-b011/content`: restore そこは、自分が「いちばん輝く場所」であるからだ。しかし、人にはだれでも、. The complete alternate family, Munja, explanations and Q68’s wording support the discourse transition. Intentional excerpting cannot be excluded. The separate を repair is high confidence.
4. `reading-b012/content/html`: prefer 青水湖 and flower-row山頂へ, supported by the notice image and alternate retypes, boat context and parallel itinerary syntax. Proper-name arbitrariness and abbreviated routes leave residual doubt.

Eleven retained cases cover Q7choice2副祉/副社; Q21のは/には; Q30underline ending; Q33を/も; Q35パジャマ姿/の姿; Q37choice4 finalと; Q43けんかをする/けんかする; Q51choice1 present/past tense; Q51choice4 finalか; Q56今; employee email honorific/department/connective. In particular, adding と or か to an intentionally wrong choice is not established merely by making it more grammatical. Those inherited changes remain openly uncertain. Harmless kana/kanji orthography is retained and recorded where it departs from the principal, rather than proliferating unsupported repairs.

Focused external evidence was used only after local comparison. The publisher-hosted 2021-05-18 福嶋聡 essay at `https://note.com/jimbunshoin/n/n9582a3f3353c` identifies 平田オリザ『下り坂をそろそろと下る』(2016) and quotes pp94–95 with 大学以上. The 2017-07-14 attributed 西脇俊二 excerpt at `https://www.kotobasagashi.net/kotoba/view.php?kid=4692` supports 期待を手放し but differs in 生きる/いる; it is a secondary quotation, not an exam page. Distinctive astronaut-phrase searches found exam reproductions but no attributable original author text. A public Qianyu recall PDF was discovered; local download failed and the web screenshot calls did not return usable images. It is not counted as visually checked or as decisive evidence. No contact address was contacted.

All71 answers were independently reconsidered with all choices. Vocabulary/grammar key groups are `24413 / 13424 / 132 / 2314432 / 24123 / 42113 / 314241341232 / 14233 / 3241`; reading groups are `42124 / 13431324 / 43 / 421 / 23`. Important key-source failures:

- Q39: pdf_12p1 gives3, but its own p22 explanation says1. Sleep reduction is precisely the loss of a recovery opportunity (ほかならない), not a belittling にすぎない. Other charts and reasoning support1.
- Q43: pdf_6p7 labels order4321, while its solved sentence is4312. The complete choices assemble すれ違っても→目を合わせる→こと→すら; ★third ischoice1. The shorter explanation p5 gives4312.
- Q47: Yuuki solution p3 and compact pdf_9p15 charts give2. The same Yuuki worked sentence, the printed choices and pdf_4p15/pdf_12p1 support1432, so ★third ischoice3. This disagreement does not make the well-determined answer provisional.
- Q69: pdf_12p46 prose mistakenly names option4 while quoting the meaning of option1; its p45 header and all useful charts say1. The author advocates passing dreams to younger people, not a prerequisite of varied expertise.
- Q70: only flower course meets railway use, at most2 hours and different entry/exit. Q71 has Dan plus15 colleagues, so16 must split into groups of at most10. Booking is10 days ahead, cancellation3 days, and October opening9:00. Keys2/3 are unchanged.

## Legacy candidate and decision reconciliation

All164 rows from this unit’s written-file candidate TSV were read in batches and all31 written records from the66-record historical ledger were inspected. Incidental listening comments inside written-file rows were classified out of scope. No global candidates or original global ledger were loaded. Prior labels were treated as claims, not authority. The following covers every substantive issue; routine duplicates share a disposition.

| Local candidate group | Current disposition |
|---|---|
| R001–005, R007 | Retain delimiter, 反対, clean body text and corrected course name. Restore removed readings as real ruby rather than inline kana. |
| R006/R080 and history8605 | Reverse the source-fidelity reversion. 夢を応援する is grammatically required and directly supported by other complete witnesses; source の is recorded as a principal defect. |
| R008/R045 | The tennis-school descriptor was correctly removed, but the generic replacement was incomplete. Restore the legible principal park-homepage descriptor. |
| R009/R018 | Prefer pcforest at medium confidence; keep the attested closing and document its competing omission. |
| R010–012/R020 | Retain repaired passage ranges; record current explicit ranges as inherited principal departures. |
| R013 | Reassessed beyond the previously chosen copy; prefer 期待を手放し provisionally, with the full longer alternative retained publicly. |
| R014–015/R017/R019/R021–040 | Retain valid Japanese against structured errors; preserve coherent passages, note placements and ordinary orthographic/punctuation variants. Q56今 variant is separately public. Source-specific いい/言い spelling is a principal departure, not an answer repair. |
| R016 | Retain employee-email wording, restore selective ruby, and publish the honorific/department/connective variants. |
| R041 | Restore the attested missing long-passage transition at medium confidence after full explanation and question comparison. |
| R042–044/R046–051 | Retain ordinary orthographic, final-stop and width variants; no new question/choice change. |
| R052–063 | Reviewed large-kana detector hits are valid words; no small-kana repair. |
| R064–079 | Boilerplate, generic/availability/thank-you comments and listening reports do not establish written changes. Cross-part 運賃 and 正しい reports are stale; both vocabulary items are already correct and were checked directly. |
| R081–082 | Prefer 湖 and restore flower-routeへ at medium confidence instead of treating principal-copy fidelity as a ban on reconstruction. |
| V001–005/V007/V009–012 | Retain coherent kanji-writing instruction, small-tsu repairs, numbering, からといって, piano clause, speech punctuation and ★ instruction. These are supported by task structure and direct sources. |
| V006/V008/V013–015 | Retain inherited を, finalと, finalか, パジャマ姿 andけんかを; withdraw unwarranted historical certainty and publish the viable principal alternatives. |
| V016–031/V051–081 | Retain valid written forms and coherent cloze markers against structured corruption; width, underscores, speaker separators and normal orthography need no semantic rewrite. Q14’s missing stop was separately restored. |
| V032–034 | Largeよ detector hits are valid. |
| V035–050 | Boilerplate and nonspecific comments require no content change; listening reports excluded; stale 運賃 and正しい comments checked against the actual vocabulary items. |
| V082/history8606 | Preserve the recovered worked example, improve its four-slot/answer-sheet structure and printed underlines, and retain the 文 repair of 分. |

Historical sequences211/228,1208–1212,1214,1216–1222,1224,1226–1229 remain supported (with source ruby now represented correctly). Sequence1215 is completed by the recovered descriptor. Sequences229/230 are reversed because 大学以上/学生に are better supported and coherent; Munja was an unreliable basis for those earlier edits. Sequence1213’s を repair is reinstated, reversing8605. Sequences1223/1225/1230–1232 remain as explicitly uncertain inherited variants rather than automatically high-confidence fixes. Sequence8606 is preserved semantically and made structurally faithful.

## Proposal verification and limitations

The structural validator, exact edit replay, source-hash checks, all current public snapshots and principal links pass. Seven option-array warnings are expected: one actual character correction inQ6 and ruby-only changes to Q13/Q16/Q65–68. No option was reordered and no key changed. Private proposal checks also preserve the semantic worked-example table, five star answers, meaningful underlines, selective ruby base spans and all notice rows/constraints. A proposal-only escaping mistake found during the underline check was corrected before any root installation; the final HTML contains genuine tags, not escaped markup.

These checks establish consistent records and reconstruction coverage, not exam authenticity. The15 public cases are results of completed focused investigations, not deferred work. The principal’s score will be reported separately after the unit result, using the highest applicable defect category per item/field and excluding repaired editorial omissions and separate key-file errors.

## Installed validation

The installed JSON passes the structural validator with51 vocabulary/grammar and20 reading questions,284 choices,14 blocks, no unknown choices or null keys. Exact replay of38 field edits reproduces the output and preserves historical import metadata and every stable ID. The original ledger bytes are an unchanged prefix. All26 source and alias hashes were rechecked. The7 option warnings are the reviewed 带→帯 correction and six groups of ruby-only option changes; option order and every key are unchanged. The67 restored ruby spans, four-slot examples, five scored star arrangements, option underlines and complete notice table were checked. Public snapshots and cross-links validate.

## Separate reporting and queue closure

After the unit result, the selected principal was added to the method1 catalogue with score133: unverified100,1 major defect,7 minor defects and14 uncertain fields; no metadata flags or missing units. The22-entry catalogue and28 departure rows pass both required CLI validators. Three encountered ancestry observations were appended with exact inspection limits. State advances to N3_07_2023; the overall goal remains active through N5_07_2023.


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 15 maintained fields / 80 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N2_07_2023-DW20261013-001 through N2_07_2023-DW20261013-015 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.


## Housekeeping 2 — 5 November 2026

N2_07_2023-PD-004: The user rejected the change to えらびなさい in this N2 heading. The boxed and compact same-sitting copies and printed 2012/2024 N2 grammar instructions support the current kanji. Keep the explicit difference from the selected copy, which actually uses kana.

N2_07_2023-PD-003: The requested additional check finds めんどくさい in the selected copy and めんどうくさい in a differently typeset boxed witness, the compact and the exact native option. Those copies also share features; they are not three original printings. Retain the fuller attested distractor pending stronger proof.

N2_07_2023-PD-005: Inspection of the selected physical page establishes 言い換えられる, already the editorial form. The compact page agrees. The boxed and native fields actually have いい換えられる: preserve that alternative in the case but retire the false standing departure. Do not alter the four choices or the key.

Retain 133: S-010 concerns 壊すには/のは, not contraction in the wrong choice. The formerly incorrect description of the fourth Q58 option was not a charged event. 0 editorial fields changed. 3 public and 5 principal snapshots rebound to pre-existing field changes; not substantive reviews.

[Before/after decisions and receipts](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N2_07_2023/disposition.json).
