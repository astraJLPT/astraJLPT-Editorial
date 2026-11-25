# N1_12_2020 editorial audit

Status: audited_with_uncertainty. Started 2026-09-28. Existing editorial JSON admitted directly under the current README; no content preflight applies.

## Baseline and scope

Byte-identical baseline: `audit_work/baseline_editorial_N1_12_2020.json`, SHA-256 `ca89fcc8e0e4fb84e972bd6d6842e05fd39b8d5fbec0db8b53b7cc6713a87042`. Do not overwrite on resume. Queue remains on this unit until its complete evidence review and reporting finish.

The index lists seven written-paper PDF variants with VisionOCR, separate answer/explanation PDFs, a munja native JSON transcript, and archive HTML. Listening sources, generic answer cards and scoring spreadsheets are outside content scope. Hash aliases are one witness. No principal selected yet; selection will follow inspection. Archive HTML is an absolute fallback for principal identification, not the default.

Local written candidates: 259 rows (48 historically accepted/high, 207 rejected/high, four ambiguous/medium), filtered before loading to exclude listening. Historical decisions are leads only. Priority issues: Q45 option 3 深み増やした; Q68 option 2 18/16日; factory notice missing 見学; Problem 12 起こった/怒った. Full candidate dispositions and source review remain pending.

## Checkpoint

Read current README, evidence procedure, editorial contract, principal difference contract and scoring method. Verified folder/index/editorial presence and baseline identity. Marked the existing progress entry in_progress atomically. No exam edits made yet. Next: inspect original source layouts and all written content, compare materially distinct witnesses, then audit candidates and all JSON fields with exact records.


## Evidence review checkpoint, 2026-09-28 (before new edits)

The original pages, not merely OCR, have now been visually reviewed end to end for both distinct written layouts: pdf_1 physical 6–22 (Chengdu layout) and pdf_17 physical 3–12 (clear scanned edition). This establishes 44 vocabulary/grammar questions and 24 reading questions, 68 total. All options, keys, four-slot ★ questions, cloze blanks, eleven reading blocks, notice and memo were compared to the existing editorial. pdf_17 physical 1 is the Chinese exam cover, physical 2 is blank, physical 15 is the complete answer table. The printed 30-page claim equals 32 physical pages less the cover and blank, so there is no unresolved pagination defect. No issuer authentication has been established. Candidate principal: pdf_17, SHA-256 a879307dba35b135bd32d700c929c49e042303f7fd0368f3a47ab3c2d6a21d20. Do not finalize its catalogue until the final comparison and cases are reconciled.

Additional original views: pdf_13 physical 2 right (Q1–16), 3 left (Q17–25), 9 left (Q54–57); pdf_14 physical 1 left (Q64–68) and right (Chinese explanation); pdf_9 and pdf_12 physical 1 explanations (same body); enlarged Q1 crops from pdf_6 physical 2, pdf_13 physical 2 and pdf_17 physical 3. The two-up pdf_13 is imposed: written text alternates left/right and OCR page text is not the whole physical page. Its layout/text agrees closely with pdf_17, but independence has not been demonstrated. pdf_9 and pdf_12 explanation page 1 agree and are not independent confirmations. pdf_6/pdf_11 and Chengdu variants require selected original spot checks of disputed readings before final source-family accounting.

The first thirteen sections of the munja native JSON were flattened, excluding listening. All 68 one-based keys match the current editorial and pdf_17 physical 15. Japanese reasoning likewise supports those keys. Q60 remains 2: continuing development threatens further loss; option 4 asserts the unestablished counterfactual that loss remains unavoidable even after stopping. All ★ slots and option orders remain sound. The notice calendar has 21 cells: 09h ×○○×△○×; 10h △××○×××; 14h △△○○×○△. The three people share 16th afternoon and 20th morning; the 16th afternoon has at most two places, excluding a party of three. Sunday permits a partial tour. Q68=3.

All 259 local written candidates have been read (48 formerly accepted, 207 rejected, 4 ambiguous). Historical dispositions are not authoritative. Their precise revised disposition remains to be written after edits. Written candidates and source files are unchanged. Listening rows were excluded. Existing import provenance and 84 historical fixlog rows are preserved.

Supported repair leads from original comparison: Q21 option 1 いくつもの (not いつもの); Q23 option 3 社会的信用, option 4 陸上選手 (not 上陸); Q24 option 2 収容されています (not the copied predicate 収容することができます); Q26 サービスには; cloze かないっこない (undo the old linguistically incorrect かなうっこない change), 流れ渡る, the three numbered glossary notes including 奇なり. The cloze ending が。 versus か? needs a medium-confidence disposition. Q45 option 3 深みが増した is clearly printed in pdf_17/13 and resolves the old ambiguous ungrammatical 深み増やした. Inhibition passage: 習慣ができる and 話すと自分に; restore circled underline references and glossary anchors. Teacher passage: 範型(モデル)ではない。; 心的なつながりは二次的; correct quote boundary in 「師と弟子」の場合. Q55 option 2 弟子は師に選ばれ is supported by pdf_17/13 but full conditional/particle reconstruction warrants a public provisional case. Extinction passage: 進化と分化をし; どんどん速く. Media passage: 怒った is visibly printed in pdf_17 and resolves 起こった; 日ごろ99% / 1%の異常; Q66 伝わる. Notice: 陶磁器 and missing 見学 are supported; restore note anchors. Q67 全日/前日 and Q68 18/16 need public provisional records if changed.

