# N2 July 2016 written-content audit

Status: **audited_with_uncertainty**. Investigation and written coverage complete on 6 October 2026. Run `2026-10-06_N1_12_2016_to_N5_07_2010`; current unit only. Listening excluded.

The final exam contains **75 scored questions (54 vocab/grammar,21 reading),300 choices,16 sections and14 content blocks including one restored worked example**. All original scored keys, option words/order, IDs, section order and source-import metadata are preserved. Twenty-nine edits comprise28 high-confidence corrections and one medium-confidence example reconstruction. Five public cases remain: one provisional fix and four unresolved variants. Nineteen current departures from the selected principal are recorded, including inherited differences. This is a complete written exam with historical uncertainty, not an authenticated issuer transcription.

## Entry preservation and identity

Existing editorial JSON was audited directly; no missing-content preflight applied. Baseline `audit_work/editorial_before.json` remains byte-identical to the entry file, SHA-256 `ca8c1301e8d58a4ffe55c0cdfefbcf04cb9ffc58623c50d84db20b8ea0f31386`. The124 historical fixlog rows (126059 bytes) were all read and preserved as an exact prefix. The index and all27 indexed original source hashes were verified again before commit. Candidates came exclusively from this unit's local file: all323 written rows, R001–224 and V001–99, were read; listening was filtered out. Original candidate statuses were121 accepted and202 rejected. Candidates, index, original sources and earlier audit history remain immutable.

Principal: `src/Yuuki Bui/Đề thi N2 các năm Yuuki Bùi/N2 7-2016/Đề N2 7-2016.pdf`; SHA-256 `2ed9b871b3d7522df462569c8aa602d41daa97767050e7f101c5435ccb62fb47`. Initial tier1 is descriptive inventory metadata. Cover and continuous question identities establish the intended N2 July2016 paper sufficiently for this unverified-source audit. The14-page copy provides a complete unsolved written body, its own STAR demonstration, coherent table and meaningful underlines. Its sharp typesetting and distributor overlay do not establish issuer authentication or prove reconstruction. The byte-identical convenience copy retains its original filename under `principal/`.

The21-page expanded copy is a materially different layout, reviewed through all available written content. It omits the example, moves the Q46 STAR to the wrong third slot, strips/changes underlines and corrupts notice details. It therefore supplies comparative evidence, not a superior authority by page count. Cover claims such as31 pages on alternate copies are not transferred as metadata penalties to the selected principal. Source21 shares the principal's body/example and errors; source0 and source17 share an inspected page body. Agreement within those pairs is not independent acquisition. The registry/digest provides no approved original source for this sitting; later approved pages cannot settle its literal variants.

## Actual evidence scope

The table distinguishes visual review, native text checks and navigation-only material. Rendered pages not actually read are explicitly excluded. Exact paths/hashes/tiers for every indexed source are also in `audit_work/source_review_coverage.json`.

