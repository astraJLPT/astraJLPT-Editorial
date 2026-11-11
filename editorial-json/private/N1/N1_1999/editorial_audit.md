# N1_1999 — H19 written-content audit

Content investigation completed 24 October 2026. This is the fifth new H19 audit. Final historical font/default calibration and complete/body PDF review remain pending; content validation is not layout acceptance.

## Identity, source and coverage

The unit is the 1999 Japanese-Language Proficiency Test, old Level 1. Its year-only storage ID is retained. Sitting attribution follows the explicitly prepared admission record; the N1 prefix does not assert equivalence to the modern N1.

Principal and approved question-layout witness: `src/CodexDownloads/UserApprovedReferenceScans/日本語能力1991～1999年試験問題集1級.pdf`, SHA-256 `8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f`, registry reference `RC03_L1`. All 30 available written question pages were directly read in full: physical384–393 vocabulary and412–431 reading/grammar. Covers383/411 were inspected. Written answers were read from435 upper vocabulary table and436 reading/grammar table; these appendix regions supply fallible key evidence, not question-layout approval. Listening, scripts, forms and unrelated backmatter are excluded.

The source has65 vocabulary questions,22 reading questions and36 grammar questions:123 questions, all gradable. There are17 contexts (9 vocabulary groups,2 long passages,6 short passages),3 complete worked examples,12 task sections,69 visible ruby groups and30 inline note references. No inferred ruby was added. Repeated local question numbers are retained separately from the stable continuous IDs. The printed example choices, explanations, marked answer bubbles, underlines, double underlines and tested subparts were transcribed.

Every question page was read at150dpi. Targeted300dpi inspection covered orthography386–388 and graphic regions421/423/425/426. Eight exact PNG derivatives preserve two illustrated definitions, a four-pie-chart group, the vertical passage's inset and four diagram choices. Every saved crop was directly viewed. The source PDF remains unchanged. Page images are inspection derivatives; contact sheets served only as navigation. Modest scan skew, borders and reproduction artifacts are not historical design choices. Geometry and font comparison remain part of the later calibration phase.

## Reconstruction and substantive checks

VocabularyⅠ/Ⅲ use source-local targets underlined in their grouped sentences, with parenthesized labels beneath them. Each following item's target text and number was checked. All15 orthography choicesets were read, including deliberate wrong forms such as挿難,極厳,箇状書き and棒大な. The shared-kanji section preserves a single underline over the whole word and a second line over the tested syllables. Usage questions retain their double-underlined headword and all tested occurrences in the stem and choices. The3 examples are complete, including their explanatory paragraphs and selected bubbles4/3/4; they are not counted as scored questions.

ReadingⅠ preserves the five-paragraph numbers argument, four circled underline references and seven notes. The keys2/4/3/2/3/1/3 follow the author's distinction between units, partial daily counts, cumulative totals and the purpose of numerical claims. ReadingⅡ preserves the hobby/happiness argument, the omitted-text marker, three-item演出 list, six references and seven notes. Its keys2/1/3/4/4/2/3 follow the contrast between internal enthusiasm and performative self-deprecation; no endorsement of the passage's generalizations is implied.

Short reading1 retains the father's change, the quotationなったみたいだ, four notes and the inference that he newly notices other people's children (key3). Short2 contrasts the newer気を許せない usage with the older遠慮のいらない usage (key1). Short3's physical battery stores rotational energy before releasing electric energy (key2); itsこま and円筒形 notes retain separate illustrations. Short4 warns against excessive dictionary restrictions (key4).

Short5 retains three paragraphs, the native recycling-target table, four exact labeled pie charts and the NEDO citation. Washing-machine plastic33% and refrigerator43% establishA/B; television glass53% establishesC; the air conditioner's large metal share establishesD. Keys1 and3 are consistent with both text and charts. No data was inferred from slice size where a printed percentage exists.

Short6 retains the vertical framed passage, exterior（6）label, upright Figure2-1, horizontal citation/notes, and both occurrences of the reference②図2-2. However supports the shift away from sequential arrangements (key4). Only diagram option2 has three reasons converging onA on the left andA branching to the reasons on the right (key2). All four paired diagram panels and their printed option numbers are preserved in the private assets and current content. The final renderer must support the observed2x2 arrangement without duplicate labels and compose the passage natively with its inset.

All36 grammar items and all144 choices were checked in context, including出ようにも,からある,あるまじき,と言うなり,したところで,せざるをえない,驚くにはあたらない,をもってすれば andものを. Every printed key across the123 questions agrees with lexical, grammatical or passage/diagram reasoning. No secondary key agreement or authenticated official scoring is claimed. The appendix's90/182 raw totals and conversion statements are recorded as observed source information in `key_comparison.json`.