Material disputes to publish if still unresolved: Q1 distractors がんぽ/かんぽ (pdf_1/6) vs がんぼ/かんぼ (pdf_13/17), verified at high enlargement; neither distractor's correctness selects the historical spelling. Q8 は/が; Q22 薬/薬品; Q29 さん/氏; Q54 強まる/弱まる; media name 輪田/論田 across passage and Q63; tree sentence この連続、柔らかな透けた壁が with no secure alternate; factory notice URL differing in protocol, www and kojo/koji. Harmless spelling differences still belong in the principal differences register, even when no uncertainty case is needed. Do not invent preferred distractor forms just to match a principal.

Focused online searches were performed for the original literary passages and disputed forms (文芸の毒/かないっこ, 並木/この連続, 情報占有率/輪田/論田, 教師と生徒/心的/二次). No authenticated original passage or issuer copy was found. A 2022 Dcard learner quotation uses 論田 and 怒った but has unknown lineage; jala.tools and sachjlpt reproductions contain their own transcription problems. The online Chengdu PDF is the already-reviewed local witness, not independent corroboration. Maggie Sensei's original 2018 っこない lesson and Fuji TV's Cinderella script confirm the productive かないっこ form; they do not establish this paper's wording. No contacting a purported exam address or invented URL was attempted.

Next: inspect remaining targeted original crops and munja notice image; decide and log each edit; write public cases and exhaustive current principal departures; reconcile candidates and provenance; run validators; then copy/hash the principal and update catalogue/progress/state. No new exam edits had been applied at this checkpoint. Queue remains N1_12_2020.


## Final evidence and reconstruction findings

The complete written content review is finished. The selected principal is the 32-page clear scan (pdf_17), initially Tier 3, chosen for complete, legible written coverage and item-specific fidelity, not its tier or scan appearance. It is **unverified**, with no issuer-hosted original or documented chain of custody. The Chengdu layout was independently read across all written pages as a materially distinct comparison; different layout does not prove independent ancestry. All 68 keys, option order, four-slot starred items, shared contexts and two meaningful tables were reviewed. No scored question or necessary passage is missing. Cover administration is an explicitly reported editorial omission; this is a complete written practice reconstruction rather than a facsimile of the cover form. Listening is excluded.

Principal page map: physical 1 cover instructions/form; 2 blank (confirmed); 3 Q1–19 and the first part of Q20; 4 remainder of Q20 through Q32; 5 Q33–40 and cloze opening; 6 cloze continuation/Q41–44, Q45–47 and music opening; 7 music continuation/Q48, learning passage/Q49–51 and inhibition opening; 8 inhibition continuation/Q52–54, teacher passage/Q55–56; 9 Q57 and extinction passage/Q58–60; 10 A/B passages/Q61–62 and media opening; 11 media continuation/Q63–67 and Q68 stem/memo/option 1; 12 Q68 options 2–4 and the factory notice. Physical 15’s written answer-table cells were read separately and agree with every retained key; its listening cells were not audited.

Actual original comparison coverage: pdf_1 physical 6–22 in full; pdf_2 physical 3; pdf_6 physical 2 (including enlarged Q1), 3, 5, 7, 8, 10, 11, 12; pdf_11 physical 8; pdf_13 physical 2 right, 3 left, 5 left, 6 left, 7 left, 9 left; pdf_14 physical 1 left written Q64–68 and right explanation; pdf_15 physical 15. The Q1/Q2 diacritics, cloze last kana, 沮喪, 賑, Q22 small イ, Q41 full-size よ, first instruction’s missing の, quote ending and teacher-passage underlines were checked in enlarged crops. Some earlier working thumbnails of imposed right halves contained listening; these were rejected as wrong halves and no listening content was edited or accepted. Generated images alone are not counted as inspection.

Explanation checks: pdf_9 and pdf_12 physical 1 are matching explanatory bodies and do not settle the Q1 distractors. pdf_17 physical 18, 21 and the written part of 24 explain grammar, inhibition/teacher content and the notice’s correct answers. The separately extracted native text of pdf_16 was searched only for relevant written explanations/translation; translations were not treated as literal Japanese or authenticated historical wording. The native munja file’s first 13 sections were programmatically aligned across all 68 ordered questions and eleven text passages; the twelfth block is its notice image, which was visually inspected. All keys match. Its omitted sentence in the media passage, missing 中略, malformed 深みが増やした, selected simplified/incorrect glyphs and inherited older option clauses make it supplementary rather than a principal. The notice image shares the older omitted 見学 and URL corruption, so it is not independent support for those defects. The archived native HTML was inspected at the disputed question/choice/notice elements to trace import lineage; its content is not mistaken for later editorial corrections.

Full available source inventory and exact identities are listed below. Repeated SHA aliases are one witness. Generic answer cards, score-calculation spreadsheets, listening PDFs, advertising pages and translations of listening were excluded. The archive is not the principal because several usable original-format written witnesses exist. None of these source files, tiers, candidates or historical records was modified.

