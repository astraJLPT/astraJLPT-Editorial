# N1_07_2025 editorial audit

The full-audit record below describes the 24 September completion. The dated 25 September follow-up at the end records current hashes, targeted ★-furigana restoration and the secondary principal assessment.

Status: audited_with_uncertainty. Full written review and focused investigations are finished. The output is a probable reconstruction from unauthenticated reproductions, not an assertion that any distributor holds an original.

## Baseline, identity and coverage

The preserved baseline is `audit_work/editorial_before.json`, SHA-256 `7a19fab649378ef7d7f07828740fe1bd4bd866a7042b53ec8d14a69bb8a79fc3`. Final JSON SHA-256: `7549b87c9e3ddb99735d94c3502da2330604f970383ebfd789bcc196d0b0cc62`. Historical source provenance, stable IDs and question order are unchanged. Earlier notes in `legacy_run/` are untouched; the previous in-progress checkpoint is preserved as `audit_work/audit_checkpoint_before_final.md`. Its suspicion that 玉北歴史クラブ lacks 市 was a visual misreading and is withdrawn: the checked original pages say 玉北市歴史クラブ.

The principal cover identifies July 2025 N1. Physical pages control coverage: its cover claims 31 pages, its printed numbers omit 27/33, and the written section ends at printed 35. Those inconsistencies do not change the recovered Q1-66 sequence. Every principal written page and the complete distinct Yuuki written section were visually read, including small kana, underlines, notes, all choices and star positions. All 44 vocabulary/grammar questions and 22 reading questions were checked in context, not just candidate hits. The evidence establishes two vocabulary blocks and twelve reading blocks. There is no missing scored item or unknown option/key in this reconstruction.

| Witness (hash in index) | Actual coverage / use | Assessment |
|---|---|---|
| 2025年07月N1真题.pdf, 0528708e…, 48 pages (local pdf_5) | Visually read physical 1-34: cover1, written Q1-44 pp2-12, Q45-66 pp13-34 | Principal complete reproduction; listening after34 excluded. |
| Yuuki Bui, N1-T7-2025 完成版 - Mark.pdf, 743b1b51…, 38 pages (pdf_2) | Visually read all physical1-33, including blank6/12; vocab1-11 and reading13-33 | Materially distinct retype. Substitutes names ユーキ/モギ and the worked example. Shared ancestry is possible; agreement is not automatically independent. |
| 日语师夫 high-resolution retype, 66445545…, 23 pages (pdf_11) | Written physical2-19 all visually read after alignment proved unreliable; cover inventoried | Many gaps: Q48 passage/options, leadership passage, Q54 distractors, A/B passage/questions, shogi passage/questions and final notice/table. It also changes distractors and creates multiple valid lexical choices; insufficient basis to replace complete-source choices. |
| 【试题】2025年7月JLPT日语N1真题, c873021c…, 45 pages (pdf_14) | All33 written pages aligned against principal2-34; original physical10,13,16,27,32,33 visually inspected for disputes | Same page-body lineage as principal, not another independent vote. |
| Nine-page partial 2025年7月日语N1真题, cccdfe29… (pdf_15) | All9-page OCR inventory/alignment reviewed; physical2,3,4,9 inspected visually | Stops at Q40; missing alternatives explicitly use ない. No reading/contact evidence. |
| Munja structured transcript, 818310f2… | All66 identity-matched questions/options/keys aligned; passage differences checked; both notice/table images visually read | Q46 only key conflict with baseline. Contains misordered Q38 and omitted/corrupted phrases; images share reproduction ancestry. |
| Original archived written HTML, b902c2ca… / 8ff55f21… | Focused original paragraphs for cloze intro, nue, leadership and notice; consequential historical key records retrieved | Import lineage, not independent evidence of correctness. No working HTML edited. |
| Yuuki answer PDF, 8cfc9a4e… (pdf_4) | Entire written answers physical1-6 read | Q46=1. Q20 numeral3 contradicts its own answer text (current choice2). Fallible. |
| Concise Chinese answer, 359bdc5f… (pdf_12) | Physical3-4 visually inspected | Q36=2, Q38=2, Q46=1; text overlaps Yuuki, independence unestablished. |
| Detailed Chinese explanation, 6f6402b3… (pdf_8) | Native written explanation reviewed; Q46 physical13-14 read in full | Argues Q46=4; Q36=1 is a demonstrably wrong star answer. Reasoning is evidence, not authority. |
| Chinese reading translation, d047fe20… (pdf_9) | Physical2 visually read for full Q46 passage/options | No answer key; preserves part/whole contrast. |
| Three answer-chart images, 98823a35… / f9d65e26… / 8e8eb5a0… | All three visually read | Same chart body and 6番 typo for Q46; gives Q8=2 and Q36=3 incorrectly. One shared lineage. |

