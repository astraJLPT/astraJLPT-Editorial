# N3_12_2015 written-content audit

Completed 6 October 2026 within run `2026-10-06_N1_12_2016_to_N5_07_2010`.

## Result and scope

**Audited with uncertainty.** The reconstruction contains all 74 reviewed scored questions: 35 vocabulary and 39 grammar/reading, with 296 options and all 74 keys retained. Its 12 sections contain 15 blocks: one restored worked example and 14 context blocks. Five of those context blocks contain only inherited passage labels; the remaining nine are substantive contexts (cloze, four short passages, two medium passages, one long passage and the railway notice). Their stable IDs and ordering are preserved. No scored question or required context is omitted; the example identity and selected fuller notice text remain explicitly provisional. Listening is outside this audit.

There are **86 new granular log records: 82 high-confidence and four medium-confidence edits**. Seven public cases remain: four provisional fixes and three unresolved comparisons. Seven current departures from the principal are recorded, including inherited choices. Historical imports, points, IDs, source indexes and all 91 prior fixlog rows (105,717 bytes, including one listening row) remain byte-for-byte preserved. The 183 written candidates and all historical log rows were read; their current dispositions are in [candidate_dispositions.json](audit_work/candidate_dispositions.json). Old accepted/rejected labels were treated as leads, not evidence authority.

## Principal and source comparison

The actual principal is `src/Yuuki Bui/Đề thi N3 các năm Yuuki Bùi/N3 12-2015/Đề N3 12-2015.pdf`, SHA-256 `620e95db593b36008acb12665cfa0497bfc8563aad5511fb9656630d4fa403f5`, initially tier 1. Physical pages **2–9** contain the complete available written content; page 1 is the cover and page 10 begins listening. The original file is unchanged. The [convenience copy](principal/Đề%20N3%2012-2015.pdf) is byte-identical and does not count as another witness.

This copy was chosen after comparison because it supplies all scored written content, the complete STAR demonstration, readable annotations and coherent information tables. Its two star positions, duplicate vocabulary distractor and abbreviated notices prevent treating it as mechanically authoritative. Its acquisition is **unverified**: no exact user-approved original or issuer custody was established. Typesetting and distributor branding alone neither authenticate it nor prove reconstruction from recollection. The other copies' cover/pagination claims were not transferred to this principal.

Four written question layouts were fully read: index source 4 pp2–9, source 8 pp2–9, source 0 pp2–11 and source 20 pp1–12. All 74 structured written items and 296 options were aligned with source 2. Written grids in source 3 p1, source 8 p12 and source 23 pp1–2 agree with every retained key. Source 24 pp3,5–8 supplies directly inspected vocabulary and grammar analysis; source 6/7 archived HTML supplies actual import-lineage readings at the affected spans. Both indexed railway images (31/32) were read in full. Focused source 16 p2 matches source 8 p2's body; source 18 pp2,5,7 matches source 0 pp2,5,7 with different branding. These are bounded page observations, not whole-file identity or independent acquisitions. Source 4 and source 20 share distinctive errors while using different examples; their agreement is not an independent vote.

[Source coverage](audit_work/source_review_coverage.json) identifies exact used and unused scopes for all 42 indexed sources. Raster bodies were read from rendered pixels; native extraction and OCR inventory were navigation only. Principal pp2,3,4,5,8,9 received 4000-pixel follow-up checks for thin underlines, glyphs, example labels, punctuation and table details. No new external research was used: the material local variants were investigated, and more unattributed copies or current phone directories would not settle their historical identity.

## Reconciliation and changes

The audit restores source task wording (`ことば`, `えらび`) and the vocabulary, grammar and reading group labels. It corrects vocabulary underline endpoints, the two `キムラ・プック` transcriptions, the missing opening blank parenthesis in grammar Q10, the quote-internal period in Q8, the comma in Q4 and intrusive extraction spaces. Separate speaker turns, cloze title/author, paragraphs, notices and glossary boundaries now have balanced renderable markup. Circled reference numbers stay outside the passage/question underlines.

Grammar Q15 had an inherited boundary error: `の建設工事が` belonged to option 1 after `駅ビル`, not the stem after the four slots. All inspected question PDFs support that boundary independently of their disputed star positions. Its repaired complete sentence and all four other STAR sentences exactly match their option sequences. The separate editorial explanations now use `基本的な使い方に`, include `が` after `冷たい空気`, highlight only Q15's selected fragment and preserve the complete sentence ending. They are not represented as printed exam text.

The previously empty example block now contains the selected principal's full television/Yamada example, four choices, solution demonstration and marked bubble. Its middle solved labels were demonstrably transposed relative to its own options; corrected labels 1–3–2–4 agree with the third-slot fragment and marked answer 2. The competing desk/pen example is documented rather than blended into this one. Its numbering is coherent but it visibly lacks の after つくえ, another reason to prefer the grammatical selected example without claiming historical certainty.

The tennis greeting and the cleanup heading/date are recovered provisionally from actual question PDFs, not merely inferred from structured text. The cleanup email and contact name are directly witnessed; the disputed phone digits have their own provisional case. Earlier claims that those contacts were invented are rejected. The final refreshments line uses the principal's ordinary bullet. The railway parent-child price is one 1,000円 cell spanning the adult and child rows; it is no longer repeated as if there were separate charges. All ticket ages, weekdays, prices, purchase deadlines, school-group conditions, footnotes, contacts and the four-row Q39 table remain intact.

