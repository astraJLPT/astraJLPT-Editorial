# N3 December 2017 — completed audit, partial practice paper

Status: **incomplete**, with evidence investigation complete. All 74 scored written questions are playable: vocabulary 35, grammar/reading 39, 296 ordered choices, 12 sections and 9 required contexts. The original unscored STAR worked example and answer-sheet demonstration remain unrecovered. No scored question is omitted. Listening is excluded.

The current bundle contains 44 high-confidence corrections, eight current principal departures, and two unresolved public cases (inherited particle wording and missing example). No new provisional fix was applied. The principal uncertainty score is **218**, describing the source rather than the corrected output.

## Identity, evidence and actual coverage

Existing editorial content was audited directly. The frozen baseline is `audit_work/editorial_N3_12_2017.before.json`, SHA-256 `6a7450c023564b281d65683f69159d11c2aaa8ba0f3d28b651c4f95821a40ddd`. The read-only index remains SHA-256 `2a8e5154e7e8b839b55fc4b171fc5909ccb6f6fe02c4a77c531fc58db4d19ca0`. Stable IDs/order and historical import metadata are unchanged.

The selected principal is PDF 4, a compressed secondary reconstruction with advertiser cover, Chinese section labels, interleaved reading kana and no issuer chain. It is not an approved reference scan. Its cover and complete available written pages were read, including all options, instructions, references and the final table. PDF 5 was read across its complete written span as a materially different retype. Their common errors mean independence is not established. It is inferior for this paper's final instruction (`xxx`), selective readings and complete-sentence punctuation; agreement is not a vote by distributor count.

Only the following actual pages/regions were inspected. Rendering other pages does not add to this list.

| Indexed PDF | Immutable source | SHA-256 | Actual physical pages/regions |
|---|---|---|---|
| 4 | `src\Yuuki Bui\Đề thi N3 các năm Yuuki Bùi\N3 12-2017\Đề N3 12-2017.pdf` | `b4ed4b3a54a3bac91b7fadfab84998be52f6441abaec0c67cd4a6af78054f983` | 1 cover; 2–11 complete written |
| 5 | `src\日语JLPT历年真题\N3真题（2010-2026.07）\2017\2017.12\2017年12月N3.pdf` | `e95edce3b8b9aaf815e10d476dada955ea0e770d15b066a83e7c2b8aee158ec4` | 2–10 complete written |
| 1 | `src\JLPT N1-N5, Past papers\N3\N3-2017-12\N3-2017-12-真题.pdf` | `c7f3f847087e4e982d54bdf5f6ae0344107b942a220eccfe1e7cef7b26680c81` | 5 STAR transition only |
| 2 | `src\JLPT N1-N5, Past papers\N3\N3-2017-12\N3-2017-12-答案.pdf` | `bda09f820a9d5afd8f28a89593164d797b6fb33aef50513841d7aa599319f078` | 1 written answer rows only |
| 3 | `src\Yuuki Bui\Đề thi N3 các năm Yuuki Bùi\N3 12-2017\Đáp án+Script N3 12-2017.pdf` | `98a4e8e87bfe59f0d7aeccb7a5c0dca6d5103c137f1d9e72c5034fd7db096b4b` | 1 written answer rows only |
| 11 | `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N3真题\2010年-2020年\2017年12月\【1】2017年12月N3 真题.pdf` | `495733558511f443a5a88d8b3086e73733fe71f5ae058ad213f8417357cbfbee` | 5 STAR transition only |
| 13 | `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N3真题\2010年-2020年\2017年12月\【2】2017年12月N3 真题.pdf` | `c0a5f75b639f63cad298849d7bb3f92a05afe0cababb5860f9da3556cb9c6e2b` | 2, 5, 6, 9 |
| 15 | `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道二\N3历年真题\2017.12\2017年12月N3试卷_解析_听力原文_高清扫描.PDF` | `05b83f7be24ed08c8014b7ec4324b079ba8bddedfb61ceec248a3bc1dd98d7fb` | 1 cover, 2 blank, 3–7, 10–11 |
| 16 | `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道二\N3历年真题\2017.12\2017年12月真题.pdf` | `0231dc016cee455be759627b28d6f68d38d529d011fc0f26cfa5a8e1b8b89e38` | 4–5 |