All indexed source files were rehashed before installation and match their immutable index identities. Full paths, aliases and hashes remain in the index. The shared blank answer card, scoring workbook and printing advertisement do not establish exam content. Listening-only PDFs (local3/6/7/10/13) and listening HTML are outside scope. Files4/8/9/12 were considered despite folders mentioning listening because they contain written answers/translation. The distributor note acknowledges variants/incompleteness but proves no authenticity. No useful indexed written source was excluded just for a low tier. The earlier `secondary_reading_alignment.txt` used an off-by-one alignment and is not evidence; it was superseded by full visual review of Yuuki pages13-33. Useful alignment reports are `munja_alignment.txt`, `pdf14_alignment.txt` and `pdf15_alignment.txt`.

## Item reasoning and final decisions

All instructions, passages, complete choice sets, key mappings, cloze boundaries, examples, names, dates, notes and meaningful markup were reviewed. The native lexical and grammar choices intentionally include distractors; they were not improved into correct Japanese. Complete sources outweigh the incomplete retype where it substitutes readings or introduces multiple valid choices (notably Q21 and Q25). Source-preserved 本態 versus 本体, 切り捨てるのでなく, で判断, and the shogi passage's awkward 整理をつける / 興奮や感動してきた / 面白さの魅力 were retained; fluency alone is not historical evidence.

Q8 stays option3 手先: 手先が器用 is the collocation, whereas the chart's 手芸 and the curator's 手際 are not supported. Q20 stays2: the Yuuki answer text itself matches choice2 despite its numeral3. Q36 stays2: 当たり・でも・しない・限り orders 3-2-1-4, with the second slot starred. Q38 stays2 with its current printed choice order: 好きだからといって / 毎日見ていたら / 飽きそうなものなのに / 一向に, sequence1-4-2-3. Prior accepted candidate reordering is rejected; the final baseline already had the correct order.

Q46 changes4→1 at medium confidence. The nue metaphor explicitly warns that a part alone cannot reveal the entity, describes varied symptoms and asks for diagnosis. Option1 integrates all presented symptoms to identify the disease. Option4 is a serious competitor because of symptoms-as-clues, but adds 特徴的 and shifts the target to 根本的な原因. The detailed explanation's objection that あらゆる is necessarily too absolute is unpersuasive in this context. Both concise answer lineages/Munja select1, while the detailed explanation/shared chart select4; none is authenticated. Full passage, every option, translation, alternative explanations and source ordering were tested. The public case preserves the uncertainty rather than claiming a definitive key.

The four-row course table and notice were checked as real table semantics, including dates, participants, locations and selection references. Q65=3 follows the July25-August31 child/parent exception and indoor/location/age conditions. Q66=3 distinguishes the representative's required briefing from an external instructor's outline/interview duties. Telephone variants do not affect either answer. Weekday/calendar details are part of the fictional notice and were not silently shifted to exam year2025. Rechecking principal33, duplicate32, Yuuki32 and the Munja table image confirms 玉北市歴史クラブ with 市.

