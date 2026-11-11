# N2_12_2018 editorial audit

Status: **audited_with_uncertainty**. Completed 2026-09-28. Full written practice paper: **73 questions, 292 choices, 12 content blocks, 14 sections; no null keys or omitted scored questions**. Vocabulary/grammar contains52 questions; reading contains21. Listening is excluded.

## Identity, baseline and sources

Existing editorial JSON was admitted directly, without a content preflight. The byte-exact baseline remains in `audit_work/baseline_editorial_N2_12_2018.json`: `25dda0abb3a1e74faf76041606b626370ffeacac00d4220fc61d79e88e7dd145`. Read-only index SHA-256: `020bf3e165360a9826ddcdd28def41ea032d217f92e8032805c487830381fb3d`. All112 historical root-ledger rows were read; the retained byte prefix hashes to `c7e9e21ba1ebe424d38500aedf6d8247ae894e015acb2bb6998b1b1754ae2d6b`. Imported source metadata is unchanged. Original source files and historical candidate/legacy notes were not edited.

The selected principal is the32-page book scan, indexed **pdf_18**, `2018年12月N2试卷_解析_听力原文_高清扫描.PDF`, SHA-256 `78b000e2749306778804545093a8d989b5e220f892f03989b460eeb45a40f712`. Its source path is recorded in the catalogue and the exact18-record source inventory at `audit_work/source_inventory.json`. A byte-identical inspection copy is in `principal/`. Selection followed the content comparison, not its tier or a claim of authenticity. It contains the complete written questions, tables and associated written key/explanations in a readable layout. Its cover/page arithmetic is coherent: cover plus blank separator and30 numbered content pages. Acquisition remains **unverified**.

Actual original-page inspection (physical, one-based; rendered but unread pages are not included):

| Indexed witness | Actually inspected scope and purpose |
|---|---|
| pdf_18, principal | pp1–13; written upper p14; written key upper p16; written explanations pp17–24 and upper p25. p2 is the blank separator. Full question/passage/formatting comparison; Q27 key, Q60 rationale, names, dates, notice. Listening portions of mixed pages excluded. |
| pdf_3, school Final Version,16pp | pp1–14, complete written comparison. p1 metadata; pp2–6 vocabulary/grammar/cloze; pp6–14 reading and notice. pp15–16 listening excluded. |
| pdf_1,14pp | pp1–5,7,9,11,12. Identity, Q7/underlines/grammar, bag/athlete/coach, knowledge passage, evolution and complete notice/Q73. |
| pdf_6,16pp | pp1,2,6,7,8,12,13. Distinct lower-fidelity transcription, including 介種, shorter mail reference, before-word notes, name, coaching text and しあさって. |
| pdf_12,16pp | pp1–2. Wrapper and opening question body matching pdf_6 on inspected p2, including 介種 and misplaced section boundary. |
| pdf_14,17pp | pp1,2,7,11. Wrapper and school question bodies matching pdf_3 on inspected pages; mail/name and full A/B instruction. |
| pdf_16,23pp | pp1,2,8,9,14,18. 介種; mail46955841 without ご; clipped bag box; abridged generic A/B instruction; clear しあさって（出発日の3日前）. Clipped name not treated as readable evidence. |
| pdf_2,10pp answers | Written key on p1 and vocabulary explanations p2. All73 written keys agree with retained answers, including27=4 and60=4. |
| pdf_5, one-page school key | Written portion of p1. Q60=1 conflicts with the passage and other keys; all other written answers agree, including27=4. Listening grid excluded. |
| pdf_9 / pdf_13 | Original p1 of each. Same inspected explanation page body; Q7 explains correct 介護 and alternate 看護 but not the wrong third glyph. |
| pdf_15 | pp1–2, Q1–22 explanations. No discriminating wrong-option kanji for Q7. |
| pdf_10 | Original p2. Translation confirms repair reference46955841 and retains selective 探/索・有/益 gloss readings. Other rendered pages not claimed read. |
| pdf_17 | pp14,19. Chinese reading translations: mail46955841, sender铃木洋一 and あさって/three-days-before equivalent. Translation is secondary evidence, not original Japanese testimony. |
| DOCX explanation | Read-only XML body paragraphs26–45 and367–382, including Q7 and Q60. OCR-corrupt Japanese was not treated as reliable glyph evidence. No DOCX layout/furigana claim; no rendering or authoring. |
| Native structured JSON | First14 written sections: all73 leaf question comparisons and11 parent passage comparisons. Native written keys all agree. Full canonical explanations were reviewed; no claim that every native explanation was independently read. Native listening excluded. |
| Native/archived notice images | Whole indexed notice images actually viewed. Table amounts and conditions agree; native image has visible15甘間 corruption and circled headings, not adopted. Archived image is supplementary, not principal. |

