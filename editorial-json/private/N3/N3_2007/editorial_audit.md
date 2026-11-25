# N3_2007 — H19 written-content audit

The first complete written-content audit recovers 105 gradable questions: 55 vocabulary, 43 grammar and seven reading questions, with 17 contexts and six worked examples in eleven sections. No prior editorial existed. The active document is authored directly in historical v3. Final fonts/defaults, diagram-grid calibration, complete/body PDFs and every-page output review remain pending.

## Evidence and scope

Principal: `src/CodexDownloads/UserApprovedReferenceScans/pdf-20074_compress.pdf`, SHA-256 `6902181b1ced1babb1aa2eb9ae4f9bc58bb96aa1780141628ff13ed7c03d03f6` (RC04_2007_L3_L4). All twenty written pages 6–15, 32–37 and 39–42 were directly read as full-page 150 dpi normalized derivatives. Original page 6 and covers 5/31 were also read. Focused small-kana/glyph rows on 6, 8 and 9 and all four clock diagrams on 40 were inspected at 300 dpi. Transformations are recorded in `audit_work/handoff19/normalized/transformations.json`; originals remain immutable. Global deskew does not remove local paper warp or establish original sheet dimensions.

Covers directly establish 2007 and old Level 3, with vocabulary 100 points/35 minutes and reading/grammar 200 points/70 minutes. December is attributed from the official JLPT guide's annual-December schedule through 2008, as recorded in preparation. It is not supplied by the year-only storage ID. Written key regions 79 (vocabulary only) and 80 (reading/grammar) were read as fallible evidence. All 105 answers agree with the authored choices and grammar/context reasoning; all six example marks agree. Scoring weights were not inferred into items.

The full review includes every instruction, question, choice, key, passage, example, target/underline, number and printed ruby. Fifteen vocabulary contexts preserve all targets and boxed references. Reading preserves a fourteen-turn alarm-clock dialogue with three circled blanks, the four-panel diagram question and a three-paragraph pet/apartment passage with its quoted underlined phrase. Both reading contexts are unframed. All six worked examples preserve the marked answer rows as tables. No missing content was found. Listening, forms and pattern page 38 are excluded. Added source folios, gutter shadows and facing-page fragments are not design features.

## Consequential comparison and principal selection

The indexed `2007年日语能力考试3级真题.pdf`, SHA-256 `42db07ed45c23df9a36d5e14fd32c50063dc18f89380dec20d0368dd08285951`, was compared through native text and full rendered pages 1–3. These are visibly jlpt.info browser-print pages with reflowed text, advertisements and a dated footer. This establishes the inspected page presentation, not upstream acquisition or issuer authenticity. No full secondary paper review is claimed.

Several consequential retype errors are directly observable. Vocabulary q2 option 1 is うてます in the scan, いてます in the retype. In q30, the source's 集まって / 隼つまって / 隼まって / 集つまって retains four distinct choices; the retype changes the fourth to 集まって, duplicating the correct choice. Q32 option 3 is 徒って, not the retype's 従って. Q34's third printed form is an altered 向-like glyph, not 伺. Other retype errors include q36 ほんとんど for ほとんど, q42 やっばり/ぶっくり for やっぱり/びっくり, q50 あさいた for あした and q51 バタン for ボタン. Source wording is retained. Inspected section starts omit the source worked examples; claims do not extend to unread secondary pages.

Eight exact small glyph crops preserve all four choices in q23 and q34, including q23 option 2's flat-topped right component and q34's deliberately altered interior strokes. Their kana suffixes remain native. The final crops were directly checked after removing stray neighboring-kana fragments from the first rough crops. Crop coordinates, source/raster hashes and final asset hashes are retained. No guessed Unicode substitute is used for a disputed stroke shape. Q4's small-kana contrast and q30's ordinary 集/隼 contrast were resolved at 300 dpi and remain native text. Only source-printed ruby is included.

Reading q47 preserves four exact source panel crops, including their printed numbers, four clocks and relative room geometry. The dialogue requires alarms ten minutes early and clocks in separate locations; panel 4 matches. The source grid is two by two in row-major order. That presentation and single ownership of each panel number are explicit pending renderer requirements in `layout_requirements.json`; generic content emission is not final layout acceptance.

The separate indexed key `2007能力考3级答案.pdf`, SHA-256 `f23b7649f9556a3258b2f2db1b12bbe15a486a914664444dec6a5f5b633737e8`, was visually read on page 1's vocabulary table and page 2's reading/grammar table. All 105 answers agree with the principal and with question reasoning; listening tables were excluded. Agreement is corroboration, not authentication or proof of independent ancestry.

The scan is chosen for observed completeness, examples, reading aids and faithful distractor distinctions, not format or newness. Its custody is unverified: principal method-1 index 100, provenance 100 and no documented content/metadata penalty. The principal copy retains exact original bytes and filename. No material unresolved content field or meaningful current principal departure remains. Empty public registers express that scoped content conclusion, not authentication. The local candidate TSV was read completely and contains only its header; candidate and source-index bytes remain unchanged.

## Validation and remaining work

Initial section fields and whole items are recorded with null before-values in the append-only unit ledger. Exact creation replay, historical v3 schema, semantic/case/fixlog checks, scoped principal validation and native content emission are required before application. The receipt binds exact outputs. Five unrelated modern catalogue mapping failures already present at H19 launch remain unchanged and separately documented.

Font investigation, cross-paper defaults, source-numbered diagram-grid rendering, final PDFs and visual/structural/size/repeatability/modern-regression checks remain H19 work. No final PDF is accepted by this content audit.


## H19 final rendering and closure — 2026-10-23 UTC

The rendering work described as pending above is complete. Font investigation, independent historical defaults, native composition and final candidate 06 validation pass. [Complete PDF](../../../pdf-render/output-h19/N3_2007.restored.pdf): 23 pages, 371,557 bytes; [body-only PDF](../../../pdf-render/diagnostics/handoff19/N3_2007.restored.body-only.pdf): 22 pages. Both outputs repeat byte for byte. Every final page has direct readable inspection or an explicitly recorded transfer from an earlier passing page with identical RGB pixels and native text. Every body page matches its complete-edition counterpart. See the [final page review](../../../pdf-render/qa/handoff19/candidate-06/N3_2007/visual_review.json) and [scoped record validation](../../audit_runs/2026-10-23_handoff19/scoped-records-06/RESULT.json).

The final historical content/configuration hash is `c312b6e6c2389e4e780af0afa5607340910fe469e405ea1694040161445f5e3b`. All 117 modern owners retain accepted H18 behavior. This is primary validation, with user review still pending. Earlier content findings and append-only evidence remain preserved; the [H19 report](../../../pdf-render/HANDOFF19_REPORT.md) records the full scope and retained 2009 limitations.