The25 new field edits (`N1_07_2025-EA-001` through025) restore reading aids for names and difficult words; the complete Q19 underline; the printed worked-example layout/instructions; the cloze introduction/訊 and broken spacing; missing inline notes/footnote wording; the full team underline; museum paragraph/dash/note placement; the generic A/B heading; Q46's preferred key; and exact complete Q39-40 explanatory chunks. Each before/after value and precise source evidence is in the append-only root ledger. No scored question or choice order was added or removed.

The public file has exactly five current records: medium provisional worked-example content, medium provisional A/B heading, medium provisional Q46 key, retained low-confidence ないだろうか versus なかろうか, and retained low-confidence phone number. The last two were checked against both complete witnesses, surviving alternate sources and full item context; neither Japanese reasoning nor shared copies can settle exact historical wording/digits. Current values, strongest alternatives, actual checks, source hashes/pages and residual uncertainty are self-contained. Minor orthographic/spacing differences with no substantive preference are accounted for here and in candidate dispositions rather than promoted into invented errors.

## Legacy candidate dispositions

All181 written rows in the unit-local candidate TSV (86 R and95 V) were read in manageable batches, including accepted and rejected rows; listening was filtered out. Old HTML locators were mapped by item content. The grouped table covers every written candidate exactly once; the finalization script asserts complete coverage. Prefixes below abbreviate `2025-07-N1-`.

| IDs | Reassessed disposition |
|---|---|
| R-001-006,008-009,011-027,081-082 | Detector false positives retained: ordinary word boundaries, volitional forms, particles, and 募 in 募集/応募 are valid. Context and printed source reviewed; no small-kana replacement. |
| R-007,010,028,031,054,057 | Printed instruction/heading digits already restored correctly. Four short-reading blocks and long-reading section numbering verified; no new edit. |
| R-029-030 | Footnote spacing and orthographic variants do not justify the old alternative. The full passages separately received supported ruby and broken-word spacing repairs. |
| R-032 | Prior claim that the main reproduction prints なかろうか is incorrect. It prints ないだろうか; retain it with a public low-confidence dispute against Yuuki/archived なかろうか. |
| R-033-037 | Question-choice punctuation and spacing only; retain the wording/order supported by the complete page. |
| R-038 | 頁 is correct; restore its printed ページ ruby, without substituting the base character. |
| R-039-041 | Reject 説明てきる, missing る, and OCR punctuation proposals after the full Q51 choices were checked. |
| R-042 | 得 is correctly restored; keep current text. |
| R-043-044 | Reject corrupted whole team-management passage and でも for ても. Current で判断 and 切り捨てるのでなく are supported. Extend the first underline through チームの and restore ruby/notes. |
| R-045-046 | Current 主観的な and quoted ヒヨコ are supported; no further change. |
| R-047-049 | Reject 奥味 and ほと recognition errors; 興味 and ほど are clear. とき/時 is an immaterial orthographic difference. |
| R-050 | Q56 punctuation-only difference; retain current wording. |
| R-051-053 | Full museum passage, including the omitted paragraph, is already restored. Retain valid current spellings; restore its dash, introductory paragraph break, note location and 甲斐 ruby. |
| R-055-056 | A/B alternatives are OCR/spacing or valid 良い orthography; keep supported current text. Generic heading change separately logged at medium confidence. |
| R-058 | 開発 is correct in the shogi passage; preserve it. |
| R-059-060 | Reject the unrelated Munja museum-style notice heading; the municipal notice is the correct content. Other difference is punctuation only. |
| R-061-064 | Circled schedule references are correctly restored as ①/②/③ and agree with Q66 logic. |
| R-065-068 | All four printed Q54 choices already restored and checked; preserve them. |
| R-069 | Reported missing Q63 is present as reading-q019, correctly located between Q62 and Q64. |
| R-070 | 秤 is the correct character; add its printed はかり ruby. |
| R-071 | Phone-number historical high confidence is not justified by shared copies. Retain 021-885-5700 but publish the 242-000-8688 alternative at low confidence. |
| R-072-078 | HTML/parser/template diagnostics do not identify new exam-content damage. Table semantics checked: header plus four groups, four columns, meaningful cell contents. All copies checked say 玉北市歴史クラブ; no name edit. |
| R-079 | Reject the curator suggestion 手際 for Q8: 手先が器用 is correct; 手際 normally takes がよい and is not the printed correct option. |
| R-080 | Old missing-item report is not an additional missing scored item. Reconciled the complete Q45-66 sequence, including restored Q63. |
| R-083-086 | Reject 議論すする and 法定 recognition errors; punctuation is immaterial; current 評価されています is correct. |
| V-001-004,006,093-095 | Detector false positives: 少しゆっくり, しよう, によって/により and 働きやすさ are valid across their boundaries. Preserve deliberate wrong lexical usage in distractors. |
| V-005,007,020 | Missing instruction numbers already restored correctly; current headings match the reviewed section sequence. |
| V-008,010,014-018 | Heading punctuation/spacing variants only; no new substantive edit. |
| V-009,012,021,029,042,089-092 | 惑わして and あきれたような are already correct. Full final cloze paragraph and notes were restored previously. Correct the cloze introduction to コミュニケーションのあり方 and restore printed ruby/訊, with source evidence. |
| V-022-024,026-028,030-037,039,045-047,049-057,059,063-064,067,069 | Earlier substantive restorations are upheld after full item review: Q1/Q3/Q7/Q9/Q11-13 choices, 中川, Q21/Q23-25 distractors, Q27, Q31 order, home-page context and source punctuation. Choices intentionally contain wrong readings/usages; do not make them linguistically correct. |
| V-025 | Q7 stem differs only by a comma and blank spacing; keep the same wording. |
| V-038,043,058,061,065,070,072 | Reject added もの in Q15, the 悉く反発 rewrite, misplaced blank, added の, omitted 色の, 買い for 買え, and 铺 / omitted らしい in Q37. Complete printed items and grammar favor current readings. |
| V-011,013,019,040-041,044,048,060,062,066,068,071,076 | Harmless kana/kanji, punctuation or spacing alternatives; preserve current exam text. Q39-40 explanatory chunks separately made exact and complete against printed option text. |
| V-073-075 | Reverse the earlier accepted conclusion, without a new JSON reorder: current Q38 already has the printed order. Sequence 1-4-2-3 puts option2 at the third starred slot. The Munja/retype alternative order is not the printed order. |
| V-077-080 | Nested cloze choices are not missing questions. All Q41-44 stems, options and keys are present. |
| V-081-086 | Historical HTML template/parser warnings concern surrounding markup, not missing exam content in the current JSON. |
| V-087 | Reject the old 手際 advice for Q8; source wording and Japanese collocation establish 手先, option3. |
| V-088 | Q23 is present with all four choices; no missing question. |