- pdf_1: `src\JLPT N1-N5, Past papers\N1\2020.12\2020年12月N1真题.pdf`; SHA-256 `e49ee9760b9affa77c560e82375a27caf1c163f1bfbd9d886a7b227e2d8d8b17`; initial tier 2.
- pdf_2: `src\JLPT N1-N5, Past papers\N1\N1答题卡.pdf`; SHA-256 `99d0ff9ea60c01b3c211c680c0c527a1604e0c91a52ece360e2873186b8dcef9`; initial tier unranked.
- pdf_6: `src\日语JLPT历年真题\N1真题（2010-2026.07）\2020\2020.12\2020年12月N1真题.pdf`; SHA-256 `31b3c46ae706fc29cf45c05d9aa85e7c7356886dc7325616aa58eb4407d49d4a`; initial tier 2.
- pdf_9: `src\日语JLPT历年真题\N1真题（2010-2026.07）\2020\2020.12\答案解析和听力原文\2020年12月N1答案解析.pdf`; SHA-256 `6d81c05f53466b411218d96f6bc562298ab7b19ada6cb70d6808a8d502aae4b9`; initial tier unranked.
- pdf_11: `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N1真题\2010年-2020年\2020年12月\【1】2020年12月N1 真题.pdf`; SHA-256 `d0f6d9000fe3d7a9503abfa8271c5db86ce8957d597d97e9793c39807621a02a`; initial tier 2.
- pdf_12: `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N1真题\2010年-2020年\2020年12月\【1】2020年12月N1答案解析+听力原文.pdf`; SHA-256 `5b364c36611a1eaebd154ae2d7c9ddaffe2a116ac4f5eb5f36e9819b44e4efdf`; initial tier unranked.
- pdf_13: `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N1真题\2010年-2020年\2020年12月\【2】2020年12月N1 真题.pdf`; SHA-256 `d69630fd29f507db18d709f9a57484e121a666ea7cba0b4411b3e5b52f8ad98e`; initial tier 1.
- pdf_14: `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N1真题\2010年-2020年\2020年12月\【2】2020年12月N1答案解析+听力原文.pdf`; SHA-256 `c70c2be3bebfa269766ce47824bdd90961a971fb4ee8ba6e7a3c2e4424831426`; initial tier unranked.
- pdf_15: `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N1真题\2010年-2020年\2020年12月\【3】2020年12月N1 真题.pdf`; SHA-256 `4798ae0f1c2878fb70b69f2499cb49c944ec2802c9004d1615ab0f356a325a0c`; initial tier 2.
- pdf_16: `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道一\日语N1真题\2010年-2020年\2020年12月\【3】2020年12月N1答案解析+听力原文+译文.pdf`; SHA-256 `0feb665b9a1f28cb19a2f0a4eb99b4153484fe6901f86f509c7f8f1a7f06878d`; initial tier unranked.
- pdf_17: `src\日语JLPT真题1992～2025.12（及时转存，避免丢失）\渠道二\N1历年真题\2020.12（7月没考）\2020年12月N1试卷_解析_听力原文_高清扫描.PDF`; SHA-256 `a879307dba35b135bd32d700c929c49e042303f7fd0368f3a47ab3c2d6a21d20`; initial tier 3.
- Native/archive witness: `src\munjaJLPT\N1\2020-12_N1\2020-12_N1.json`; SHA-256 `ebed342e37ad4f4d783b8301d2e1842474407311a1765a7c9b536a868956e3ca`.
- Native/archive witness: `src\zzClassic_ArchiveOnly De Thi Tieng Nhat\dethitiengnhat_N1\reading\N1_12_2020_reading.html`; SHA-256 `f695bb00fc0cd8c95bc06efebdd519534f24767d4952109880ab0098170cbea8`.
- Native/archive witness: `src\zzClassic_ArchiveOnly De Thi Tieng Nhat\dethitiengnhat_N1\vocab\N1_12_2020_vocab.html`; SHA-256 `6b74740adb0cd68a9f714609ac326ae8581fa19df6c2ae24692ffe1cd3da1873`.
- Native/archive witness: `src\munjaJLPT\N1\2020-12_N1\images\2020-12_N1_s13-q01-img01.jpg`; SHA-256 `3829122e5a51ce9295d9bfaaf238c09e738bfa5db5e8d76db2bc2ab8ee787ce5`.
- Native/archive witness: `src\munjaJLPT\N1\2020-12_N1\images\2020-12_N1_s13-q01-img02.jpg`; SHA-256 `153c59944e33c3091351320cba666f41b263deb573e9175a227e0ed1810bf853`.

### Reassessment of consequential decisions

The old assertion that かないっこない is malformed was wrong: the continuative stem precedes っこない. Restore that source-supported form. The newly inspected clear editions directly establish 深みが増した, 怒った, 見学, 範型(モデル) and 二次的, so former uncertainty/source-only reversions no longer justify keeping corruption. In deliberately wrong vocabulary examples, repair the incidental grammar or reversed athletics noun while preserving the tested wrong word. In contrast, ぽ/ぼ, opposing inhibition conditions and alternative connectives can all function as distractors, so Japanese correctness does not authenticate one.

A second enlarged reading supersedes an early checkpoint impression: the principal cloze ending is **か。**, not が。. The imposed edition clearly prints が?, and the older layout か?. The existing か? is retained with a public unresolved case. The suspicious small glyph in 賑やか is normal 賑, not 脈; no spurious principal defect was recorded. The first source’s teacher sentence really is 二次元的, but the principal’s 二次的 and the author’s public/private contrast support the content repair. Both statements can be true: a reproduction can legibly contain a wrong word.

