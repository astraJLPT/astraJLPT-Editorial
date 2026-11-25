# N3_07_2019 editorial audit

Status: in_progress. Existing editorial admitted directly; no content preflight. Listening excluded.

Byte-exact baseline: audit_work/baseline_editorial_N3_07_2019.json; SHA 3587c63ffdc0966d3ff45d4fdef914ffc7cc8c643618cc3b94dad2c23dcc88eb. Index SHA 789e9253fcd301b82fff13653a2fac8b0cd6b636db4e730c582697f8265bb331. Full current index read. Candidate/log isolation done, not yet fully read. No canonical edits. Original-page/full-content comparison pending.

## Resume checkpoint: completed review before canonical edits

The complete canonical 74 questions (296 options), 12 headings and 9 blocks have been read. All 312 written candidate rows and all 46 written historical ledger records reviewed; the root ledger contains 73 total records including 27 listening records, all to be preserved. No canonical edits yet.

Actual original visual coverage: pdf_3 physical 1–12 (complete available written principal); pdf_1 1–4 (same scan family, branded derivative); pdf_6 2–10 and written keys on 13 (materially distinct reconstruction, full written coverage); pdf_14 2–3; pdf_16 3–12 and upper written notice on 13, written key table 15, explanations 19–21; pdf_5 written key table 1; pdf_2 1–3. Rendered other pages are not yet claimed as reviewed. Native JSON first twelve written sections read fully; its Q25 is an unrelated garbage-collection notice and must not replace the printed white-box passage. Source identities and hashes are in audit_work/source_inventory.json. The twelve useful PDFs, native JSON and native notice image were hashed. Listening excluded throughout.

The scan pdf_3 supplies complete grammar questions 1–13 lost/paraphrased in the poorer pdf_6/native lineage. Restoring its options requires reading keys 9=4 and 13=3; all other written keys align with the scan's companion key and book key. Its vocabulary order matches the editorial order; the poorer reconstruction uses different vocabulary order while retaining keys for the scan order. Do not transfer its answer numbers blindly.

Pending focused decisions: vocabulary 1 missing も, q4/q6 reading distractors, q12 買いました/買いたいです, q13 裏測/内測 distractors, q18 いろいろな…人だ, q19 引っ越して/引っ越しして, q21 行けなく/行かなく, q24 時差/時定; underline scopes q5, q26, q27, q31–35, q33 options; q35 final 選べない/選びなさい. Grammar 1–13 full restoration; q14 高校; q18 shared みたいだのよ corruption (current ending よ is grammatical; consider retaining and documenting). Reading blocks: b001 速く/早く; b002 以下は/これは and 皆さんへ/皆さん。; b003 missing と in scan (current repair supported by retype); b004 introductory 以下は/これは; b006 literal escaped u3000; b008 missing second underline; b009 scan 1/9 for autumn vs current/source-retype 11/9, postal symbol, fee separator and empty row. Full table values and all reference questions have been checked. No source has printed furigana beyond genuine inline 五角(ごかく)/合格(ごうかく).

Next: inspect focused remaining answer/explanation and retype pages plus native notice image; resolve choices with field-specific confidence; prepare exact edit log/public cases and all inherited principal departures; review proposed full diff; write canonical artifacts, principal byte copy/catalogue and coverage/dispositions; run all three validators and exact ledger replay/integrity checks before advancing.

## Completed audit — 2026-09-28

Status: **audited_with_uncertainty**. Complete available written content reviewed: 35 vocabulary questions and 39 grammar/reading questions, 296 choices, 12 section headings, and 9 shared blocks. No scored written question or required context omitted. Listening was excluded. The preceding checkpoints are retained as history; their pending statements are superseded below.

### Evidence, identity and actual coverage

The July 2019 N3 identity is supported by cover, internal content and matching companion keys. Selected principal: indexed pdf_3, `src/Yuuki Bui/Đề thi N3 các năm Yuuki Bùi/N3 7-2019/N3-T7-2019-.pdf`, SHA-256 `ced665b17d8bcef15156db7975a30e553aada042902d4815c448f6b41e823ec8`. It is an unverified reproduction, not an authenticated original. Its physical pages 1–12 were visually reviewed completely; pages 13–14 concern listening. Page 1 identifies the sitting but advertises 22 pages in a 14-page file. Page 2 is publisher proficiency/time/scoring reference material, not an exam worked example. Pages 3–5 contain all vocabulary; pages 5–7 all grammar/star/cloze; pages 7–12 all reading passages, questions and the final table.