All18 inventory SHA-256 values were verified again after editing. Initial tier guided discovery only. School copies share inspected bodies; pdf_6/pdf_12 likewise share an opening body. Distinct typesetting is not proof of independent acquisition. Book and school covers have different metadata; school cover’s180-minute/30-page claim does not describe its16-page file. These school flags are not scored as principal defects. Pure listening sources pdf_4/7/8, native listening, shared score workbook and answer-card material were excluded. Archive HTML fallback was unnecessary because usable alternative principals existed; no working HTML, global candidate file, site or tool was changed.

## Complete content review

Read all14 canonical sections, all73 stems, all292 choices, all12 blocks, every key and existing canonical explanation. Compared the principal’s complete written content with the complete school witness, then focused distinct question layouts, native text and explanations on conflicts. OCR/native extraction supplied leads; quoted source readings and meaningful underlines/readings/table cells were checked on originals.

Principal coverage: p3 Q1–17; p4 Q18–30; p5 Q31–43; p6 Q44–52 and origami column; p7 Q53–55; p8 bag/athlete/coach opening; p9 coach ending/Q58–60/personality opening; p10 personality ending/Q61–63/knowledge; p11 Q64–66/A–B opening; p12 Q67 ending/Q68/evolution; p13 Q69–73/notice opening; written p14 notice ending. All42 ordinary language questions, five four-slot ★ questions (43–47) and five cloze blanks (48–52) were reconciled in their order:42 +5 +5 =52. Reading has21 questions and11 context blocks. No missing passage or empty choice remains.

Answer reasoning included lexical fit, particles and inflection, collocations, complete ★ assembly, cloze discourse, passage reference/contrast and every reading distractor. All73 keys remain unchanged. Two source-key conflicts were resolved explicitly:

- **Q27 鈍い:** principal key3 and its p18 explanation are wrong. 仕事が鈍い is not the appropriate collocation here; 動きが鈍い in choice4 is. The other keys and native transcript give4. Preserve the deliberate bad alternatives; score one principal major defect.
- **Q60:** the separate school key gives1, while the passage stresses a coach’s reflection on **みずから** and anticipating what scolding conveys. Choice1 replaces self-reflection with facing the child. Choice4 fits; repetitive scolding in2/3 is expressly warned against. Principal,10-page key and DOCX explanation give4. The separate-key error adds no principal defect.

Q55’s native option reordering was rejected; current book/school order and key1 are preserved. Q56’s uninterrupted physical-shop sales make choice1 correct. Q72: light zipper model, at least60L ⇒ M64L; ten days uses15-day bracket ⇒4000円, choice3. Q73: online deadline already passed; telephone application by five days before departure at13:00 meets three-days-before delivery ⇒choice3. Choice4 remains too late even after provisional しあさって repair. All18 rate values, capacities50/64/81L, period bands7/15/30, free return shipping, travel-only billing, dispatch/pickup example, phone041-369-2500, business hours and application/delivery cutoffs were cross-checked against the original notice and images.

High-resolution review preserved Q4 underline **和やか** only and all four Q30 underlines on **乗り継いで/乗り継ぐ** only; early impressions of longer spans were rejected. Principal/school both print **意思**, so no speculative 意志 change was made. Before-word notes are positively supported by pdf_6 and were retained as source variants, with principal post-word placement disclosed.

## Edits, cases and candidate dispositions

**38 granular ledger edits:29 high-confidence and9 provisional.** High-confidence corrections restore Q9/Q24 underlines, cloze48–52 numbering and question labels, the full A/B instruction and block separation,16 option-final stops, remove artificial underlines, and recover the full semantic rental notice/tables. The coaching field combines independently certain underline/sentence-boundary repairs with provisional selective reading aids. The photograph of three suitcases is decorative; all task-bearing information is represented in text/table markup.

Nine current public provisional fields record exact before/current values, readable evidence, alternatives, focused attempts and residual uncertainty:

1. Q7 third choice **介穫**, versus attested介種; key2 unchanged.
2. Repair email **46955841 / ご確認**, versus shorter695581 and unprefixed確認.
3. Bag-shop signer **鈴本洋一**, versus native/translation鈴木洋一; key1 unchanged.
4. Q73 choice4 **しあさって（出発日の3日前）**, versus the widespread anomalousあさって branch and alternative changing the parenthetical numeral.
5. First-passage gloss readings on 探/索 and 有/益 only.
6. Exactly three coaching **叱/しか** aids, with no extra readings on other occurrences.
7–8. Q57 choices3–4 **捉/とら**.
9. Q61 choice1 **勘/かん**, moving the already inherited reading into ruby and disclosing historical-presence uncertainty.

Names/digits and wrong-option glyphs cannot be proven by naturalness or copy counts. Reading aids may have been added by the reproducer. Medium choices are useful preferred reconstructions, not authenticated exam claims. No unresolved playable-content gap or null key remains. All cases are self-contained, with no private candidate/fixlog references.

