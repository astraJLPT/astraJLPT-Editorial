# N4_12_2025 editorial reconstruction audit

## Opening checkpoint — 2026-09-26

Status: in_progress. Folder/index present, editorial absent. All indexed canonical and alias hashes verified. Four-row historical root ledger preserved byte-for-byte. Original written pages rendered; visual review and full reconstruction remain pending.

## Completed reconstruction — 2026-09-26

Status: **audited**. No editorial JSON existed; this audit creates schema v2 from inspected source pages, with null HTML import hashes/counts and explicit reconstruction evidence. The logical HTML paths are future export bases only. Working HTML and source files were not edited.

### Evidence and coverage

Principal: `src/JLPT_N1_N5_202512/25年12月N4/25年12月N4真题.pdf`, SHA-256 `38525b613a28dbec20003f7d2a2cbda6a4a5fc7ca96d0a9788b6955cc294ea1c`. All six indexed canonical files and every indexed alias were hash-verified. The question PDF is 36 pages with no usable native text. Its entire available written content was visually inspected: physical pages 1–13 (grammar/reading) and 14–21 (vocabulary). Physical page 22 was inspected only to establish the listening boundary. Listening content is excluded.

The header identifies the 2025 second sitting, level IV. The legacy claim that this header establishes a reconstruction is unsupported: no positive recollection/retyping claim was observed. Neither the header nor scan appearance authenticates the file. Classification is `unverified`.

Printed grammar/reading labels are 1–4, 6–10, 12–15; vocabulary labels are 1–8. Missing printed labels 5 and 11 are one unresolved pagination issue group. Every question and necessary context is present, but the copies cannot prove that these were blank separators. Score: 100 provenance + 2 metadata = **102**, with zero missing scored units or confirmed principal-content defects. Key-image omissions are not defects of this question PDF.

The three indexed question-PDF aliases are byte-identical, not independent witnesses. The focused inventory retained 13 matching paths (including the generic answer card and advertisement); all useful question/key files were already indexed and it found no distinct question witness. A first broad filename filter also matched date text in collection names; it was narrowed to the immediate path components before drawing this conclusion. No unrelated paper was used as question evidence. Generic answer cards and printing advertisements were excluded. Cached OCR is derivative navigation support, not independent testimony.

All written regions of `答案1.png`, `答案2.png`, and `25年12月N4答案.jpg` were visually inspected. The PNGs are consecutive portions of a shared reference-key design; their independence from the JPEG is not established. Their exact indexed hashes and locators accompany the reconstruction and public cases. No explanation document or independent full question transcript was found. Local source comparison and full-item Japanese reasoning resolve the material discrepancies without external research.

### Full-content review

The final structure has 11 sections: five vocabulary and six grammar/reading. Vocabulary has 28 scored questions and five printed example blocks. Grammar/reading has 29 scored questions (21 grammar and eight reading) and eight blocks (two examples, cloze, three short passages, long passage and final notice). Total: **57 questions, 228 options, 13 blocks, seven examples, 199 ruby spans, no null keys**.

All headings, complete stems, all four choices, keys, shared passages, paragraph order, names, dates, contacts, underlines, printed ruby bases and placement were compared. The five vocabulary examples and two grammar examples were absent from the old transcription and are now restored, including the answer-sheet demonstrations and the worked ★ arrangement. No vocabulary-body ruby was printed; none was added. Grammar Q7 option readings remain bare as printed. Cloze 作 has ten printed readings, including 作れる; its 野菜 has eight. The PDF crops settle small reading aids and underline boundaries.

The fishing passage and Q22 underline the complete span ちょっと面白い魚料理の店. The long passage and Q25 underline only いつか日本に行ってみたい, excluding the following thought expression. All other observed underlines were preserved. The cloze options belong to physical page 6, correcting the legacy page annotation of 5.

Both drawing-class notice tables were checked cell by cell: all six classes/teachers; A/B people or objects, C/D landscapes, E/F selectable subjects; group/individual conditions and paired fees; ten schedule rows; both footnotes; address 北糸市白田18-6 and phone 012-245-6621. Blank source table headers remain blank. Row/column spans preserve the actual relationships. Decorative drawing, headers/footers and harmless reflow are excluded. No meaningful diagram is needed to answer the questions.

Keys, grouped in printed problem order:

- Vocabulary: `2143132 / 44321 / 23412234 / 1314 / 2312`.
- Grammar: `2133141424312 / 3312 / 1432`.
- Reading: `313 / 144 / 22`.

★ orders for grammar Q14–17 are `4-1-3-2`, `2-4-3-1`, `2-4-1-3`, `3-4-2-1`. The third positions give `3,3,1,2`. All four slots remain outside ruby.