The final media underline selection uses only the later occurrence, printed in the principal and the distinct 15-page layout, after the author distinguishes ordinary character from an exceptional bad day. The earlier two-underlines hybrid matched no inspected layout. The older first-occurrence placement remains a public competing reading, so this latest formatting correction is medium confidence. The surname remains unresolved and is kept consistently across passage and Q63.

Arbitrary names/diacritics/contacts were not guessed. The URL follows a fully legible source provisionally without inventing a domain suffix or testing its ownership. The 16th and 前日 repairs remain provisional because deliberately incorrect alternatives may include such inconsistencies. Full source-context attempts and strong alternatives are included in the public rows. Ordinary synonymous/spelling departures are also listed in the principal register rather than hidden by an empty uncertainty file.

The final 24 new field records are append-only in the unit-root fixlog; eight are medium-confidence corrections. There are 21 public cases (eight provisional fixes and thirteen retained uncertainties) and 52 current principal-difference rows, including inherited spelling, meaningful formatting, the corrected heading and the omitted administrative cover. The 20 uncertain score events are assessed per item/field, not by counting cases: the surname and underline share one passage field. Principal score **127 = 100 unverified + 5×1 major + 2×1 minor + 20 uncertain fields**. There are no metadata flags or missing principal written units. The major event is the unrelated subsidy heading; the minor event is the missing instruction の. Repairs that make the editorial agree with a sound principal do not count as principal defects. Source-supported additional readings are transparent departures; their absence from this edition is not by itself asserted to be a historical printing error.

Public comparison scope excludes only whitespace/reflow, equivalent slot/line width, decorative borders, imported metadata/weights, and editorial explanations. The cover instructions are explicitly recorded, not silently classified as decoration. The principal’s written answer table agrees; no separate key disagreement is invented. All original question numbers, cloze references, ★ position (third of four), notices, note definitions, selective readings and option order are retained. Restored readings are based on explicit alternate printing, not invented learner aids.

### Complete legacy candidate dispositions

All 259 local written rows were read and reconsidered. Their older accepted/rejected labels are retained in the source TSV. This table is the current disposition; `audit_work/candidate_dispositions.json` is the same coverage in structured form. Normalization-only proposals never authorize deleting labels, notes, memo cells or substantive sentences.

