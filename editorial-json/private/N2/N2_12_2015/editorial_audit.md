# N2_12_2015 — written-content audit

Completed 6 October 2026 in run `2026-10-06_N1_12_2016_to_N5_07_2010`. Result: **audited_with_uncertainty**. Investigation and available written coverage are complete. This is an exam reconstruction with 75 playable and gradable questions, 300 ordered choices, 12 context blocks and one restored worked STAR example. No scored question, necessary context or witnessed example is omitted. Listening is excluded.

The frozen baseline is [audit_work/editorial_before.json](audit_work/editorial_before.json), SHA-256 `90dcc3bc9869b5c49968606fe28467cc0523e64228bf7c9ad23cef7c6e26fb8b`. All 178 historical ledger rows (176,907 bytes) remain byte-for-byte at the start of the main fixlog. Thirty new exact edits are appended: 25 high-confidence restorations and five medium-confidence decisions. Eight public cases remain: five provisional fixes and three unresolved retained values. All 75 answer keys are unchanged. The principal-departure register has 22 current rows, including inherited spelling and punctuation variants.

## Identity, principal and actual coverage

The selected principal is the indexed 14-page **Đề N2 12-2015.pdf**, source 4, initially tier 1:

`src/Yuuki Bui/Đề thi N2 các năm Yuuki Bùi/N2 12-2015/Đề N2 12-2015.pdf`

SHA-256: `4afb4f1c7a14783fda08675390f7c7473265bc8c1d3cb00391c3df6de95c6e47`.

Its entire written content on physical pages 2–11 (printed pages 1–10) was read visually, including every option, attribution, note and instruction. Cover 1 and the transition to listening on page 12 were also inspected. The cover and page headings identify December 2015 N2; the content aligns with the other sitting-specific witnesses. Branding, clean typesetting, distribution labels and file hashes do not establish issuer custody. No registered approved original applies to this exact unit. Provenance is **unverified**, not authenticated and not classified as a known reconstruction solely from its appearance.

The principal was selected for complete, legible written coverage, its worked example and its generally useful preservation of text and annotations. It was not allowed to decide every disputed field. Its convenience copy retains its original filename and bytes in [principal/Đề N2 12-2015.pdf](principal/Đề%20N2%2012-2015.pdf); the catalogue identifies the immutable source under `src/`.

| Principal physical pages | Reviewed content |
|---|---|
| 2–3 | Vocabulary Q1–31, target underlines, all reading and kanji distractors, usage options |
| 4 | Q32 usage item; grammar group label and Q33–44; STAR heading and example opening |
| 5 | Example continuation and marked bubble; Q45–49; entire sushi cloze Q50–54; reading group and Problem 10 instruction |
| 6–7 | Short passages Q55–59, factory notice, glosses; teaching passage and Q60–61 |
| 8 | Q62; toy passage Q63–65; science passage opening |
| 9 | Science continuation, notes and Q66–68; A/B note-taking texts and Q69–70 |
| 10 | Long fiction-writing passage, all seven notes and Q71–73 |
| 11 | Workshop heading, Q74–75, four-cell notice and all booking/cooling conditions |

Two further question witnesses received complete visual written review: source 23, **2015年12月n2真题(1).pdf**, physical pages 1–18; and source 8, **2015年12月N2真题.pdf**, physical pages 2–16, plus cover 1 and written answer grid on page 20. The alternative layout includes the complete example; the older 20-page copy omits it. The different layouts are not proof of independent acquisition. Source 4 and source 23 share the transposed example labels; source 8 and source 19 share several distinctive wrong readings. The known relationships are bounded to inspected pages.

Source 2's structured written sections 0–13 were aligned against all 75 questions, 300 options and 12 contexts; relevant differences were read and the Q7/Q22 explanations checked. All 75 zero-based keys were converted and matched by aligned item identity. This is not a claim that every Chinese explanation was read. The embedded notice image is source 27, not a second independent witness; its entire four-cell notice was visually reviewed.

Focused visual checks covered source 0 cover 1/page 2; source 21 page 1; source 17 page 3; source 19 pages 2, 3 and 16; source 18 analysis page 2; source 20 analysis pages 1 and 4; and source 3's page-1 written answer grid. Native text from source 18 page 7 and source 20 pages 2, 3 and 18 was only supplementary navigation/content evidence, not a claim about their printed typography. Source 21 page 2 was rendered but not read. Listening, blank answer sheets, scoring spreadsheets and unnecessary duplicate analyses were excluded. Archived HTML was not needed for principal selection after complete usable question witnesses were found. The imported editorial is a reconstruction, not an independent witness. No external research or contact with exam addresses was used.

Exact paths, hashes, reviewed locators and exclusions for all 28 indexed sources are in [source_review_coverage.json](audit_work/source_review_coverage.json). All 28 original source hashes were checked at entry and again before completion; the source index was unchanged.

## Editorial decisions and residual uncertainty

The group labels for vocabulary, grammar and reading, rendered dialogue turns, STAR heading underline, full worked example, passage paragraphs, factory-notice hierarchy and required reading aids are restored. The example's printed options are 1 テレビ / 2 見ている / 3 を / 4 人. Its solved words and marked second bubble require the sequence **1–3–2–4**; the principal incorrectly numbers the middle words 2–3. That demonstrable label error is repaired without inventing example content.