Japanese checks included particle relations and predicate forms throughout grammar, the vegetable-juice cloze's hearsay/benefactive/comparison/invitation sequence, the fishing condition versus bringing outside fish, today's call deadline versus tomorrow's meeting, and the pet-hotel reference. Q25's earlier wish precedes the later invitation; Q26 describes the family's normal meals/showers; Q27 recognizes their special accommodation. Q28 requires C; Q29 requires A and D after applying both time and price limits. Intentional vocabulary distractors, including machine/piano うんてん and 年がにている, were retained rather than polished.

### Legacy and discrepancy dispositions

The local candidates file exists with **zero data rows**. All four historical ledger records were reviewed. The two full HTML payloads supplied a private transcription aid and were rechecked against every original written page; they are not treated as independent witnesses. The two navigation additions are outside editorial content and were neither replayed nor changed. The complete four-row ledger prefix remains byte-identical.

The legacy note overlooked that `答案1.png` has only seven digits `2412234` for eight vocabulary questions13–20. Its omitted Q14 answer is **3 だいじな**, supplied explicitly by the numbered JPEG and independently supported by the cherished-watch context. Inserting that digit aligns the full group. The other known omission is the JPEG's missing reading Q25 answer **1**, with subsequent labels shifted by one. The PNG `144` sequence, full passage chronology, and all following questions settle the alignment. These are two **resolved, high-confidence public cases**, not remaining provisional questions. No medium or unresolved content cases remain.

The public principal-difference register has one row: the final instruction's 右のページの becomes 以下の for the sequential notice layout. Printed examples, ruby and underlines were restored to match the principal, so they are not current departures. Unprinted keys and reconstruction metadata are not textual disagreements. This reconciliation covers all 21 written pages and the complete final editorial, not just changes against the legacy transcription.

### Validation and integrity

All three required checks passed without errors or warnings: editorial with `--expect vocab=28 --expect reading=29`, principal index (32 rows), and N4 principal differences (one row). Exact outputs are retained in `audit_work/validation_results.json`; checks establish structure/record consistency, not authenticity. `final_integrity.json` also confirms exact replay of every new section/item from the appended ledger, all 57 keys, count/ruby totals, two notice tables/contact, and the untouched index hash.

103 new high-confidence creation records were appended: 33 section-field records and 70 complete question/block records. No fabricated line numbers, official points or HTML import hashes were introduced. Ledger SHA-256: `df08819763708db55cca68f299d4da269ef0d906ff49c15417349402b90a1e1b`. Final editorial SHA-256: `412722cc724a5a42a5b8cb363d6aaf0a1fd0f15e3c45ce903636c615c699557f`. Index SHA-256 remains `f79407de1d2bce7c6ba04e96775d4b8e6ef2fafd71783a18fac69bcf366d2f47`.

The principal inspection copy preserves the original filename and exact catalogued bytes. The catalogue records the canonical `src/` path, written scope 1–21, unverified provenance and score102. One bounded byte-alias ancestry observation was appended. All current outputs and validation precede progress completion and queue advance.


## H11 continuous-reading amendment — 2026-10-15

Removed 338 explicitly reviewed phrase separators in 36 actual reading fields. Exact before/after values, reversible position maps, intact ruby proofs and live canonical binding are in `pdf-render/evidence/handoff11/N4_READING_AUTHORING_PREPARED.json` and the appended unit fixlog. Grammar, examples, scored facts and existing unresolved-case statuses are preserved.


## Housekeeping 2 — 5 November 2026

N4_12_2025-PD-001: resolved. Keep the HK1 restoration 右のページの. Both approved pages, all table headers and notes, and every choice were inspected. The exact spatial reference and two printed ruby spans agree with current markup. The previous 以下の adaptation is not printed. Resolve this source-agreement case while preserving N4's distinct heading construction and the full task.

Nishiyama's group landscape class is C (Q28 option 2). Saturday morning classes under 15,000 yen are A and D; F meets the time condition but costs 20,000 yen (Q29 option 2). The heading points to the right-page art-school notice, with の connecting ページ to the notice description. The current 絵/え and 案内/あんない spans match the heading. An N1/N2-style は clause would not preserve this level's printed wording.

Unchanged 102. The pagination issue is independent of this heading and remains.

No editorial, ruby or principal-departure content changed. Historical fixlog bytes and all case identities are retained. [Source hashes, before/after cases and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N4_12_2025/disposition.json).


HK2 additional written-page reviews, 5 November 2026: 2 record-only decisions, no canonical edits. Exact sources, competing evidence and all before/after records: [N4_12_2025](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/later-direct/N4_12_2025/report.json).