| Candidate | Historical | Current disposition | Decision |
|---|---|---|---|
| 2020-12-N1-R-001 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-002 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-003 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-004 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-005 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-006 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-007 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-008 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-009 | rejected | revised_medium | Q67 前日 selected provisionally; wrong group-reservation option remains wrong. |
| 2020-12-N1-R-010 | ambiguous | revised_medium | Q68 16日 selected provisionally; 18 remains a published competitor. |
| 2020-12-N1-R-011 | ambiguous | resolved_high | Missing 見学 restored from original source evidence. |
| 2020-12-N1-R-012 | rejected | retained_variant | Keep grammatical お願いします; longer polite request documented as a principal departure. |
| 2020-12-N1-R-013 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-014 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-015 | rejected | revised_high | 二次的 restored; the secondary-versus-primary relation is printed in clearer witnesses. |
| 2020-12-N1-R-016 | rejected | closed_comment | Relevant correction/key already present; thanks/noncontent comments need no edit. |
| 2020-12-N1-R-017 | rejected | closed_comment | Relevant correction/key already present; thanks/noncontent comments need no edit. |
| 2020-12-N1-R-018 | rejected | closed_comment | Relevant correction/key already present; thanks/noncontent comments need no edit. |
| 2020-12-N1-R-019 | rejected | closed_comment | Relevant correction/key already present; thanks/noncontent comments need no edit. |
| 2020-12-N1-R-020 | rejected | closed_comment | Relevant correction/key already present; thanks/noncontent comments need no edit. |
| 2020-12-N1-R-021 | rejected | closed_comment | Relevant correction/key already present; thanks/noncontent comments need no edit. |
| 2020-12-N1-R-022 | ambiguous | resolved_high | Q45 深みが増した now directly witnessed and restored. |
| 2020-12-N1-R-023 | rejected | retained_high | Keep correct ceramics-company instruction; subsidy/museum headings are misplaced. |
| 2020-12-N1-R-024 | accepted | overturned_high | Undo the earlier reversion to 二次元的; original witness plus context supports 二次的. |
| 2020-12-N1-R-025 | accepted | overturned_medium | Undo prior 全日 reversion; 前日 preferred provisionally. |
| 2020-12-N1-R-026 | accepted | overturned_medium | Undo prior 18日 reversion; 16日 preferred provisionally. |
| 2020-12-N1-R-027 | accepted | overturned_high | Undo omitted 見学 reversion; restore the tour activity. |
| 2020-12-N1-R-028 | accepted | retained_variant | お願いします is valid and retained, while principal お願いいたします is registered. |
| 2020-12-N1-R-029 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-030 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-031 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-032 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-033 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-034 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-035 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-036 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-037 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-038 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-039 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-040 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-041 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-042 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-043 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-044 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-045 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-046 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-047 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-048 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-049 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-050 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-051 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-052 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-053 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-054 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-055 | rejected | rejected_high | Pattern-only large-kana alert; the full word/particle sequence is valid in the reviewed context. |
| 2020-12-N1-R-056 | accepted | confirmed_high | Existing correction is supported by the original written pages and answer context. |
| 2020-12-N1-R-057 | ambiguous | resolved_high | 怒った is directly printed in two inspected editions; old source-absence premise no longer applies. |
| 2020-12-N1-R-058 | accepted | retained_variant | 手には is grammatical and retained; principal 手に recorded. |
| 2020-12-N1-R-059 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-060 | rejected | rejected_high | 緑をある is ungrammatical; original pages support 緑がある. |
| 2020-12-N1-R-061 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-062 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-063 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-064 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-065 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-066 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-067 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-068 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-069 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-070 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-071 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-072 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-073 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-074 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-075 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-076 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-077 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-078 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-079 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-080 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-081 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-082 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-083 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-084 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-085 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-086 | rejected | retained_uncertainty | Keep 強まる and publish the 弱まる conflict; terminal punctuation alone does not settle it. |
| 2020-12-N1-R-087 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-088 | rejected | revised_high | Original-source 直接の restored separately from the candidate’s punctuation change. |
| 2020-12-N1-R-089 | rejected | retained_variant | Keep 個別な as an equivalent inherited attributive variant; principal 個別的 recorded. |
| 2020-12-N1-R-090 | rejected | revised_medium | The defective clause is repaired to the witnessed passive; exact conditional remains uncertain. |
| 2020-12-N1-R-091 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-092 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-093 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-094 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-095 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-096 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-097 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-098 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-099 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-100 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-101 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-102 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-103 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-104 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-105 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-106 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-107 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-108 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-109 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-110 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-111 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-112 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-113 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-114 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-115 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-116 | rejected | retained_variant | Keep colloquial わかってない; principal full form recorded. |
| 2020-12-N1-R-117 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-118 | rejected | revised_high | 伝わる restored from original evidence; avoid copying the candidate’s defective verb. |
| 2020-12-N1-R-119 | rejected | retained_variant | Keep nominalized すること; principal finite する recorded. |
| 2020-12-N1-R-120 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-121 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-122 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-123 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-124 | rejected | retained_high | Retain question labels, ordered choices, and source-supported punctuation; native-transcript normalization is not evidence of a content defect. |
| 2020-12-N1-R-125 | rejected | retained_variant | Reference-period difference registered; exact referent remains clear. |
| 2020-12-N1-R-126 | rejected | restored_high | Restore circled ① in question and matching passage. |
| 2020-12-N1-R-127 | rejected | restored_high | Restore circled ② in question and matching passage. |
| 2020-12-N1-R-128 | rejected | retained_high | Keep the complete memo/table; retain あって spelling and record 合って. |
| 2020-12-N1-R-129 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-130 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-131 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-132 | rejected | rejected_high | No need to append a period to the glossary definition. |
| 2020-12-N1-R-133 | rejected | rejected_high | Preserve Japanese ニュース; 二 is a transcription artifact. |
| 2020-12-N1-R-134 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-135 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-136 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-137 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-138 | rejected | restored_high | Restore note 1 at 位相. |
| 2020-12-N1-R-139 | rejected | retained_uncertainty | 独り/一人 remains published after source and context review. |
| 2020-12-N1-R-140 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-141 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-142 | rejected | restored_high | Restore the actual note/reference or model-contrast content using the original scan, not a blind text delta. |
| 2020-12-N1-R-143 | rejected | rejected_high | Preserve Japanese 摯; simplified 挚 is not the selected source glyph. |
| 2020-12-N1-R-144 | rejected | restored_high | Restore 二次的 with the witnessed な construction. |
| 2020-12-N1-R-145 | rejected | restored_high | Restore the 昇華する note anchor. |
| 2020-12-N1-R-146 | rejected | retained_variant | 違う/異なる is a documented synonymous departure. |
| 2020-12-N1-R-147 | rejected | rejected_high | Wave-width normalization alone is unnecessary; ほとんど was independently repaired to どんどん. |
| 2020-12-N1-R-148 | rejected | restored_high | Restore the ゆりかご note anchor. |
| 2020-12-N1-R-149 | rejected | rejected_high | Principal retains a comma before 傷ついた; do not insert a sentence break. |
| 2020-12-N1-R-150 | rejected | rejected_high | Glossary definition needs no added final period. |
| 2020-12-N1-R-151 | rejected | rejected_high | Keep correct small ょ in でしょう. |
| 2020-12-N1-R-152 | rejected | retained_high | Keep the printed 中略; do not silently join omitted material. |
| 2020-12-N1-R-153 | rejected | retained_high | Principal supports inherited あふれ. |
| 2020-12-N1-R-154 | rejected | rejected_high | Keep complete もの; alternate lacks の. |
| 2020-12-N1-R-155 | rejected | retained_high | Principal supports inherited といって. |
| 2020-12-N1-R-156 | rejected | rejected_high | Keep katakana ニ in コミュニケーション. |
| 2020-12-N1-R-157 | rejected | restored_high | Restore note after 等身大の. |
| 2020-12-N1-R-158 | rejected | restored_high | Restore source-supported 奇をてら note anchor; do not copy alternate late placement. |
| 2020-12-N1-R-159 | rejected | rejected_high | Keep きつい; extra small っ has no source advantage. |
| 2020-12-N1-R-160 | rejected | retained_high | Preserve the complete printed 初対面/付き合いの浅い sentence. |
| 2020-12-N1-V-001 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-002 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-003 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-004 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-005 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-006 | accepted | overturned_medium | Restore サービスには provisionally; plain は remains a source variant. |
| 2020-12-N1-V-007 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-008 | accepted | retained_uncertainty | にあってさえ retained with a new public case for とあってさえ. |
| 2020-12-N1-V-009 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-010 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-011 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-012 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-013 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-014 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-015 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-016 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-017 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-018 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-019 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-020 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-021 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-022 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-023 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-024 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-025 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-026 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-027 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-028 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-029 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-030 | accepted | confirmed_high | Prior substantive or word-join correction remains supported by inspected original pages. |
| 2020-12-N1-V-031 | accepted | overturned_high | Restore かないっこない: continuative かない plus っこない; old morphology rationale was wrong. |
| 2020-12-N1-V-032 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-033 | rejected | retained_uncertainty | Publish ぽ/ぼ distractor conflict; answer logic cannot choose the diacritic. |
| 2020-12-N1-V-034 | rejected | retained_uncertainty | Publish the same second distractor conflict. |
| 2020-12-N1-V-035 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-036 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-037 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-038 | rejected | rejected_high | Reject duplicate final punctuation; independently select いくつもの at medium confidence. |
| 2020-12-N1-V-039 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-040 | rejected | retained_variant | Keep 見えます; principal みえます recorded. |
| 2020-12-N1-V-041 | rejected | retained_variant | Keep さし上げます; principal さしあげます recorded. |
| 2020-12-N1-V-042 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-043 | rejected | retained_high | Principal prints 起きません, matching current choice. |
| 2020-12-N1-V-044 | rejected | rejected_high | The reviewed cloze has 41–44, not 41–45; keep the four actual blanks. |
| 2020-12-N1-V-045 | rejected | retained_variant | 一週間/1週間 recorded; retain Japanese 晩 rather than native 晚. |
| 2020-12-N1-V-046 | rejected | rejected_high | Preserve 天候; alternate 天侯 is a character error. |
| 2020-12-N1-V-047 | rejected | retained_uncertainty | さん/氏 is published; no arbitrary honorific normalization. |
| 2020-12-N1-V-048 | rejected | retained_high | Principal supports kana あきらめ. |
| 2020-12-N1-V-049 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-050 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-051 | rejected | retained_variant | おしらせ/お知らせ recorded. |
| 2020-12-N1-V-052 | rejected | retained_variant | 夕べ/ゆうべ recorded. |
| 2020-12-N1-V-053 | rejected | retained_high | Principal retains Arabic 5; no wholesale switch to 五 or removal of dialogue punctuation. |
| 2020-12-N1-V-054 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-055 | rejected | retained_high | Principal has 子供; keep source-supported spelling. |
| 2020-12-N1-V-056 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-057 | rejected | retained_high | Preserve 高齢者, four slots and the third-position star. |
| 2020-12-N1-V-058 | rejected | rejected_high | Keep full name 平一明; restore its alternate-source readings rather than delete 明. |
| 2020-12-N1-V-059 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-060 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-061 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-062 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-063 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-064 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-065 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-066 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-067 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-068 | rejected | retained_variant | かた/方 recorded; no need to normalize orthography. |
| 2020-12-N1-V-069 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-070 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-071 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-072 | rejected | restored_high | Restore かないっこない; preserve the selected source-supported quote text rather than copying all punctuation deltas. |
| 2020-12-N1-V-073 | rejected | restored_high | Restore かないっこない; preserve the selected source-supported quote text rather than copying all punctuation deltas. |
| 2020-12-N1-V-074 | rejected | restored_high | Restore かないっこない; preserve the selected source-supported quote text rather than copying all punctuation deltas. |
| 2020-12-N1-V-075 | rejected | restored_high | Restore かないっこない; preserve the selected source-supported quote text rather than copying all punctuation deltas. |
| 2020-12-N1-V-076 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-077 | rejected | retained_high | Retain source-supported instructions, punctuation, four-slot layout and cloze labels; reject mere native-transcript formatting differences. |
| 2020-12-N1-V-078 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-079 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-080 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-081 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-082 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-083 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-084 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-085 | rejected | restored_high | Restore the three actual glossary notes and anchors, retaining valid cloze labels and other documented spelling variants. |
| 2020-12-N1-V-086 | rejected | retained_variant | Retain alternative 阻喪 spelling and the source-supported causative gloss やる気を失わせる. |
| 2020-12-N1-V-087 | rejected | retained_variant | Retain alternative 阻喪 spelling and the source-supported causative gloss やる気を失わせる. |
| 2020-12-N1-V-088 | rejected | retained_variant | Retain alternative 阻喪 spelling and the source-supported causative gloss やる気を失わせる. |
| 2020-12-N1-V-089 | rejected | retained_variant | Retain alternative 阻喪 spelling and the source-supported causative gloss やる気を失わせる. |
| 2020-12-N1-V-090 | rejected | retained_variant | Retain alternative 阻喪 spelling and the source-supported causative gloss やる気を失わせる. |
| 2020-12-N1-V-091 | rejected | revised_high | Large-kana trigger itself false; full review nevertheless repairs the copied dictionary-option predicate. |
| 2020-12-N1-V-092 | rejected | rejected_high | やりよう is correct; do not reduce よ. |
| 2020-12-N1-V-093 | rejected | confirmed_high | 漢字 力 and full-size よ in 力にしよう are verified. |
| 2020-12-N1-V-094 | rejected | closed_comment | Already-correct content/key or noncontent comment; no new change required. |
| 2020-12-N1-V-095 | rejected | closed_comment | Already-correct content/key or noncontent comment; no new change required. |
| 2020-12-N1-V-096 | rejected | closed_comment | Already-correct content/key or noncontent comment; no new change required. |
| 2020-12-N1-V-097 | rejected | closed_comment | Already-correct content/key or noncontent comment; no new change required. |
| 2020-12-N1-V-098 | rejected | closed_comment | Already-correct content/key or noncontent comment; no new change required. |
| 2020-12-N1-V-099 | rejected | closed_comment | Already-correct content/key or noncontent comment; no new change required. |