Principal page map: physical 2 has vocabulary 1–15; 3 has 16–31 (partial last item); 4 completes vocabulary and starts grammar 1–4; 5 has grammar 5–16 and the STAR transition; 6 completes STAR and the cloze plus first short passage; 7 has short questions 24–26; 8 has rail notice, business-card passage and praise opening; 9 completes praise and starts cooling; 10 completes cooling/questions and introduces the last task; 11 supplies the full timetable/notice. The principal's physical pages and printed labels were kept distinct.

Additional native witness: `src/munjaJLPT/N3/2017-12_N3/2017-12_N3.json`, SHA-256 `0fba97ae61fad0a3653474b58a4cce808b0be227ca4eb4d2fec0837a9bea0adc`. Focused checks covered written section 4 usage Q32–35; section 5 Q7; complete section 6 STAR; section 7 cloze/options; section 9 praise; section 10 cooling; and section 11 table container. No complete native alignment is claimed. The written table image `2017-12_N3_s12-q01-img01.jpg`, SHA-256 `829695845ecff94bf2ea54bec87c11ea2a401e4513a368f295954bc4a9854988`, was visually read in full. It confirms schedule relationships but omits the principal's second symbol in the introduction, so both principal symbols remain.

The two answer-table pages share the same layout/body, with an overlay difference; they are not independent keys. All 74 written keys were checked against them and independently reviewed by the full item. Listening sections/images, analysis/translation files not needed to discriminate an issue, blank answer forms, score spreadsheets and classic archive fallback were not used as exam-content authority. Initial metadata handling briefly matched a shared blank-answer `pdf_1` suffix; the source was corrected by its exact indexed OCR path before any adjudication, and its metadata was removed. Five listening headings appeared in a native metadata inventory; no listening question content was reviewed or changed.

## Content decisions and unchanged anomalies

All questions, four choices, six existing explanations, nine contexts and all headings were reviewed. Vocabulary preserves intentional distractors, `受取る`, `繰返し`, and occurrence-specific 子ども/子供. The source supports plain usage headwords (Q31–35), with targets underlined in the options. Q32's target excludes auxiliary いる. Three inherited longer underlines in Q34/Q35 are directly witnessed in the bound retype physical 5 and retained as explicit principal variants; shorter principal endpoints are not automatically proven defects.

Seven grammar option marks were removed because the printed fragments lack them. Reading Q7 restores 客/きゃく and the stop after the blank. The cloze restores only source-visible selective readings (生/せい, 大/おお, 勢/ぜい, 自/じ, 由/ゆう), separates author マイヤー レア and removes word-internal extraction gaps. Q22 option 2 is `そんな部屋`, without imported が, in all inspected PDF versions and native text. No other lexical choice changes.

The stationery notice and Q26 now share the printed 間違い underline. The business-card opening is body speech, not a centered title; witnessed `話しが広がり` remains. The praise passage restores the selective 頑/がん and 張/ば on the quoted occurrence only, and includes both printed terminal stops in its reference underlines. The cooling slogan's internal stop is restored in passage and question. The retained reference-before-quotation order is directly supported by bound physical 11, while the principal passage prints the opening quote before ②; this residual variant has its own departure row. The final notice's interview subsection is bold, not underlined. Existing rich-HTML newlines remain markup whitespace; no spurious `<br>` was inserted into the table.

Twenty complete-sentence options (all four in Q25, Q27, Q30, Q31, Q32) regain the terminal stops visible in the principal. The punctuation-free retype had informed earlier removals, which are reversed. Fragment options elsewhere remain as printed. Final-table facts were checked cell by cell: seven meetings from October 30 to December 18; November 20 is closed; C's first November 6 session starts at 11:25; preparing for November 27's interview refers back to November 13. Both table answers are 2. Preserve ☆/★ and the printed `左のページ`; do not rewrite spatial wording for web placement. Blank diagonal linework can remain empty cells without semantic loss. Mixed 下さい/ください is retained as witnessed.

All keys remain unchanged. Grammar task answers were checked by construction and discourse, including family からの, 工事中ため, あと5分, 作ってみると, いただいた, なんて…だろう, company でございます, negative appearance, でしか, にしても, つけたまま, 歩きやすくて, and 帰ってきたところだ. The STAR sequences are Q14=4-2-3-1, Q15=3-4-2-1, Q16=1-3-2-4, Q17=2-1-4-3, Q18=4-2-1-3; their third-slot keys are 3,2,2,4,1. Cloze answers follow contrast, expectation, decision, place reference and qualification. Reading answers follow the naming wish, entering without waiting, three of five glues sent, car order, cookie-card misunderstanding, business introduction, effort-based praise, cooling energy savings and timetable constraints. Existing explanations remain coherent with these results.