The factory title was already present as a literal angle-bracket string. It is now escaped in HTML so it remains visible; it was not claimed missing. Main bullets and nested meeting details retain their meaning. The art notice preserves its two-by-two course table, all objects, ages, session times, booking rules and cooling delays. The accidental comma in `B～D、の` is removed and `お持ちになる` is corrected to `お待ちになる`, supported by the principal, standalone notice and explicit waiting context. Valid `観賞` and label brackets are retained with principal differences.

| Issue | Current decision and strongest contrary evidence |
|---|---|
| Q7 option 2 | Provisionally restore **準調**. Principal and alternate copies support it and it completes the specific 準/順 × 長/調 contrast. The older copy, source 19 and source 20's dictionary explanation really have 準備, an effective wrong choice. Pattern logic does not authenticate the original. |
| Q22 option 4 | Retain **けずった**, supported by source 17, source 23, source 18's explanation and structured text. Principal/source 8/source 19 clearly print はずった; another analysis explains 外す. Do not silently manufacture はずした from a grammar preference. |
| Sushi quantity | Provisionally restore **約400グラムもご飯**. The emphatic particle fits the comparison with a 150-gram bowl and is directly witnessed. Its omission in source 8 and structured text is grammatical, so history remains uncertain. |
| Factory preparation time | Retain **9時** with an unresolved case. The principal and alternate layout have 9時半. Both precede the 10:00 visit and neither affects Q56; no adequate item-specific basis establishes which arbitrary time was printed. |
| Q57 option 4 | Provisionally prefer **ヒトと動物との**. It directly expresses the comparison in the passage; older/structured text has ヒトは動物との. This remains a wrong comprehension option under either wording. |
| Teaching glossary | Provisionally restore **全くわからない** for チンプンカンプンな. It expresses complete incomprehensibility in context; 全てわからない is a real printed rival, not an OCR invention. |
| Course D fee | Provisionally restore **2,000円**, clearly printed in the principal, alternate question layout and standalone notice. Source 8 and source 19 really print 200円. The probable digit loss is an inference; fee does not determine either answer. |
| Q75 option 4 | Retain **BとC** with an unresolved case. Other question copies have BとD. Both are wrong; B/C supplies the reservation trap but cannot prove historical identity. Correct option 2 is secure. |

Each medium edit has an exact before/current public case and a linked fixlog record. Every case gives readable source identities/hashes, actual checks, the strongest rival and the remaining limitation. The three unchanged disputes also have self-contained public records. An uncertain historical reading is not a reason to defer available checks or relabel the investigation unfinished.

Specific visual reconciliation prevented false departure records: Q44 already has a final `。` in the principal, and the science passage already prints `良い`. The toy and science target underlines exclude their final stops. Circled ①/② in the long passage and Q72 sit outside the target underline; these are restored accordingly. The long-passage notes now follow the first ベストセラー, the full 肌合いがよくて and 心地いい expressions. The final glossary stop was absent in all three inspected question copies, despite a contrary historical source claim, and is removed. Note 7 remains after 熟読, as printed; a structured alternative after している is not preferred.

The 22 principal departures cover the retained Q22 distractor; numeral/spelling variants in Q29/Q30/Q41/Q42/Q46; the corrected example labels; seven title-bracket fields; factory 言葉 and deadline; science 片付け spelling/note-anchor representation; Q67's shorter interrogative; two commas in A; the printed `右のページは` instruction; and the notice's brackets/観賞. Equivalent glyph width, blank-label linework, decorative furniture, import numbering, answer explanations and harmless reflow are excluded explicitly. Separate answer keys are supplementary information, not automatically principal departures.

## Full question and answer review