Historical report checkpoint: validation and terminal queue update were the only remaining unit steps. The byte-identical principal inspection copy has been created and SHA-256 verified.

## Final validation and disposition

Completed 2026-09-27T18:55:13.392959+00:00. All three documented validators passed (exit 0): validate_editorial.py with the immutable baseline, current cases/fixlog and expected vocab=44, reading=24; validate_principal_index.py; and validate_principal_differences.py N1_12_2020. Exact outputs are in audit_work/final_validator_outputs.json. The nine baseline option warnings are the reviewed, logged wording repairs: no option reordering or answer-key changes occurred. These checks establish structure and record consistency; the original-page and item-level content review is documented above.

Final editorial SHA-256: 74814948c46a1703927eff49b8aa59f0cb7889e98bb86e5f4d94badde1143927. All 68 written questions (44 vocabulary/grammar, 24 reading), 272 options and 12 context blocks are retained. Twenty-four new edits replay exactly from the immutable baseline. The public case file contains eight provisional fixes and thirteen unresolved cases; 52 meaningful principal differences are recorded. Principal uncertainty index: 127 (unverified provenance plus item-specific events), with a byte-identical inspection copy. The reconstruction remains probable rather than an authenticated official edition.

All 259 local written candidate rows have current dispositions. No required evidence work remains for this unit. Status: audited_with_uncertainty. Progress is persisted before advancing state.txt to N2_12_2020.


