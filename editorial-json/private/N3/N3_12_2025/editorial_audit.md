# N3_12_2025 editorial reconstruction audit

## Opening checkpoint — 2026-09-26

Status: in_progress. Folder/index exist; editorial JSON absent. All18 canonical source hashes verified. Root ledger baseline preserved byte-for-byte in audit_work. No original page has yet been visually reviewed. Next: filter and review all written candidates/historical decisions, establish identity/coverage, compare complete written witnesses, reconstruct and investigate, then publish/validate.

## Completed written reconstruction — 2026-09-26

Status: audited. The missing editorial JSON has been reconstructed as a complete written paper: 12 sections, 57 vocabulary/grammar questions (35 vocabulary plus22 grammar),16 reading questions,292 choices, and10 context blocks (worked example, cloze, eight reading texts/notices). All73 questions are playable and gradeable; no omitted written unit or null key. No listening content was reconstructed.

### Evidence and coverage

All18 canonical indexed source hashes were verified before and after reconstruction. The index remained unchanged (SHA-256 9fde87503624c4bb96480b8d6fb8ef99146a9778e12696b796db3b9b774717d3). The focused20-path inventory finds only the two substantive question PDFs, the Munja transcript, their indexed answer/explanation/notice assets and byte-identical distributor aliases. No additional independent written witness was found in the sitting-specific local inventory.

Principal: index source0, src/JLPT_N1_N5_202512/25年12月N3/25年12月N3真题.pdf, SHA-256 5d558eb1ec603acb931318d2170515ece93a385504ce960d4a095de5ea84b9db. All physical pages1–24 were visually read, including every stem/option, printed ruby, underline, example, passage, footnote, email and table. Printed vocabulary pages1–5 contain questions1–35; grammar/reading pages1–19 are physical6–24 and contain questions1–38. Physical25 establishes the listening boundary. There is no gap in written pagination or content.

Comparison source2 has a replacement cover, the same written page sequence at physical2–25, and a final key grid at39. All24 written pages were aligned using Vision OCR as a navigation aid. Direct original-image comparison covered source2 physical2,3,4,6,7,9,10,11,12,13,16,23,25; cover1 and the written region of key39 were also inspected. Listed corresponding page bodies match, with different scaling/margins. The replaced cover's31-page claim does not describe the selected principal. The bounded visual relationship is appended to ancestry_record.tsv; hashes/distributor names do not establish independence or authenticity.

All12 written Munja sections were read in full. Native written explanation source5 physical1–9 was read in full. Source4 page1, source8, source9 and source17 written answer grids were visually compared across their full written spans. The source2 appended key matches source4's design/entries; source8 and source17 share answer-table design and the same two contrary entries. These are not treated as independent votes. Original picnic/library assets15/16 were visually checked in full against principal pages14/24. Listening source3, images10–14, generic score spreadsheet6 and answer card7 are excluded as written-content evidence.

### Candidate and historical review

All31 written candidates (15 reading,16 vocabulary) and10 written historical decisions were read. The76 listening candidates and4 listening historical wrappers were filtered out. R001–R005 andV001–V002 flag valid morphology; preserve source-supported forms. R006–R009 andV003–V010 concern UI heading prefixes; rebuild instructions from the original. R010–R015 andV011–V016 are parser diagnostics, not exam defects. No candidate was accepted merely because it was listed or previously rejected.

The10 historical written repairs were independently checked against current original pages: worked example, full picnic notice, full hotel mail, displaced hotel question stem and four choices, complete library table, dropped30分 digit, 近所にもっと, and spanned library header. Duplicate UI copies in the old history do not create extra exam items. The14-row old root ledger remains an exact byte prefix;119 new creation records are appended (36 section fields plus83 items).

### Reconstruction and Japanese decisions

Restore the printed ことば/つぎ/えらび instruction wording, complete reading directives, the cloze instruction 文章全体の内容を考えて, and the four cloze labels19–22. Preserve the original wrong distractors, including question14 fourth choice姓各; the transcript had duplicated性各. Restore source-printed ruby with exact base spans and occurrence control:348 ruby nodes. In 留学生／留学生活, only the first full word receivesりゅうがくせい and the later留学 receivesりゅうがく. Reading予想 has no printed ruby and remains unannotated. The final original-page check also recovered飛(と) in vocabulary31 option3.