## Focused secondary evidence and principal choice

The indexed DOC `src/JLPT N1-N5, Past papers/N1/1999年/1999年日语能力考试1级真题及答案.doc` has SHA-256 `5d9c43c1042143dd0bc6063f7a45b359e0fe7ae337a6ef4833980482da49a27f`. Five bounded UTF16LE byte windows were inspected around簡潔,そうなん,ボブ,頭の中に and家電リサイクル. Exact offsets and text are saved in `audit_work/handoff19/secondary_doc_windows.json`; offsets are not Word page locators. This was an issue-driven text comparison, not a full secondary reading or DOC-layout review.

The DOC confirms the primary's挿難 and極限 choices, helping resolve the small scan form. It also agrees withなったみたいだ, but misprints the definition as難崖 and changes出会い to出合い. It changes several forms in the vertical passage and omitsに in一枚全部にわたって. The primary wording and visible reading aids are retained. The DOC's raw image-field URL was only observed as provenance; no URL or active document field was executed. No ancestry independence is established. Its inline circled vocabulary labels differ from the scan's parenthesized below-line markers.

Observable complete coverage, readable content, retained examples/ruby/notes and intact diagram relationships favor the collection as principal. File format, newness, registry approval and metadata alone are not quality rankings. The multi-year annotated PDF and translation/listening witnesses were not needed to resolve these issues; they have no whole-reading claim in this audit. The principal's custody remains unverified, so method1 provenance contributes100 points. No additional material source defect or unresolved ambiguity was found; current principal departures and public uncertainty registers are empty.

The unit's legacy candidate file was read in full and is header-only (zero substantive rows). Its starting hash and the read-only source-index hash are retained in `start.json`. No global candidate files were loaded.

## Records, validation and remaining rendering work

There was no prior editorial. The initial reconstruction is applied once through the guarded H19 transaction, with creation records for each section field and item, plus provenance/configuration, admission and principal-assessment entries. The private proposal and full source-to-item map remain in `audit_work/handoff19/`. An original-filename principal inspection copy is verified byte-for-byte against the canonical source.

`proposal_validation.json`, `application_receipt.json` and `post_application_validation.json` record schema, case/fixlog checks, exact creation replay, source/index preservation, scoped principal validation and native content emission. Those checks do not establish final typography. The five documented pre-existing modern principal mapping failures remain unchanged outside this audit.

The instruction's parenthesized double-rule sample exposed an answer-blank classification error. The bounded historical-only emitter correction preserves that explicitly marked sample, while ordinary brackets and modern rejection behavior remain intact. `current_renderer_tests.json` records52 passing tests; the H19 modern comparison `pdf-render/evidence/handoff19/n1-1999-underline-sample/` verifies all117 emitted bodies and3,431 protected artifacts against the accepted baseline. Four original H17 live-state test assumptions no longer match authorized H19 output paths, the reconciled N3_2009 source or its identity validator exception type. Their initial failures remain recorded; current replacement assertions preserve the same admission, marker, content and isolation checks. The frozen H17 tests were not rewritten.

`layout_requirements.json` records unresolved implementation work, not unresolved exam content: unboxed below-line target groups; restarted local labels and問/【問い】families; paired illustrated notes; native table/chart association; a native vertical frame with upright inset and horizontal trailer; and source-numbered2x2 diagram choices. Font investigation, independent reusable historical defaults, final complete/body PDFs, readable every-page inspection, repeatability and modern regression verification are still required by H19.


## H19 final rendering and closure — 2026-10-23 UTC

The rendering work described as pending above is complete. Font investigation, independent historical defaults, native composition and final candidate 06 validation pass. [Complete PDF](../../../pdf-render/output-h19/N1_1999.restored.pdf): 36 pages, 583,271 bytes; [body-only PDF](../../../pdf-render/diagnostics/handoff19/N1_1999.restored.body-only.pdf): 35 pages. Both outputs repeat byte for byte. Every final page has direct readable inspection or an explicitly recorded transfer from an earlier passing page with identical RGB pixels and native text. Every body page matches its complete-edition counterpart. See the [final page review](../../../pdf-render/qa/handoff19/candidate-06/N1_1999/visual_review.json) and [scoped record validation](../../audit_runs/2026-10-23_handoff19/scoped-records-06/RESULT.json).

The final historical content/configuration hash is `80b1d88ee24f8c6064616256300e7eb6a2f2bdc64b92963f1f3f7738ae1c9861`. All 117 modern owners retain accepted H18 behavior. This is primary validation, with user review still pending. Earlier content findings and append-only evidence remain preserved; the [H19 report](../../../pdf-render/HANDOFF19_REPORT.md) records the full scope and retained 2009 limitations.