## Housekeeping 2 — 5 November 2026

N1_12_2020-PD-024: The selected and imposed copies both show 趣旨を踏まえて, 41–44 and 一つ選びなさい; Chengdu also uses 一つ, though it shortens the heading and writes えらび. The workbook directly attests this same instruction formula. Its own 41–45 is correct only there; the 15-page reconstruction wrongly carries 45 into this four-blank exam. Restore 一つ in this heading only.

N1_12_2020-HK1-INST-vocab-s07: Both complete reconstructions with the correct 41–44 range and the official N1 cloze use 最もよい. The school also uses よい. The four actual sets after the passage settle the range; the independently logged numeral correction supplies 一つ. Do not reapply the old 良い spelling or copy the workbook’s fifth slot.

N1_12_2020-PD-015: Prefer the selected and imposed renderings うそをつかず. There is close contextual support in this paper’s Q64 fourth choice, again about speaking honestly, where the competing sources also use うそ. Chengdu, the 15-page copy and native Q25 use 嘘, so the original glyph remains provisional. Do not touch the underline, the unnatural use of 実に, or key 3.

N1_12_2020-PD-016: Keep よくわかる. It is readable in the selected and imposed layouts. School, book and native use よく分かる; genuine N1 options also use 分からない. This supports both script forms in context, but does not justify reversing a spelling that matches the selected item. Do not repair the deliberate misuse of 実に or disturb option 3.

N1_12_2020-PD-020: The staff act for their customer; お迎えにあがります is the humble service, so choice 2 remains correct. The selected, imposed and native versions have an all-kana set, including みえます. Chengdu and the 15-page version print 見えます instead. Prefer the kana transcription of this actual option without altering the verb or making the incorrect honorific appropriate.

N1_12_2020-PD-021: This distractor is a giving verb; it cannot supply the required humble going-to-meet construction. The selected and imposed copies and the native written set have さしあげます; school and book have the mixed form. Prefer the complete internally consistent kana option set without modifying either the action or the correct answer.

N1_12_2020-PD-022: The first word locates the trip in time, not in the tested construction. The selected and imposed copies and native title use ゆうべは; Chengdu and book use 夕べは. Prefer that bounded first-word reading. The adverse wind/cold make option 3 楽しむどころではなかった the answer; retain every choice.

N1_12_2020-PD-025: Retain 阻喪 in the body and matching note. The dictionary recognizes both forms; this is not a lexical error comparable to a wrong answer. Principal and imposed have 沮, Chengdu has 阻 in both locations, the book has 阻 in its unglossed body, and native has 阻 in the body but 沮 in the gloss. The sources also split on quote closure, こめて/込めて, dates and spelling; preserve the existing notes, quote repair, four slots and かないっこない. The note count in an edition that drops 奇なり cannot locate the original note.

N1_12_2020-vocab-b001-final-question: The principal detail clearly shows か followed by 。. The imposed layout has が?; the school, 15-page version and native have interrogative か?. The rhetorical question and trailing qualification are both intelligible. Preserve the current か? and separate original punctuation from the resolved four-blank task.

N1_12_2020-PD-026: Keep the earlier 原稿をつくる and the two later kanji expressions. The selected copy also uses くわえる/つくりだす; the other exact layouts and native use 加える/作り出す/原稿を作る. Genuine N1 prose has both つくりだした and 番組を作っている, with different authors and objects. No reason to require one script for all the verbs in this passage.

N1_12_2020-PD-027: Keep 状態にあったり, which school, book and native read; the selected reconstruction says 状態があったり. The particle changes syntax, so do not infer it from a kanji/kana parallel. Keep 壁をつくったり from the selected copy against 作ったり elsewhere. Both describe the same visual effect and none of the four options requires changing it.