## Candidate and historical-record review

All 151 written candidate rows were read with full affected contexts: R001–R119 and V001–V032. Listening was filtered before candidate loading. All 79 old root-ledger records were read; 78 concern written content, while legacy record 2 is a listening ビデオ repair excluded from present adjudication. Their original bytes remain untouched. Per-row decisions are in `audit_work/candidate_dispositions.jsonl`: 53 accepted decisions retained, 75 rejected decisions retained, 20 punctuation removals overturned, two decisions retained with disclosed uncertainty, and one partly overturned.

Material exceptions: R020 regains the slogan stop but keeps a separately witnessed reference order; R027/R068's 子供にも is retained with an unresolved public case, not inherited as uniquely high confidence; R031–050's option-stop deletions are reversed. R067's spatial instruction remains; its former independence claim is not adopted. R066's native 止めで is rejected. R116/V030's Q31 勤めている is in scope and correct; vague R118/V032 small-kana comments identify no actual defect. V015's native てじゅっつ and V019's expanded 難しいことではない are rejected against print. R119's 後期 field separation is retained. Decorative passage-label dots/field separators do not justify content changes. Every remaining row has an explicit disposition, with no global or unrelated candidate files consulted.

## Remaining uncertainty and coverage gap

`N3_12_2017-reading-q033-particle-order`: principal 4, retype 5 and native have malformed 子供もに. Current 子供にも is a minimal transposition with coherent additive meaning. Alternate 13 physical 9 and bound 15 physical 10 directly print 子供に, an equally grammatical rival. Full passage/choices and enlarged spans were checked. The historical presence of も is not settled; retain the existing value with an honest unresolved case and linked conjectural principal departure. No answer changes.

`N3_12_2017-gap-star-example`: the transition was checked in all seven indexed question-PDF layouts plus native STAR content. All omit the unscored worked example and demonstration. Focused web searches for the exact sitting and example returned general official samples/notices and unrelated sittings, without recovering this content; none was imported. A generic other-sitting example would not establish the historical wording. The output is therefore labelled partial practice paper despite all 74 scored questions being available.

## Principal reconciliation, score and validation

Eight departures cover three interleaved-reading repairs, three witnessed underline variants, the cooling quotation/reference boundary and the inherited particle repair. Meaningful inherited differences are included. Harmless spacing, reflow, glyph widths, advertising, linework and supplied keys/explanations are excluded. The missing example is absent from both principal and current JSON, so it is a public coverage case rather than a false textual departure.

Method 1: known reconstruction 200 + one missing block ×10 + four minor defective fields ×2 = **218**. The four fields are the three interleaved readings and malformed 子供もに; each is counted once at its highest category. No metadata flag, major defect or additional uncertain-field point is charged. The witnessed longer underline variants are not proven source defects and add zero. `principal/Đề N3 12-2017.pdf` is a byte-identical copy of the selected source, verified against its catalogue hash.

Validation passed on the exact committed bundle: `audit_work/validation_editorial.json`, `validation_principal_differences.json`, and `validation_principal_index.json`. The 12 editorial warnings concern changed option arrays: Q32 vocabulary underline endpoints; grammar Q4/6/7/8/13 punctuation; Q22's extra が; and Q25/27/30/31/32 restored stops. Each was checked against source and key text; none reorders choices or changes an answer. `canonical_replay.json` verifies all 44 exact edits reproduce the final JSON, the 86,064-byte/79-record ledger prefix is preserved, all 296 option positions and 74 keys remain, stable IDs/import metadata remain, and the final table changes only its heading emphasis.

Final editorial SHA-256: `673d131359385cb53332746cea5f5f04101f470928fc8b3b20ee0e46220beb95`. Structural consistency does not authenticate the paper or settle the two remaining historical questions. Investigation is complete; advance to N1_07_2017 under the preserved queue.


## 9 October 2026 — current practice classification

The user reclassified this output as `audited_with_uncertainty` with complete scored-question coverage (74 questions and their required contexts). Missing unscored examples remain open source-preservation cases and do not produce a partial-paper title or practice warning. Earlier incomplete/partial labels in this audit are preserved audit-time history. No editorial JSON, question, option, key, principal assessment or audit rule O5 changed; no example was supplied. See [the product follow-up](../../audit_runs/2026-10-09_star_example_classification/README.md).


Housekeeping 2: 2 previously stale public snapshots reconciled; 0 obsolete principal rows retired. [Exact before/after, source exceptions and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/prior-reconciliation/N3_12_2017/report.json). No canonical edit.
