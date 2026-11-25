# N1_12_2009 — H17 written-content audit

**Current status: investigation complete; body and complete edition accepted with disclosed uncertainty.** All available scored questions recovered; reading question 8 remains ungraded because of a key/reasoning conflict.

**Earlier presentation-stage status, superseded on 23 October 2026:** Status: **written-content investigation complete with disclosed uncertainty; body accepted; complete edition pending H17-STYLE-003**. H17 remains in progress. The earlier in-progress audit is preserved at `audit_work/handoff17/editorial_audit_before_body_acceptance.md`.

The prepared 35-file baseline and all 17 indexed source paths were verified at launch. No source or source index was changed. No editorial existed at entry. The original empty fixlog and case register remain in the prepared baseline. The local candidate TSV was read completely and contains only its header.

## Historical identity and admission

The compilation's physical page 11 titles the paper December 2009 Japanese Language Proficiency Test **1級**. Five consecutive complete vocabulary questions 1–5, all choices and their shared contexts passed admission. The N1 storage prefix is retained and does not establish equivalence to revised N1.

The selected principal is `src/JLPT N1-N5, Past papers/N1/1995-2009.12日本语能力测试真题详解N1.pdf`, SHA-256 `e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00`. It is a Tier 3 secondary reprint with unverified provenance, not an authenticated issuer copy or approved original-style scan. The copy in `principal/` is byte-identical.

## Evidence actually reviewed

Complete principal page images were viewed at physical 11–15, 18–34 and 36–45. Vocabulary occupies 11–14 and upper 15; reading/grammar begins below listening on 18 and ends above keys on 29. Written keys occupy parts of 29–30. Vocabulary explanations run from lower 30 through upper 34; reading/grammar explanations start below listening on 36 and end at the first line of 45. Physical 35 and all mixed listening regions are excluded. Printed pagination is physical minus ten. Detailed close views resolved small characters, target positions, double underlines and chart labels.

The materially distinct written DOC, SHA-256 `cc329e81d436d96d75c25db0ac89033d9d42c34f6cdb7daa4c9463b7054ef3cc`, was read in native text and all 16 pages of a byte-identical inspection copy's LibreOffice 26.2.4.2 rendering. Derived pagination is not intrinsic DOC pagination; stable locators are headings, question labels and paragraphs. The import contained zero images or embedded objects and one textbox; neither native inspection nor the complete rendering recovered a chart. The DOC supplies a worked example missing from the principal. Its independence and authenticity are unestablished. The indexed listening DOCX is outside written scope.

The official statistics report at https://www.stat.go.jp/data/kagaku/kekka/kekkagai/pdf/19ke_gai.pdf was downloaded and visually inspected at physical 7, 18, 30 and 37 (tables 5, 14, 25 and 34). SHA-256: `c81b739c32d70cac8e3ad23801836ab4607e3a8062d02b29f650d5a7e9cf7389`. It supports all twelve FY2006 percentages, including replacements 74.8, 32.3 and 8.8 for defective reprint labels. It does not authenticate the passage's retained 2008 survey-year statement. The publisher catalogue https://www.kodansha.co.jp/book/products/0000147287 independently confirms `他人を見下す若者たち`, ISBN 9784061498273, by 速水敏彦. The Nakamura newspaper citation date remains unresolved.

## Current editorial and audit decisions

The sole active `editorial_N1_12_2009.json` uses schema 3.8.0 and the bounded `pre-2010-2009` historical branch. Its SHA-256 is `debc9511b49db3e91567d97a38648feb896d2d0640245a7679f2e8cbc970066d`.

It contains 13 sections, 65 vocabulary questions and 59 reading/grammar questions, 20 shared contexts and one worked example: 145 items total. Every question has four options. There are 123 gradable questions; reading question 8 deliberately has a null key. Forty-four source-supported ruby groups are preserved and no inferred ruby is added. Old section order, instructions, source-supported local labels, boxed target numbers, underlines, double underlines and note associations are retained. No modern timing, scoring or STAR templates are invented.

All 124 questions have independent answer-logic review and source/key locators in `audit_work/handoff17/item_review_coverage.json`. The live [fixlog](fixlog_N1_12_2009.jsonl) has 189 granular creation/repair records. The [public cases](unresolved_cases_N1_12_2009.jsonl) contain 11 provisional fixes and 20 unresolved cases. Nineteen current [principal departures](principal_differences_N1_12_2009.jsonl) disclose adopted differences.

Material decisions include the DOC-supported worked vocabulary example, question 39's tested syllable, incidental particle/word repairs, reading note 3's attachment, the publisher-supported book title, the leisure passage's missing connectors and the three chart percentages. The user-approved placement changes `右のグラフ` to `次のグラフ`. Every adopted content change has its own evidence and ledger entry; approval of layout is not approval of numbers or source authenticity.