The worked example retains order3–2–4–1, third-slot star and filled answer4 in aligned tables. The five scored star orders are1–4–3–2,3–2–1–4,2–1–4–3,4–1–2–3,4–2–3–1, yielding3/1/4/2/3. Grammar5 retains distractorのと比べると despite OCR omissions; the correct option remains3にしたがって. Cloze keys3/4/1/2 follow the retrospective cause, contrast, inclusiveどの会社も and final explanation.

The email's greeting, seasonal warning, signature, URL and room details are complete. Its question is restored from a five-entry transcript to the actual stem and four choices; correct key2. Picnic notice: advance contact is unnecessary, drinks are brought, and joining with the2000-yen annual fee waives the300-yen participation fee; key4. The library table preserves the two-column spanned席の種類 header, all four seat descriptions/capacities, computer permissions, time limits, opening hours, and application/card conditions. Its two questions both answer1. No printed label利用内容 is invented.

Restore the missing short-reading and分散型ホテル stem underlines and subway footnote callout. In the reading-aloud story, underline① stops before the sentence period,② covers予想 only,③ stops afterだろう; the corresponding question13 underline excludesとあるが. All complete passages and all alternatives were evaluated against their keys, not inferred solely from a key majority.

Two resolved public cases explain the image-key conflicts: vocabulary14 is3性格, not2性各; grammar3 (editorial vocab-q038) is1でなら, not3でしか, because the governing predicate伝えられる is affirmative and the embedded言えない does not satisfyしか. Both original question versions preserve the same choices and predicate; the full explanations and separate PDF key support the retained answers. No medium-confidence correction or retained material ambiguity remains.

### Principal reporting and verification

One principal difference adapts右のページは to以下は for the sequential library-notice layout. Other repairs recover what the principal actually prints. Separate image-key errors are not principal defects. Method1 principal assessment: unverified provenance100; zero metadata flags, missing units, major/minor defects or uncertain fields; total100. This is not authentication. The convenience copy underprincipal/ retains the exact original filename and verified bytes.

All three canonical validators pass without errors or warnings: editorial schema/cases/root ledger with expected57/16 counts, principal index, and principal differences. Exact creation replay confirms all36 section fields and83 items; all73 one-based keys match the reviewed sequence; all292 choices, five star orders,348 ruby nodes and table relationships are checked. Source/index hashes and ledger prefix are preserved. No HTML export or source rewrite occurred. Private scripts, coverage/ruby map, OCR alignment, provenance, validation outputs and integrity result are retained in audit_work for reproducibility.

Final editorial SHA-256: 250980657c4341772ab318159cd6674ca158d8beb2708637bd7e36f6b2771016
Final root ledger SHA-256: df2f67197bcb6c34446ea4fb784ec8232db498cbc28e29498655db1f6b20d865


## Housekeeping 2 — 5 November 2026

N3_12_2025-PD-001: resolved. Keep HK1's restored 右のページは. The complete approved heading, facing library notice, table, application instructions and all question choices were inspected. Current keys 1/1 fit the full conditions. 以下は was a layout adaptation unsupported by the source. Resolve this source-agreement case without changing the current wording, markup or retained November presentation policy.

Two hours after 17:00 is possible on Wednesday in reading seat A; B's 90-minute limit and Saturday's 18:00 closure rule out the other choices (Q37 option 1). A high-school student using her own computer for an hour can request reading seat B or a study seat with her lending card (Q38 option 1). The notice is the facing right-page referent. Other December levels retain their own verb forms and ruby; no cross-level template replacement is justified.

Unchanged 100; no source-concern event is charged for this heading.

No editorial, ruby or principal-departure content changed. Historical fixlog bytes and all case identities are retained. [Source hashes, before/after cases and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N3_12_2025/disposition.json).


HK2 additional written-page reviews, 5 November 2026: 2 record-only decisions, no canonical edits. Exact sources, competing evidence and all before/after records: [N3_12_2025](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/later-direct/N3_12_2025/report.json).