Other original-page coverage actually completed:
- pdf_1 physical 1–4: same principal page-body family with branding, not independent confirmation.
- pdf_6 physical 2–10: entire materially distinct written reconstruction; physical 13 written answer table. It changes vocabulary order and corrupts/shortens several grammar items. Its keys follow the principal order, so numeric transfer into its reordered items is unsafe.
- pdf_14 physical 2–6 and 11: distinct typesetting, full vocabulary/grammar/cloze and nature-program notice; useful for the star ending よ, 早く and autumn date 11/9.
- pdf_16 physical 3–12 plus the upper written-notice region of 13, written key table on 15 and explanations 19–21. This book shares several principal errors; agreement is not independent authentication. Rendered pages 16–18 were not claimed as reviewed.
- Companion pdf_5 physical 1 written keys; pdf_2 physical 1–5; pdf_9 physical 1–6; pdf_13 physical 1–4; pdf_15 physical 1–5. These answer/explanation pages were checked for the disputed vocabulary distractors, grammar and star/cloze content. pdf_9/pdf_13 share page bodies.
- pdf_12 physical 2, 4 and 9: confirms the poor pdf_6 typesetting lineage.
- pdf_10 physical 1, 6 and 7: cloze/decluttering/notice translation evidence.
- Native JSON's first twelve written sections and its complete nature-program image were read. Native Q25 substitutes an unrelated garbage-collection notice for the printed white-box passage; those mismatched candidates were rejected.

Fourteen relevant source files were SHA-256 checked; identities are in [source_inventory.json](audit_work/source_inventory.json). Listening-only pdf_4/pdf_7/pdf_8, listening images, shared answer cards and scoring spreadsheets were excluded. A suitable non-archive principal existed, so archive fallback was unnecessary.

### Full-content and difficult-case review

All stems, four choices, keys and shared context were checked in order, including unchanged text, punctuation, underlines and the final table. The written sources contain no ordinary printed furigana to restore; 五角(ごかく) and 合格(ごうかく) are genuine inline parenthetical text. Every star item retains four slots and its third-slot star. Reconstructed option orders for grammar 14–18 are 2413, 1432, 4231, 1324 and 1423, giving keys 1, 3, 3, 2 and 2. All written keys were reconciled with item reasoning and the companion/book key tables.

65 exact field corrections were appended to the root ledger: 50 high confidence and 15 medium confidence. Major high-confidence repairs restore the full grammar 1–13 questions and corrupted choices; reading-q009 key changes to 4 and reading-q013 to 3 as required by the restored option identities. Other repairs restore 高校 in the star item, underline scopes in vocabulary, the final 選べない distractor, the missing second underlined reference in the decluttering passage, and table structure/separators.

The fifteen medium-confidence fields were investigated against relevant page families, explanations and native transcription: vocabulary q001 も; q004 ゆうべん; q006 ほうこう; q012 買いました; q013 裏測 and 内測 distractors; q014 細い; q018 いろいろな…人だ; q019 引っ越して; q021 行けなく; q024 時差; grammar q004 にくらべ; cloze 早く; the white-box introduction/皆さんへ; and the cafe introduction 以下は. These readings have a defensible source preference but competing historically plausible wording survives. Each has its own exact public provisional-fix record with alternatives, actual checks and residual limits.

One material ambiguity remains unchanged: vocabulary q032 option 3 has 会話 in the principal/book but 会議 in another typeset family. Both contexts can carry the intentionally wrong target 満員; grammar cannot establish which noun was printed. The current 会話 is retained with a public unresolved case. Source counts were not treated as votes.

Inherited supported repairs were also rechecked: only 腰 is underlined in vocabulary q005 despite the principal's extra underline under 塗; the current quotation particle と in the white-box passage is supported by the other reconstruction and syntax; star q018 ends よ, supported by the alternate typeset source and the construction みたいだ, instead of the principal/book のよ; the notice's autumn 11/9 is supported by the alternate original pages, native image, translation, season and calendar context, unlike principal 1/9. These are current principal departures even when they required no new edit.

Corrections to preliminary checkpoint observations: reading-b006 contains an actual ideographic space, not a literal escaped Unicode sequence, and was not edited. The relevant printed q004 option is にくらべ, not にくらべて. Vocabulary q014 option 4 is 細い. The white-box passage already contains the comma after その時, so a proposed false difference was removed before application.

### Candidates, history and public records

All 312 local written candidate rows and 46 written historical ledger records were reviewed; the 27 historical listening records were preserved without review or change. Every candidate has a disposition in [candidate_dispositions.tsv](audit_work/candidate_dispositions.tsv), covering retained variants, corrected earlier decisions, wrong-item contamination, false positives, excluded non-exam text and unsafe order/key transfers. No global candidates or historical rebuild scripts were used.

The public uncertainty file has 15 provisional fixes and one unresolved case. The public principal-difference register has 23 current meaningful departures, including inherited kana/kanji/instruction variants, the omitted part labels, punctuation, the four supported repairs above, and notice details. Printed furniture and harmless reflow were excluded; separately supplied answer keys, editorial explanations and import metadata are not treated as printed source text. Every public snapshot matches the final JSON.

### Verification and reporting

Baseline SHA-256: `3587c63ffdc0966d3ff45d4fdef914ffc7cc8c643618cc3b94dad2c23dcc88eb`.
Final JSON SHA-256: `04a8917a47216c743d595a4ee41b06b327ea631f96b20b09e37425084496ced4`.
Read-only index SHA-256 remains `789e9253fcd301b82fff13653a2fac8b0cd6b636db4e730c582697f8265bb331`.