Historical distractor variants remain explicit: sparse single-character choices in vocabulary 32, `衡点` in 35, variant wrong uses in 61–65 and several competing grammar choices are not normalized for naturalness. Principal vocabulary keys 50/54/56 (3/2/2) are supported by lexical reasoning and explanations despite different DOC keys. Reading question 8 is ungraded because both local answer lists and the reprint explanation favor 3, while the passage's reciprocal social/design influence supports 1. Agreement between derivative witnesses does not settle that conflict. Retained 1980/year-decade wording, the 2008/2006 dates, and grammar 29's 開店/閉店 concern remain public uncertainties.

The principal assessment is complete for all available written material: provenance 100 + one missing unit ×10 + two major defects ×5 + ten minor defects ×2 + twenty uncertain fields = **160**. Coupled defects in one field are counted once, using the highest applicable category. See `audit_work/handoff17/principal_assessment.json` and the appended entry in `preprocess/principal_uncertainty_index.json`. Prior catalogue entries were preserved.

## Validation and native rendering

Content structure, all public cases, append-only fixlog records, the current principal assessment and principal departures pass. The known null key is the only content warning. Full schema validation and native composition pass directly from the current editorial and historical defaults. Existing content-validator reuse uses an in-memory audit projection only; runtime builds do not reconstruct v2 or replay a fixlog.

The 37-page native body is **618,973 bytes**, SHA-256 `3e89f26a64cdf6f09271946b4d8d59927061e25f6e3083b7c11fe1aa2b5db337`. All pages and continuations were directly inspected using Poppler, with enlarged details where needed. A first-trial group separation was repaired. Final chart labels are clear of outlines; the other 36 final raster pages are byte-identical to their reviewed pages. Machine checks report zero missing glyphs, lost/extra Japanese characters, overfull boxes, blank pages, unsafe bounds or footer collisions. All fonts are embedded and there are zero raster image resources. Charts are native vectors with searchable text.

The body repeats byte-for-byte. Thirty-seven targeted tests passed, including seventeen new historical contract tests; all seventeen historical tests passed again after the final chart adjustment. The 117 H16 owners retain identical generated TeX, editorials, sealed PDFs, profiles and preservation records. See [body acceptance](../../../pdf-render/qa/handoff17/N1_12_2009/BODY_ACCEPTANCE.json), [visual review](../../../pdf-render/qa/handoff17/N1_12_2009/visual_review.json), and [H16 regression](../../../pdf-render/evidence/handoff17/H16_REGRESSION.json).

The global principal catalogue already failed `Stale source-to-unit mapping` before the H17 addition. The same pre-existing failure remains; this unit's entry and departures pass separately. Whole-catalogue success is not claimed, and unrelated historical entries were not silently repaired.

## Remaining work

**Earlier presentation-stage status, superseded on 23 October 2026:** H17-STYLE-001 (groups/markers with H16 typography) and H17-STYLE-002 (charts below with the following graph) are approved. H17-STYLE-003, editorial title page versus starting with questions, remains unanswered. The file currently in `output-h17/` is a body-only candidate, not a final complete-edition release. Complete-edition assembly, its visual/repeat checks, and final H17 index/manifest/report wait for the relevant work and decision. Continue independent evidence investigation in the exact six-paper queue; no final H17 acceptance is claimed.


## Final H17 acceptance

Accepted 23 October 2026: **38 complete pages**, one approved editorial title plus 37 body pages; **651,058 bytes**. Every new page was directly inspected. All assembled body pages match the reviewed pages pixel for pixel and text for text. Complete/body PDFs, generated TeX and editorial repeat byte-identically. Fonts, glyphs, text, overflow, bounds, footers and blank-page checks pass.

Current editorial SHA-256: `debc9511b49db3e91567d97a38648feb896d2d0640245a7679f2e8cbc970066d`. Complete PDF SHA-256: `346e5ff0275c7875342996a7185d1770a9edbcb71e49bdff1295c78767887cdc`. [Complete acceptance](../../../pdf-render/qa/handoff17/N1_12_2009/COMPLETE_ACCEPTANCE.json) · [Final-page review](../../../pdf-render/qa/handoff17/N1_12_2009/complete_visual_review.json) · [Repeatability](../../../pdf-render/qa/handoff17/N1_12_2009/complete-repeatability.json). The final package has 31 passing historical tests and 117 modern regression checks against accepted H18; frozen H16 is preserved. Earlier presentation-stage status and test counts above are retained as history. Level 4 now has 114 content records plus one approved-presentation record. No inferred ruby or original-exam authenticity is claimed.

H23 written-case reconciliation (26 October 2026): current values, alternatives and source testimony were reassessed. Reporting corrections and any narrow evidence-supported closures are recorded in [W01 dispositions](../../../pdf-render/evidence/handoff23/existing-cases/reconciliation-01/DISPOSITIONS.json). Exact previous records and edits are preserved alongside that receipt. No canonical content, answer key, ledger prefix or listening row changed in this reconciliation. Remaining written uncertainty and partial coverage are retained for their stated evidence reasons.