## Validation and diff reconciliation

The structural validator passed on the final root JSON with the current public cases, full root fixlog, preserved baseline, and evidence-derived `--expect vocab=44 --expect reading=22`. Result: valid, no errors; 44 vocabulary questions/176 options/two blocks and22 reading questions/88 options/twelve blocks, no null keys. The final report is `audit_work/validation_final.json`.

Three baseline warnings are explained: vocab-q024 and reading-q018 options changed only to add printed 林/棋士 ruby, preserving option order and keys; reading-q002 key changed4→1 intentionally at medium confidence with its public case. Imported source provenance is byte-value unchanged. Replaying all25 new records against the exact baseline reproduces the entire final JSON semantically; there are no unlogged content changes. Existing169 ledger records are byte-preserved and25 appended, for194 total. New medium records all link to the appropriate current public record. Source files and index were rehashed unchanged. Structural success does not authenticate a reproduction; the five public cases remain part of the deliverable.

Unit result is recorded before queue advancement. Next unit: N2_07_2025.


## Follow-up: scored ★-stem furigana — 25 September 2026

Revisited 5 scored ★ stems. Principal physical pages: 9, 10; complete comparison witness physical pages: 9. Exact paths, hashes, item/page maps and observed readings are in [the focused review](audit_work/star_furigana_20260925/review.json).