All406 written candidate rows (R001–R310, V001–V096) were read, including rejected and accepted rows; truncations were recovered during review. `audit_work/candidate_dispositions.jsonl` has one current disposition per row. Historical112 ledger rows were also independently read. Key reversals/reassessments: R019/R106 full A/B introduction; V025介穫; R226–228 email; R235–237 selective readings; R250 sentence stop; V047–051/V091–096 complete cloze numbering; R086–089/R102–105/R113–116/R122–124/V031 printed stops. Earlier signer change to鈴木 is reversed provisionally. R230 title の and all source-supported before-word notes remain, with departures disclosed. Fragment detectors are rejected after context review; metadata/comment text stays private, while substantive key claims were tested.

Native corruption was not copied wholesale: retain 飛び立って, してみる, コンピュータ, 患者数は, わかりました and nested『ザイオンス効果』; reject unrelated children’s-magazine introduction, 届た, omission of社会としては, extraし inお願い申し上げます, だったのが, 性格を欠点, 腹を立つ, 慣れていないうち, 若いごろ and altered A/B choice3 消極的. Native orthographic alternatives do not override clear printed 子ども/ふつう/生きかた/生きもの.

## Principal reconciliation and assessment

**41 current principal differences** cover inherited heading colons, Q22 underline, 濡れた, dialogue punctuation, school-only cloze introduction, note-anchor positions/athlete note numbering, retained title の, selective reading aids, inherited option punctuation, Q73 day word, the confirmed Q27 key/AB comma repairs, and omitted cover administration/title blocks. Cover instructions and registration fields are candidly recorded as editorial omissions, not hidden as decoration. IDs/import metadata, auxiliary explanations and archive scoring weights are not exam-source departures. Harmless reflow/spacing and equivalent-width glyphs are excluded.

Principal method1 assessment: **100 +5×1 +2×1 +9 =116**. Unverified provenance100; metadata0; missing scored units0; major1 (Q27 key); minor1 (A passage 考え方、が); uncertain fields9, counted once per affected item/field. Ordinary source-supported formatting/orthographic variants are not automatically scored as material uncertainty. The school Q60 error belongs to a separate key. No source is authenticated by this score.

## Validation and final state

All three required validators passed. `audit_work/validation.json` records commands and results, exact ledger replay, immutable checks and principal-copy hash. The full38-edit replay from the byte-exact baseline equals the final JSON; the112-row ledger prefix and all18 source hashes/index are unchanged. No key or option order changed. Ruby bases and three selective coaching positions, all five four-slot ★ items, five cloze labels, two4-column tables with18 rates, every complete context and72/73 answer logic were checked.

Nine structural warnings are expected option-value edits: Q7 glyph, Q29 stop, Q54 stops, Q57 readings, Q61 reading, Q65 stops, Q69 stops, Q71 stops and Q73 day word. All preserve four choices, their order and key mapping. The first principal-difference validator run rejected typed evidence summaries; these were serialized as readable strings while typed current values remained exact, then the validator passed. Structural success does not authenticate historical wording.

Final editorial SHA-256: **e55270ca46f632b87f50657021d426bb81ca4869831faa29850259553cb956e4**. Progress was updated only after this completion record and all checks; queue advances to N3_12_2018. Earlier checkpoints are retained privately in `audit_work/checkpoint_before_final.md`.


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 4 maintained fields / 5 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N2_12_2018-DW20261013-001 through N2_12_2018-DW20261013-004 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.


## Housekeeping 2 — 5 November 2026

Apply only 濡れた→ぬれた in Q40. Both fully inspected exact-item layouts print kana and the expanded approved historical comparison uses the same wet-state verb incidentally in a grammar question. The blank still tests ままにせず, not kanji recognition; all four options and key 1 remain intact. The older 2級 example is not a fixed modern-N2 policy and the two 2018 layouts have unestablished independence. Use medium confidence and retain historical uncertainty rather than treating agreement as issuer authentication. The principal departure for this fragment becomes obsolete after the change.

The full hair-care sentence instructs the reader to dry washed hair thoroughly instead of leaving it wet. ままにせず completes that contrast; the other three complete choices do not, so key 1 and all grammatical boundaries are preserved. Both exact inspected reproductions print ぬれた, while the inherited editorial has 濡れた. The verb is incidental lexical content, not a tested kanji reading or spelling target. The newly inspected approved 1991 old-2級 grammar question uses ぬれて in an incidental wet-state clause after lending an umbrella; its reason blank takes ものだから (3). This is a same-lexeme/function comparison, stronger than the previous lack of a parallel, but its older era and approximate level correspondence limit transfer. The exact 2018 witnesses carry the decision; the historical example corroborates kana viability rather than imposing a level rule. No empty text extraction or missing occurrence elsewhere is treated as evidence against the kanji form.

One editorial field changed, with an exact field-map and current-scope binding update. No ruby annotation occupies that field; all current/frozen ruby bytes remain unchanged. One older case snapshot and three principal snapshots were rebound only to existing parentheses. Principal score 116 is unchanged.

[Before/after decisions, evidence and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N2_12_2018/disposition.json).
