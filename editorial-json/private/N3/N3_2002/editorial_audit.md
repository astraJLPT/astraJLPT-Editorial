# N3_2002 written audit — H25

The available written investigation is complete; the result is **incomplete source coverage and a partial practice paper**. The Old 3.9.0 editorial contains 98 playable questions (48 vocabulary and 50 reading/grammar), 392 choices, 13 contexts and 11 sections. Seven original scored vocabulary questions and six known unscored examples remain unrecovered. The source has 105 scored positions, 55/50. Original question-number gaps remain. PDF integration is `pending_after_h23`.

## Source review

The principal is `src/JLPT N1-N5, Past papers/N3/2002/2002年日语三级真题及答案.pdf`, SHA-256 `a83e39a404d4e8528843be29df49b9c0f64f0147f48ebfc5928666b9bc766044`, indexed Tier 2. Both written title blocks establish 2002 and 3級. The previously inspected [official 2011 guide](https://www.jlpt.jp/reference/pdf/guide2011.pdf), physical 2, supports the December sitting attribution through its annual-examination footnote.

All written PDF regions were visually reviewed: vocabulary pages 1–5, ending above the listening heading on 5; reading/grammar pages 24–31; vocabulary key on 32 above listening; reading key on 33 below listening. Page 30's passage was additionally checked in a native close-up: 花 is present in めずらしい花や鳥, so no repair was made. Existing indexed OCR served only as navigation and was checked against visible pages. There was no fresh OCR. Five consecutive complete questions 1–5 on page 1 passed missing-editorial preflight; the candidate TSV has zero rows. Listening regions were excluded.

The complete GB18030 text `2002年.txt`, hash `c08dbaecc4ee592417b62e231209c7babe4fde9ca2ee67e0ab4e3aedc5e90c43`, and both written panels of `答案.jpg`, hash `0a2ec7ed2de4e29aff6c97e517cd41c6da5f2df59430f23b25d50e902b04152b`, were compared. The TXT contains all 105 positions followed by a repeated vocabulary block after a sell marker. That repeated block is identical after width/whitespace normalization and is not an independent witness. The JPG and embedded PDF key scans have the same table arrangement and hujiang watermark; independent authority is not established. The indexed listening TXT, hash `daa5b4ac27cd28703e0a50bcfd848a7b17b51679db3919aa609e09d1f3f3c4dd`, was classified from its opening, not audited as content. No written explanations were available.

The PDF is a compiler-branded 一碌蔗 retype with bingdian001.com creator/author metadata and a 2018 conversion date. Neither it nor the related text/key witnesses establishes original issuer custody. Retypesetting alone does not prove known recollection reconstruction. Exact source mirrors and a byte-identical principal inspection copy preserve filenames and hashes.

## Playability, repairs and uncertainty

Vocabulary positions 22, 24, 26, 28, 30, 33 and 35 contain 16 literal star placeholders in wrong-choice glyph positions. Their keys do not recover the missing alternatives. They are omitted from the playable editorial; complete surviving fragments and original keys are stored in [omitted_fragments.json](audit_work/omitted_fragments.json). All 11 target contexts remain complete, including tested words for omitted questions.

Focused external checks found the same stars in search-indexed gaku.ru and Qingsuyun retypes. Their page opens timed out; no external PDF pixels were reviewed. The opened [Yurika/Saromalang Level 3 2002 retype](https://y.saromalang.com/k%E1%BB%B3-thi-n%C3%B4-jlpt/2001-2005/level-3-2002) supplies candidate glyphs but repeats distinctive damaged wording elsewhere and has no recovery provenance. Several candidates also change surviving suffixes, including 味→末 and an added お. Arbitrary wrong-character forms cannot be inferred from language logic. Those alternatives are documented in the seven public gap cases, not adopted as recovered content. Focused exact-candidate and original-booklet searches found no discriminating original image. A commercial 2001–02 volume listing establishes only bibliography, not question content.

The separate れい columns in both keys identify six missing examples: vocabulary I–V with keys 4,2,2,3,4 and reading I with key 3. No prompts or choices survive in the available written sources or the checked external retype. They are separate known missing blocks. Original written covers, timing and typography also remain unverified; secondary title blocks and scaling tables do not authenticate them.

Twenty-five changed fields are recorded in the exact ledger and [principal_differences_N3_2002.jsonl](principal_differences_N3_2002.jsonl):

- Eleven target-group labels replace corrupted question marks with the aligned web middle-dot separators. In the same field, group 4 changes 地理に研究して to 地理を研究して. The latter is a medium-confidence minimal object-particle repair; all available retypes repeat に, so original wording could have been longer, such as について. Its public provisional case preserves that uncertainty.
- Eight task headings restore separators between choice numbers; the ninth heading repair completes the truncated vocabulary V instruction from both indexed TXT occurrences.
- Vocabulary 38 moves the response slot after たまに, supported by the indexed TXT and the contrast expressed by key 2 しっぱい. The principal's position after おいしく makes the keyed answer ill-formed. Vocabulary 41 restores す before る, also supplied by both TXT occurrences, allowing key 4 りようする.
- Three fields restore unfinished-utterance dots from the aligned web text: four dots after ちょっと in the restaurant dialogue and three dots in each of reading 45's first two choices. No missing predicate is invented.

Seven further principal departures record omission of the unplayable question fragments. There are 32 departures total and 10 public cases: one provisional particle repair, seven unresolved wrong-choice sets, one combined missing-example/partial-coverage case, and unavailable original covers. All current-value snapshots match the editorial.

Every scored key was checked against the tables and task meaning. No key changed. Reading 23's interrogative いいんですか is awkward in isolation but grammatical; the available sources agree, and key 4 元気だ remains supported. Wrong alternatives are preserved rather than normalized. Reading 17 and 27 have wide unruled answer gaps; canonical fill-line representation preserves the response-slot function without asserting a source underline. This harmless linework choice is documented separately from substantive departures.

## Structure and defaults

All 13 contexts, paragraphs, dialogue turns, tested underlines and inflections are preserved. No written body figure, ordinary ruby, attribution or lexical note was observed. Key-table images are not question-body figures. Lower-level word spacing remains meaningful content. All context/question associations have exact digests and page/region bindings with inferred presentation authority. Original writing direction and pagination are unknown; retype page breaks are not forced.

The unit inherits Old shared/level-3 revision 6 with no local overrides or style variants. Secondary per-question weights are retained: vocabulary 1–35 at 1 and 36–55 at 2, reading 1–38 at 2, 39–43 at 3 and 44–50 at 4. Original raw totals 75/119 become 68/119 for included questions. Secondary scaling formulas are not a basis for presenting this partial paper as a complete timed exam.

## Assessment and validation

The method-1 principal uncertainty index is **199**: 100 unverified provenance points plus the capped content score. Thirteen missing units contribute 130 (seven questions counted once each, six example blocks), one major defective field contributes 5, and 24 minor fields contribute 48. The uncapped content sum is 183, capped at 99. Group 4's punctuation and particle share one content-field event. Covers create no additional content unit. A record correction assigns distinct identities to the six example score events; counts, score and question content were unchanged.

Canonical editorial/schema, public cases, fixlog, principal index and current principal differences pass. All 169 exact content-ledger rows replay to the editorial (33 section metadata fields, 111 question/context creations, 25 repairs), as does root metadata creation. Source hashes, immutable dependencies, profile/style APIs and context bindings pass available checks. The full assembled final text was read back, including all 98 questions, 392 choices, keys and 13 contexts.

Two pinned-runtime checks remain unavailable: model composition/renderer collectors lack the frozen dependency `rubi-restore/tools/ruby_core.py`; publication identity rejects the immutable registry's absolute live-source paths under the isolated root. No live replacement dependency, parser edit or registry rewrite was introduced. These limitations are explicit common integration requirements, not claimed passes. Validation receipts are under the run's `validation/N3_2002/` directory.

All available required written checks are complete. Listening/audio, exam-PDF composition/rendering and publication remain deferred. Live files, other handoffs and original sources were preserved.