The evidence establishes 32 vocabulary questions, 12 sentence-grammar questions, five scored STAR questions and five cloze questions (54 in the schema's vocab part), followed by 21 reading questions. All 300 choices, question targets and mappings were reviewed in context. All 15 section identities and every existing item retain their order. The only new item, `vocab-b002`, is inserted before Q45 in the existing STAR section.

The two visually reviewed written grids and the aligned structured keys agree with all 75 current keys. Their repeated layout may have shared ancestry, so answer logic was checked separately. [answer_grid_verification.json](audit_work/answer_grid_verification.json) records the complete typed grid. [star_review.json](audit_work/star_review.json) verifies the five four-fragment sequences, third-slot keys and unchanged explanatory fragment order: Q45 3–1–4–2, Q46 1–4–3–2, Q47 4–2–1–3, Q48 2–4–3–1, Q49 3–1–2–4. The restored example's marked bubble also agrees with its corrected sequence.

The cloze keys 2–1–3–2–4 follow the general inference about overeating, the numerical amount, introduction of an experiment, the experimental result and the resulting explanation. The intrusive `し` seen in some copies before blank 52 cannot connect the offered choices; the principal and current `こんな【52】` are retained. Wrong usage choices remain wrong usage choices; repairs did not turn them into answers.

Reading answers were checked against full discourse: Q55 the lost pleasure of solving questions (3); Q56 pamphlets by 17 December (3); Q57 appetite-stimulation techniques (2); Q58 demands beyond a manager's own ability (1); Q59 expressing one's feelings (3); Q60 over-short explanations (2); Q61 leaving a final portion for the learner (4); Q62 adapting teaching to the recipient (3); Q63 adults' continuing attachment to toys (3); Q64 additional value beyond play (1); Q65 the ability to charge more (4); Q66 use without understanding principles (2); Q67 overemphasis on fun (4); Q68 unavoidable involvement with science (1); Q69 reconsidering one's own thoughts (1); Q70 one notebook versus separating information and thought (4); Q71 unoriginal similarity from following bestsellers (3); Q72 one favorite author's craft (2); Q73 reaching a level others will read (4).

Q74 is **A and D (4)**: a 10-year-old qualifies; A finishes at 12:45 and D's 10:45 finish plus two-hour cooling also reaches 12:45. B and C are ready after 13:00. Booking a week ahead allows D. Q75 is **B only (2)**: it makes a pendant without advance booking. C's key holder is the right kind of object but requires booking three days before, incompatible with tomorrow. A and D make tableware. The old suggestion to change Q75 to option 4 is rejected; the reply explaining the three-day rule is correct. [notice_logic_review.json](audit_work/notice_logic_review.json) records all four course-cell checks and factory deadlines.

## Legacy review and reporting limits

All **420 written candidate rows** were read: 302 reading and 118 vocabulary, including 171 previously accepted and 249 rejected rows. Listening rows were filtered out before loading. All 178 historical fixlog records were read without rewriting them. [candidate_dispositions.json](audit_work/candidate_dispositions.json) preserves each reviewed row identity and its current disposition.

The earlier source-matching changes were not assumed historically correct. V004, V032, R003, R048 and R108 are reversed provisionally for the five public decisions above. R021 remains as a documented uncertain deadline. R004's literal choice is Q60 option 4 despite its old Q62 label. R004–R009's affected complete answer sentences regain their witnessed stops. R014's shorter Q67 ending, R063/R065's science spelling and R068/R071's A-text commas are retained as real witnessed variants. R082/R085's reference numbers remain but move outside the underline. R083/R084 and R179–R186 were checked as exact note-anchor issues, not accepted from generic claims. R190's old assertion of a printed glossary stop is false. R114/R118 receive the notice fixes described above.

R130's proposed Q56 room B is not adopted: the principal, older question copy and alternative question layout all print A, while the structured transcription substitutes the nearby meeting room B. The retained A is supported by the full question-page evidence; key 3 remains unchanged. R155's proposed つよい spelling does not displace principal-supported 強い. Current すすめる, complete copulas, glossary `ここでは`, body stops and source-supported blank boundaries are retained despite weaker structured variants. Routine spacing/glyph repairs remain where context supports them. Broad confusable-character, full-size-kana and ASCII flags were checked in context and rejected where they catch legitimate Japanese, A–D/NHK labels, morpheme boundaries or deliberately wrong choices. The late curator vocabulary requests were already satisfied; acknowledgments contain no further repair.

All source quotations in public records were checked against actual page pixels or native structured locators. Native PDF extraction only guided inspection when layout mattered. No claim is made that unused duplicates, listening pages or every explanation were read. No authenticated original was found; additional copies with unknown ancestry would not by themselves settle the eight historical conflicts.

## Validation and principal assessment

The current principal's method-1 score is **113 = 100 provenance + 5 × 1 major defect + 8 uncertain fields**. Metadata flags, missing units and confirmed minor defects are zero. The sole major event is the worked-example label mapping. Each of the eight uncertain fields has its own evidence event. Source-matching provisional decisions still count as source uncertainty. Valid spellings, brackets, reflow and omissions only in the imported JSON add no source penalty. This score is a source-review index, not an authenticity probability or the quality score of the corrected output.

The staged and canonical editorial/case/fixlog checks, principal-index check and principal-departure check passed. Exact replay of the 30 new fixlog records from the frozen baseline reproduces the final JSON. Historical import metadata, all prior ledger bytes, stable IDs, option order and 75 keys are preserved. All 28 source hashes and the principal convenience copy were verified. The 80 prior catalogue entries, unrelated progress entries, previous run history, prepared queue and 20 recorded terminal skips remain unchanged.

Warnings were reviewed: `vocab-s01` is an intentional standalone heading; `vocab-b002` is the restored example; existing membership/order is unchanged except that insertion; changed options are the two public distractor decisions and six restored terminal stops, with no key or order change. There are no missing or empty playable items. [completion_verification.json](audit_work/completion_verification.json) contains the final hashes, counts, validator results and preservation checks. Investigation is terminal; proceed to **N3_12_2015** without reopening this result. Housekeeping 2, website rebuilding and publication were not executed.


Housekeeping 2: 16 previously stale public snapshots reconciled; 0 obsolete principal rows retired. [Exact before/after, source exceptions and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/prior-reconciliation/N2_12_2015/report.json). No canonical edit.