[Apply verification](audit_work/apply_verification.json) confirms exact baseline-plus-ledger replay, unchanged import metadata, all fourteen source hashes, and the preserved 82,799-byte historical ledger prefix (73 rows; SHA-256 `92d3b94d4185b7f37824afde8bb9736cef995a8860e44b83c0d5c023e806f006`). The root ledger now has 138 rows.

All three canonical validators passed; [validation.json](audit_work/validation.json) contains their actual outputs. Structural counts: vocab 35/140/0 blocks; reading 39/156/9 blocks; zero null keys. The 17 baseline warnings are expected: fifteen question option-array changes and the two key changes described above. Changed choices were visually checked and answer mappings reevaluated; no unexplained warning remains. Validation establishes record/structure consistency, not historical authentication.

The principal catalogue records method-1 score **132**: unverified provenance 100 + one metadata group (2) + two major defects (10: star ending and autumn date) + two minor defects (4: extra underline and missing quotation particle) + sixteen disputed fields (16). Imported corruption absent from the principal was not charged to it. Its byte-identical inspection copy is [principal/N3-T7-2019-.pdf](principal/N3-T7-2019-.pdf). Four scoped ancestry observations were appended; they do not establish uploader-wide rules.

The unit is complete with published uncertainty. Advance over already-terminal July N4/N5 entries to N1_12_2018.



## Housekeeping 2 — 5 November 2026

N3_07_2019-PD-002: The selected copy, numbered copy, native writing heading and three authenticated parallel tasks agree on ことば, 書くとき and えらびなさい. All retain the comma before the four numerals. Restore that punctuation; the compact copy’s 言葉 and 書く時 do not better fit this task.

N3_07_2019-HK1-INST-vocab-s02: The selected copy, numbered copy, native writing heading and three authenticated parallel tasks agree on ことば, 書くとき and えらびなさい. All retain the comma before the four numerals. Restore that punctuation; the compact copy’s 言葉 and 書く時 do not better fit this task.

N3_07_2019-PD-003: The selected and numbered same-sitting copies retain the complete blank instruction and the comma. The compact copy drops もの; the same-level printed comparators and native heading preserve it. Restore the comma and ordinary heading separator without touching item blanks or choices.

N3_07_2019-HK1-INST-vocab-s03: The selected and numbered same-sitting copies retain the complete blank instruction and the comma. The compact copy drops もの; the same-level printed comparators and native heading preserve it. Restore the comma and ordinary heading separator without touching item blanks or choices.

N3_07_2019-PD-004: The selected, numbered, compact and native versions place に directly after the target line. Three actual N3 printings use that construction for the same task. Remove the earlier inserted noun, restore the attested comma and omit the unprinted colon. Preserve the existing drawn target.

N3_07_2019-HK1-INST-vocab-s04: The selected, numbered, compact and native versions place に directly after the target line. Three actual N3 printings use that construction for the same task. Remove the earlier inserted noun, restore the attested comma and omit the unprinted colon. Preserve the existing drawn target.

N3_07_2019-PD-005: The selected copy supports つぎの, 使い方, the comma and えらびなさい but writes 言葉. The numbered and native copies and genuine N3 usage tasks support ことば. Keep that scoped spelling and restore the comma and ordinary heading separator. The remaining 言葉/ことば departure is real.

N3_07_2019-HK1-INST-vocab-s05: The selected copy supports つぎの, 使い方, the comma and えらびなさい but writes 言葉. The numbered and native copies and genuine N3 usage tasks support ことば. Keep that scoped spelling and restore the comma and ordinary heading separator. The remaining 言葉/ことば departure is real.

N3_07_2019-PD-007: The selected copy writes もうすこし. Both separately typeset alternatives and the native field have もう少し, although the compact/native copies reorder choices and share 細かい. Neither spelling changes the target. Preserve the present surface pending an original.

N3_07_2019-vocab-q014-options-3: The selected and numbered copies give 細い fourth. Compact and native agree on 細かい in a reordered list with 浅い first, so their shared alternative is not a second printing. Keep the selected distractor and retain the source-index uncertainty.

N3_07_2019-PD-008: The selected copy and the compact/native family print 歩きまわって in this very sentence. The numbered reconstruction prints 歩き回って. Prefer the selected suffix with corroboration across layouts; keep 辺り, all alternatives, and the fourth-choice key.

N3_07_2019-PD-015: The selected question and the compact/native wording variant give the same kana humble option. The stem variant changes the construction to 買ってきて but not the option spelling. Keep さしあげます and resolve the editorial choice; no direction-of-giving repair is warranted.

The 132-point source assessment is retained. Q14 alternative S-012 remains uncertain, and the four instruction punctuation comparisons were not charged events. No score evidence was removed. 5 editorial fields changed. 2 public and 4 principal snapshots rebound to pre-existing field changes; not substantive reviews.

[Before/after decisions and receipts](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N3_07_2019/disposition.json).