|Index|Source|Inspection|Scope and limit|
|---|---|---|---|
|0|src/JLPT N1-N5, Past papers/N2/N2-2016-07/N2-2016-07-真题.pdf|visual_focused|Physical1,5,6,8,11,14,15. Cover and selected discrepancies only; Q75 option4 and full dorm notice on15. Not full review.|
|2|src/munjaJLPT/N2/2016-07_N2/2016-07_N2.json|native_complete_written|All75 questions,300 choices,12 grouped contexts. Munja order13–15 aligned by content; linked notice image is source26. External explanatory text not a complete reviewed source.|
|3|src/Yuuki Bui/Đề thi N2 các năm Yuuki Bùi/N2 7-2016/Đáp án+Script N2 7-2016.pdf|visual_key|Physical1 written answer grid only. Listening scripts excluded; same key lineage as source8.|
|4|src/Yuuki Bui/Đề thi N2 các năm Yuuki Bùi/N2 7-2016/Đề N2 7-2016.pdf|visual_complete_written|Cover1; complete written2–12. Only Q75 upper written region of12; listening remainder12/13 and ad14 excluded.|
|8|src/日语JLPT历年真题/N2真题（2010-2026.07）/2016/2016.07/2016年07月N2真题.pdf|visual_complete_written|Cover1; written2–17; written key21. Listening18–20 excluded;18 rendered only, not read.|
|15|src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/2010年-2020年/2016年7月/【1】2016年07月N2 真题.pdf|visual_focused|Physical1,5,7,10,12,13. Copy explicitly disclaims final version. Focused example/STAR, email, passage, citation and notice checks.|
|17|src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/2010年-2020年/2016年7月/【2】2016年07月N2 真题.pdf|visual_focused|Physical1,5. Page1 blank/separator; page5 body matches source0 page5. Native text elsewhere used only as navigation.|
|19|src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/2010年-2020年/2016年7月/【3】2016年07月N2 真题.pdf|visual_focused|Physical2,4,10,14,16,19. Targets, usage heading, email/dog, management, happiness and notice. Native text elsewhere navigation only.|
|21|src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道二/N2历年真题/2010-2017.12高清无水印/N2 2010.7-2017.12（真题试题）/n2 2016.7真题.pdf|visual_focused|Physical1,3,4. Matching principal body and complete example. Pages10/11 rendered but not read.|
|23|src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道二/N2历年真题/2016.07/2016.7 N2真题.docx|native_focused|OOXML zero-based paragraphs61,253,261,336,339,383. Usage instruction, sender, family dog, management, author, thought. No visual DOCX layout claim.|
|25|src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道二/N2历年真题/2016.07/2016年7月N2试卷_解析_听力原文_高清扫描.PDF|visual_focused|Physical1,3,6,8,11,12,13,14. Page14 upper notice only, listening excluded; page4 rendered but not read.|
|26|src/munjaJLPT/N2/2016-07_N2/images/2016-07_N2_s14-q01-img01.jpg|visual_complete_image|Complete dormitory-notice image. Table cells/asterisks, conditions, quoted passport pages and duplicated domain inspected.|

Unused archive fallback, listening, blank answer sheets, scoring workbook and unneeded analysis/translation files were inventoried without claiming content review. Native extraction is navigation, not proof of visual annotations. Chinese explanation agreement is not independent Japanese literal evidence. The five existing editorial STAR explanations, Q45–49, were read and agree with the reconstructed fragment orders; they remain unchanged.

## Complete content and answer review

All16 section headings,13 existing contexts,75 full stems and300 choices were read against the principal and expanded body. The source4 cover1 and written2–12 were inspected; only the upper Q75 region of12 was included. Source8 cover1, written2–17 and written-key21 were inspected. Two intentional empty sections retain the standalone 文字・語彙 and 文法 group headings. The printed 読解 label before Problem9 is restored inside its existing heading; the historical54/21 logical-part split is preserved.

Q1–10 readings/orthography, Q11–15 word formation, Q16–22 meanings, Q23–27 synonyms, Q28–32 usage, Q33–44 grammar, Q45–49 STAR, Q50–54 cloze and Q55–75 reading were reviewed as tasks, including wrong distractors. Context coverage: cloze; short notices/professionalism/email/dog/mirror; picture books, wrinkles and work creativity; clothing A/B; happiness; and the full dormitory notice, table and memo. Paragraphs, citation boundaries, notes, circled references, underline spans, table merged cells, money/date conditions and contact strings were checked.

All75 keys agree with the written grids (source3 physical1 and source8 physical21) and the content-aligned structured witness. Those two printed grids are treated as one key lineage. Munja Q13–15 records are rotated: their original positions contain redevelopment/drug/land; alignment by stems and choices yields the actual land/redevelopment/drug order. The imported choices and keys are correct; ID/index alignment alone falsely suggested miskeys. `answer_alignment.json` records all75 identities. No key was inferred from a raw position match.