N1_12_2020-reading-b002-continuity: All three visual layouts and the written native passage preserve この連続、柔らかな透けた壁が. The compressed apposition makes sense in the comparison and option 3 describes its effect. No witness supplies した, and adding it would rewrite the author. Close this particular omission hypothesis; retain the separate が/に conflict in PD-027.

N1_12_2020-PD-030: Keep the applied forms matching the selected copy, including ひとつ and the auxiliary あり, without extending them to 過ごした or 見れば. The school’s vertical version mixes ひとつ with 前/今/有り; book/native also favor several other spellings. Genuine author prose supplies そのまえ and いま but is not this author. The answer concerns a change of era and culture.

N1_12_2020-PD-031: Keep the two earlier まえ spellings: they match the principal and the time reference in the passage. The other reconstructed options use 前. The selected copy also uses かわる in the first alternative, but the school, book and native read 変わる. Retain the exact option meanings; 文化がかわり and the age analogy are what make option 1 correct.

N1_12_2020-PD-034: The selected copy has 子どもたち; school, book and native have 子供たち. The July 2025 approved N1 question shows the exact plural in untested context, and another approved N1 education passage uses 子ども. That supports the earlier change without settling this author’s text. Keep 自分一人, the underlined content and the three questions; do not move punctuation or turn the plural into a universal rule.

N1_12_2020-PD-036: Retain both たとえば occurrences as printed in the selected copy. Workbook prose also has たとえば; another approved N1 author writes 例えば. The selected copy uses とりたてて and 繰り返し, whereas school/book/native support kanji in the first expression and kana in the later repeated-thought expression. Keep those independent choices and both referents instead of extending house style.

N1_12_2020-reading-b007-individual-spelling: The selected page and native title explicitly contrast 固有の独り with 偶然的な一人. This is a meaningful shift from unique identity to a member of a set and fits the argument; school and book repeat 独り in the second position. Prefer 一人 only in that second phrase. Leave the chosen-master description, the note on 煮つめられた and all three question/choice sets intact.

N1_12_2020-PD-039: Keep 煮つめられた in the body and 煮詰められた in the definition. Native actually has this mixture, the school defines the term with kanji, the selected page uses kana in both and the book drops the definition. The note is understandable and its anchor exact. The separately logged person correction does not authenticate either spelling of the gloss.

N1_12_2020-PD-041: Keep the earlier なかで. The selected copy prints that form; school/book/native have 中で. The approved career essay actually prints 産業構造のなかで, a close abstract structural use in the same level, but a different passage. It supports the inference without proving this option’s original glyphs. Keep the neighboring distractors and key 2.

N1_12_2020-PD-045: The selected reconstruction and the dated 2013 transcription of the reused 2010 item support several kana forms, including 怒ったとき, ふだん and 伝えるほうが. Chengdu/book differ; native explicitly links both years. Keep the earlier bounded changes in the passage. Preserve the distinct numbers, the employee’s provisional name and the later underline. The same prior passage is one lineage, not two independent votes.

N1_12_2020-reading-b010-name-and-underline: Keep 輪田 consistently in this paper for now. Chengdu, the 15-page version and the shared native passage have 輪; the principal and a 2013 transcription of the 2010 questions have 論. The prior date adds real evidence for the latter lineage, but the native multi-year identity means the two sittings are not independent testimony. Meaning cannot choose a surname, and no original author page or 2020 approved printing establishes it.

N1_12_2020-reading-q019-surname: Keep all five deployed occurrences consistent with the passage. The selected copy and the 2013 2010-Q66 text use 論田 five times; school/book and the shared native transcription give 輪田. Nothing in the comparison selects the glyph. Short acquaintance with three observed errors gives choice 4; a name repair would need support for the whole repeated group.

N1_12_2020-reading-b010-underline-provisional: Retain the later underlined phrase after the example about an uncharacteristically bad day. The principal and book mark this later question; the school underlines an earlier occurrence. The conclusion explicitly contrasts the usual 99% with the exceptional 1%, supporting option 3. The 2013 transcription confirms the same conclusion but does not establish the precise underline.

N1_12_2020-PD-047: Prefer the selected copy’s すなおな. The earlier dated Q67 transcription uses the same kana in the same distractor, independently of later 2020 retyping, although it belongs to the repeated item lineage. School/book/native use 素直な and genuine later N1 prose uses 素直に; there is no general rule to avoid kanji. The wrong meaning, the three alternatives and key 3 stay intact.

N1_12_2020-HK1-INST-reading-s06: Keep the ceramics-company description from Chengdu: it matches the factory tour, seven-day phone rule and actual table on the principal’s next page. Reject the principal’s grant and book’s museum. Their answer-selection formula, the approved workbook’s genuine Problem 13 and the contextual checks support 最もよい…一つ選びなさい. Q67 choice 3 is the phone/week rule; on Q68 the two-place cap rules out the 16th and Sunday has partial access, also choice 3.

Index 127 retained. The grant heading contradicts the facing ceramics notice and was already scored/recorded. Agreement on several ordinary variants neither creates a new principal defect nor settles the alternative surname, underline or cloze ending. Rechecked the existing selected source without replacing it. 7 editorial fields changed. 4 public and 15 principal snapshots rebound to pre-existing field changes; not substantive reviews.

[Before/after decisions and receipts](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N1_12_2020/disposition.json).