No printed furigana occurs in these five scored stems; no editorial change was needed.

Applied 0 high-confidence stem edits, adding 0 ruby groups. Exact base text (including whitespace), four-slot positions, all choices/keys, IDs, imported provenance and every unrelated field are unchanged. Original ledger bytes are preserved; the new records replay exactly from the new byte-preserved follow-up baseline. Original full-audit baselines/reports remain historical evidence.

Follow-up baseline SHA-256: `7549b87c9e3ddb99735d94c3502da2330604f970383ebfd789bcc196d0b0cc62`. Current editorial SHA-256: `7549b87c9e3ddb99735d94c3502da2330604f970383ebfd789bcc196d0b0cc62`.

The current structural validator passes with evidence-derived counts; no new baseline warnings. The 21 regression tests pass, including inverse rendering. Private previews were visually checked for source-supported ruby placement and slot/option visibility. The combined public-case/ledger check passes. The unit retains 5 public cases.

Separate catalogue assessment: principal `src/日语JLPT历年真题/N1真题（2010-2026.07）/2025/2025.07/2025年07月N1真题.pdf`, SHA-256 `0528708e83d1c809f1af5f035e943d12dce54e6fdac319d70576485320479dcf`, index **106** under [method 1](../../principal_uncertainty_method.md). This is unverified provenance plus the documented components in [the catalogue](../../principal_uncertainty_index.json), not authentication or a new evidence-priority rule.

See [scoped follow-up verification](../../pilot_followup_20260925/verification.json). The completed five-paper scope and queue state are unchanged.


## 2026-09-25 — principal-differences and ancestry reporting

Current reporting: 1 public departure record(s) in [principal_differences_N1_07_2025.jsonl](principal_differences_N1_07_2025.jsonl), 5 public uncertainty case(s), principal index **106**. The current exam JSON, source index and correction ledger are byte-for-byte unchanged by this reporting step. The catalogue is now [JSON](../../principal_uncertainty_index.json); [ancestry observations](../../ancestry_record.tsv) are separate low-effort historical evidence. Full comparison scope, fresh physical-page checks, exclusions, source/JSON hashes and validation are in [the reporting pilot](../../pilot_records_20260925/review.md). Its register covers observed current departures and does not certify exhaustive equality.


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 4 maintained fields / 5 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N1_07_2025-DW20261013-001 through N1_07_2025-DW20261013-004 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.


## Housekeeping 2 — 5 November 2026

N1_07_2025-PD-001: resolved. Retain the user's 充分 correction. Direct inspection of the complete approved passage and its two dependent questions confirms 充分 in the final investment/return sentence. 十分 is a plausible spelling alternative but is not what this page prints. The current departure table is already empty. Resolve this source-agreement identity under final-housekeeping authority without editing exam content or claiming authentication of the entire file.

The passage contrasts chicks' innate avoidance of fatal falls with humans' learned fear and subsequent flexibility. Q55 option 2 identifies avoidance of fatal danger; Q56 option 3 identifies the benefit of low initial judgment capacity. The final investment metaphor describes ample return, so 充分 and 十分 would both express a viable meaning. Meaning cannot choose the glyphs; the approved page clearly prints 充分. Current questions, options and keys 2/3 agree with the complete task.

Unchanged 106. The pagination issue and four other uncertain targets do not concern this verified spelling.

No editorial, ruby or principal-departure content changed. Historical fixlog bytes and all case identities are retained. [Source hashes, before/after cases and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N1_07_2025/disposition.json).

Validation follow-up: restricted the public evidence record to its declared schema and rebound two older case snapshots to already-existing v3 typography. Original failed diagnostics and the first acknowledgement remain preserved; a supplemental seal records the schema repair. No substantive decision or editorial content changed, and these two record repairs are not counted as source reviews.


HK2 additional written-page reviews, 5 November 2026: 5 record-only decisions, no canonical edits. Exact sources, competing evidence and all before/after records: [N1_07_2025](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/later-direct/N1_07_2025/report.json).