STAR fragment orders are Q45=3-1-4-2 (slot2/key1), Q46=1-4-3-2 (slot2/key4), Q47=4-1-2-3 (slot3/key2), Q48=2-3-1-4 (slot3/key1), Q49=4-2-3-1 (slot3/key3). Existing explanations agree. Source8's Q46 star3 is defective; principal and other focused copies support star2. Close-ups establish that principal Q49 has all four separated slots, with STAR third. There is no missing scored question/slot to repair or score. The new worked example belongs to this exact paper's principal, not a borrowed model: option identities1テレビ/2見ている/3を/4人 give order1-3-2-4 and shaded answer2. The printed solved row mislabels its middle fragments; the coherent restoration is public and provisional.

Dormitory Q74 remains key3: Fuji meets≤30,000yen, utilities included, a private bath/toilet and arrival by April3; Sakura opens April15, Sumire prices bear the utilities-exclusion asterisk, and Tsubaki lacks private bath/toilet. Q75 remains key4: the overseas applicant must submit the application, offer-letter and passport data by February20, before arrival in March. The third-year two-year duration, all asterisks, shared table equipment cells and document③ were checked. The doubled `higashiokahigashioka` domain is repeatedly legible; it is not silently deduplicated or turned into a speculative uncertainty case.

## Changes, retained anomalies and close-up corrections

The29 append-only edits are enumerated in `audit_work/edits_staged.json` and the canonical fixlog. Repairs include the usage-task instruction 最もよい, underlined STAR instruction, printed group label, full inflected targets 衝突する and 生じている, note1 outside 真のプロ, Q56 target underline, circled reference numbers outside their target spans, and the picture-book target ending before です. Six plain contexts now preserve paragraphs/fields explicitly. 家庭犬→家族犬 and 思想→思考 restore literal readings visible in both complete copies and focused witnesses. The notice footnote loses an unwitnessed first の, passport-page delimiters return to 「」, title/intro are separated, and Q74's four conditions form a distinct memo list.

High-resolution rechecks corrected tentative inspection findings before any canonical mutation: Q7 underlines only さんしょう, with honorific ご outside, exactly as the baseline; Q49 has four slots, exactly as the baseline. Neither receives an edit, departure or defect point. The principal's actual defective Latin token is `QuAlityControQ`, application phrase `必要な種類`, and Sakura phrase `建築中ための4月15日から`. Those readings supersede earlier small-image misreadings. Source4 Q32 and Q26 full verb endings are visibly underlined. Its reading circled labels are outside the underlines. Its business-book attribution is 高田神助, not the older candidate's claimed 島田紳助.

The sender tome/tomoe, screw-tightening predicate そうだ versus emphatic 、だ, literal historical author spelling, and 下/右/次 page direction remain unresolved after focused checks. The retained forms and alternatives, exact source testimony, language/task reasoning, material investigation and residual uncertainty are self-contained in the four unresolved records. Sender name 友恵 alone cannot prove an email spelling. The predicate variants are both grammatical and leave Q66–68 playable. Page direction cannot be normalized to today's screen layout. A publisher's bibliographic fact settles the author of the book without authenticating the original exam's citation.