The principal clearly prints terminal stops on all four options of reading Q24,26,30,33,35,36,37. All 28 stops removed in the historical pass are restored. It also prints a stop after the long passage's ellipsis; that stop is restored. The older copy's omissions were real variants, but do not justify the historical description of those stops as absent from the selected source. Conversely, the suspected missing 支給 underline was a low-resolution viewing error: it is present at 4000 pixels and yields no departure, defect or edit. Vocabulary Q17 already had no comma after 毎日; no phantom correction was applied.

Intentional wrong choices retain their words. In particular, vocabulary Q3's `ふんか` is a wrong option, not the correct reading of 変化; correct key 2 is `へんか`. The earlier rationale is corrected in the disposition record, without rewriting history. Vocabulary Q14's `頻って` is a printed distractor. Reading Q29 remains key 2 after full context review; vocabulary Q29 remains key 3 (`機会` = `チャンス`). Broad character detectors and nonconcrete comments do not authorize speculative Japanese polishing.

## Remaining public uncertainty

| Case suffix | Current decision | Limitation |
|---|---|---|
| `reading-b001-example-identity` | Restore television/Yamada example, internally corrected | Another question family prints a different desk/pen example, apparently missing の. |
| `reading-b004-greeting` | Restore addressee and opening sentence | Principal omits both; exact original extent is unproved. |
| `reading-b008-contact-phone` | Restore `222-3333（森口）` | Fuller-notice family prints `222-333`; archive extraction has further corruption. |
| `reading-b008-header-date` | Restore title, invitation and December 13, 9–11 date line | Principal condenses the top to `13日9時`; original extent remains uncertain. |
| `vocab-q018-third-distractor` | Retain `壊す` | Principal/book question duplicate `踏む`; archive has `挑む`. Actual question copies and paired analysis explicitly support `壊す`. |
| `reading-q014-star-slot` | Retain second star/key 2 | Principal and some copies print third; assembled order is 4–2–1–3. |
| `reading-q015-star-slot` | Retain third star/key 2; repair fragment boundary | Principal/book copy prints second; assembled order is 3–4–2–1. |

The first four cases correspond to the four medium-confidence edits. The remaining three retain current preferred choices with residual source uncertainty. Separate answer grids support coherent practice answers but do not authenticate historical star placements. No available material distinction was left unchecked merely to create a case. The public files contain exact final typed snapshots and source titles/hashes/pages, without private-log dependencies.

## Current principal departures and assessment

The seven departure rows cover the retained instruction target blank, Q18 third distractor, corrected example labels, Q14/Q15 star positions, tennis opening and cleanup heading/date. The restored phone matches the principal and is not a departure. All other changed words and meaningful annotations were compared with the final reconstruction. Harmless spacing, width, table linework/reflow, IDs, import metadata, separately supplied keys and clearly separate editorial explanations are excluded. No ruby appears in the reviewed principal body that must be reconstructed as omitted reading aids.

Method 1 score is **116 = 100 + 5×2 + 2×1 + 4**: unverified provenance; two major defective fields (example labels and duplicated Q18 option identity); one minor defective field (the missing instruction target line); four materially uncertain fields (Q14, Q15, tennis opening, cleanup content). The example's additional identity uncertainty and Q18's residual alternative are not counted twice. Cleanup header and contact share one passage content field and one score event despite two cases. No missing-unit or metadata flag is charged. The score describes the actual principal, not the 86 edits to imported JSON, and is not an authenticity probability.

## Validation and preservation

[Completion verification](audit_work/completion_verification.json) records the three canonical validators: editorial/cases/fixlog with baseline and expected counts, principal catalogue and principal differences. The stage passed the same checks before committing. Exact sequential replay of all 86 new records reproduces the final JSON. All 74 scored keys, all IDs and order, historical provenance and the original fixlog prefix are unchanged. All 42 indexed source hashes pass, and the principal copy matches its canonical source hash. Existing catalogue entries, prior terminal results, the prepared queue and all 20 DEAD skips remain untouched.

Validator warnings concern changed option representations and the existing example gaining options/key. Five vocabulary option changes only adjust underline endpoints; the reading changes are two proper-name fixes, one fragment stop removal, the full Q15 first fragment and 28 source-matching terminal stops. The worked example is unscored. All warnings were reconciled against source and answer logic; none represents a changed scored key, missing item or silently shuffled option.

After this terminal result, continue the prepared queue at **N1_07_2015**. Do not reopen N3_12_2015 or earlier completed audits. Run closure, housekeeping 2, website building and publishing are not part of this unit completion.

Baseline editorial SHA-256: `981ec9518394663f6c367d7d4cf70dc2461467ab26136ef9daf919989153ded1`. Final editorial SHA-256: `f97c2184a5f44bfb202edf25a923e484a992cf99f36e7e1f00bcf16a568573dc`.


Housekeeping 2: 5 previously stale public snapshots reconciled; 0 obsolete principal rows retired. [Exact before/after, source exceptions and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/prior-reconciliation/N3_12_2015/report.json). No canonical edit.