The exact-title [Gentosha publisher record](https://www.gentosha.co.jp/book/detail/9784344980389/) gives 島田紳助, ISBN9784344980389 and release2007-05-28. No authoritative preview of the screw-tightening passage was found. Secondary test mirrors and an unrelated dog interview were not used as independent resolution. `web_resolution.json` records those limits. No contact address was messaged.

## Legacy candidate dispositions

`audit_work/candidate_dispositions.json` contains one current disposition for every323 written candidate IDs. Reviewed routine groups are consolidated below; row status never served as evidence.

|Rows|Disposition|
|---|---|
|R001–093|Retain supported spacing/punctuation/note repairs, with subsequent underline, note and notice-delimiter changes explicitly logged. R019 email stays public. R039 circled target is corrected. R075/076 keep③ but retire the false source8 attribution. R077 keeps the witnessed doubled domain. R079/085–088/090/092 field colons are witnessed by the notice image and registered as principal variants.|
|R094–115|Keep harmless width choices, reject extra Q68 option1 period, retain colon-free Q74 memo heading. Preserve breadcrumb>, pwq/PWQ and correct note2 placement; do not add learner phonetics or email trailing punctuation.|
|R116–129|Reverse R116/117 to 家族犬 and R129 to 思考 after actual pixel review. R118/119 phonetic insertions remain rejected; preserve picture-book もたない comma and A/B widths. R123–126 cannot substantiate their claimed exam author spelling; retain publisher-confirmed 島田紳助 with explicit historical uncertainty.|
|R130–205|Broad confusable-character, small-kana and ASCII detector flags reviewed in full context; no additional supported corruption.|
|R206–224|Recheck written comments within this whole-paper audit, including Q48/49 slots, existing Q42 blank, Q26 option4破れる, Q29 option3 marking, clozeの and reading heading. R214's requested removal of stray「before知人 is already satisfied; its old reasoning confused this with valid 金曜25時 quotes. Acknowledgments and benign gaps add no evidence.|
|V001–028|Retain supported historic repairs except V007's usage instruction, now 最もよい; V016 STAR markup and V018 printed group label are explicit new edits.|
|V029–064|Reject cosmetic width/extra separator proposals. V032–43/50–52/63–64 are structured-question rotation artifacts. Q45–49 retain correct slots; V054's old source8 agreement claim was false. Preserve necessary cloze numbered labels.|
|V065–099|Broad detector flags, written comments and already-correct boundaries reviewed; no unsupported changes. V092 quote comment corresponds to R214. ロベズ name spacing and harmless gaps are retained.|

## Principal reconciliation and assessment

All19 current material departures have typed final-value snapshots in `principal_differences_N2_07_2016.jsonl`. They cover usage wording, example labels, missing 一つ, email, management predicate/Latin/name, page direction, notice issuer/labels/conjunction/punctuation/academic period/Sakura/application/deadline/selection terms, and Q74 memo punctuation. Some are inherited witnessed variants, not new repairs or confirmed source defects. Public cases link where both contracts apply. Mere HTML paragraph representation is not a principal departure.

Method1 assessment: unverified100 +3 major fields×5 +2 minor fields×2 +2 uncertain fields = **121**. There are no principal metadata or missing-unit points. Major fields are usage instruction, entire worked example, and notice content. Minor fields are the missing 一つ in an otherwise clear single-choice instruction and management passage spelling/citation. The latter also contains a predicate uncertainty, counted only once at the highest applicable category. Sender and spatial heading are the two separate uncertain fields. Repeated notice typos count once; imported underline repairs, Q7/Q49 false alarms and harmless variants add zero. The score describes the selected source, not the corrected JSON or authentication probability.

## Validation and completion

Exact replay of all29 new ledger rows from the preserved baseline reproduces the staged JSON. Historical fixlog bytes, original IDs/order, all75 keys and all300 option words/order are unchanged. The only added item is the source's own worked example. All27 source hashes match their index entries. Structural, principal-index and principal-departure validators pass. Canonical results are saved as `audit_work/validation_editorial.json`, `validation_principal_index.json`, `validation_principal_differences.json` and `completion_verification.json`.

The five structural warnings are explained: two intentional empty group-label sections, one added example ID, its section-membership change, and Q32 option underline markup. None indicates lost or reordered choices. Validation checks structure and record consistency, not historical authenticity. Every unaffected progress/catalogue entry, prior run history, prepared queue and20 DEAD skips is preserved. The next queued unit is N3_07_2016. Housekeeping2, website rebuilding/publication and reopening earlier terminal audits are outside this work.


Housekeeping 2: 20 previously stale public snapshots reconciled; 0 obsolete principal rows retired. [Exact before/after, source exceptions and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/prior-reconciliation/N2_07_2016/report.json). No canonical edit.
