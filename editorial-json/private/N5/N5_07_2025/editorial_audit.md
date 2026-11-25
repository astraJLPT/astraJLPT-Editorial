# N5_07_2025 editorial audit

The full-audit record below describes the 24 September completion. The dated 25 September follow-up at the end records current hashes, targeted ★-furigana restoration and the secondary principal assessment.

Status: **audited**. All 43 written questions, 172 ordered choices, 10 section instructions and 11 content blocks were reviewed against the complete written question pages. There are 21 vocabulary questions and 22 grammar/reading questions. All 43 answer keys are retained after source comparison and Japanese reasoning. No material unresolved content or medium-confidence repair remains in this unit; the public uncertainty file is empty after review.

The preserved baseline SHA-256 is `97f203900363b20da457c04a538bedf285c919d332c2194434e0ffb7c0a727ad`. Final editorial SHA-256: `7a438840073cdcc65430168228b6922a60ec9bcc70bdfd955a444888a6c2b764`. The 4 historical root-ledger records are preserved byte for byte; 67 granular `editorial_audit_v1` records were appended. All new decisions are high confidence. Exact replay reproduces the final JSON, including imported provenance, stable IDs, ordering and archive weights.

## Identity, evidence and actual coverage

The source index was read completely. All six primary indexed sources were hashed on entry; all 17 unique indexed paths, including aliases, were rehashed at completion. Source copies and the index remain unchanged. No global candidates, other papers' candidate context, working site HTML, import tools or site generation were used.

| Source | SHA-256 | Inspection and role |
|---|---|---|
| 【试题】2025年7月JLPT日语N5真题.pdf | `de138087b9ab4d78e993f8c3360981e9bf7f61f6d1e286b777ef96dccd074a2a` | Principal: full visual reading of physical pages 1–18, including every heading, example, question, choice, passage and table. Physical 1–6 are vocabulary printed 1–6; physical 7–10 are grammar printed 1–4; physical 11–18 are grammar/reading printed 6–13. Physical 19's OCR identifies the start of listening, excluded. |
| Đề N5 07.2025 [Full] - Mark.pdf — Yuuki Bùi / JLPT MOGI | `de616de7059e372f582d1182e7261b27848e6b15ff03f390e3ccd5cb99ae0f09` | Full visual comparison of physical 3–8 and 11–23. Physical 15 is a patterned separator corresponding to omitted printed page 5, not missing questions. Physical 2 and 10 were also visually inspected and are patterned separators. Cover OCR on 1 and 9 establishes N5 2025-1 and the written booklet identities; 24 begins listening. |
| Đáp án tham khảo N5 T7-2025.pdf — Yuuki Bùi | `f17d8fb8a412defa6c76704ff0195feba7354c736587b2f63262991d45f64b1c` | All three native-text pages read, including all 43 written answer numbers, vocabulary glosses and four star-order solutions. Reference explanations were checked against the full questions, not copied mechanically. |
| 【参考答案】2025年7月JLPT日语N5真题.jpg | `52573e85cb8676c3881f34b7104879da1b56cce82e858043454b87cbe46e37ef` | Image visually read; every vocabulary and grammar/reading answer compared. Listening rows excluded. |
| Script Nghe N5 T7-2025.pdf | `efe9f209ecd2692dfe68fc3e2996b77621b378c6bd81b98d6a53306872f5567f` | Native first page and inventory identify a listening script. Excluded from written content. |
| 5分钱打印（首单免费1）(1).PNG | `ad77c1b1ca35d09b7bfd2b242a43b7b480e7dfb008ac914ae770d67ab386732f` | Image visually inspected: commercial printing advertisement, no exam content. Alias locations do not make it another witness. |

The two question PDFs have the same page-body reproduction lineage: matching glyphs, layout, line breaks and small marks, with extra Yuuki branding, covers and separators. Agreement corroborates legibility but is not independent authentication of the historical exam. There is no additional independent written-question lineage in the current index. Native text/OCR served as navigation and transcription aids; the actual written-page coverage above is visual. Hashes identify artifacts, not authenticity.

## Completeness and decisions

Vocabulary sections contain 7, 5, 6 and 3 questions, plus four complete examples. Principal physical pages 1/3/4/5 contain the examples; the two trailing pages contain questions 7 and 21. No vocabulary question or distractor wording needed repair. Deliberately incorrect choices, such as 位って／言って／信って and the readings of 四月, remain as printed. No vocabulary ruby was invented.

Grammar/reading sections contain 9, 4, 4, 2, 2 and 1 questions. The seven blocks are two examples, the two student compositions in a single cloze block, a bicycle notice, the fish-shop passage, Marta's letter and the cooking-class notice/table. Complete introductions, titles, author/recipient names, phone numbers, dates, fees and attendance instructions were reviewed. There is no missing scored content or null key.

The 67 logged field edits cover:

- 258 printed ruby groups: 242 from the manually reviewed 58-field ruby map, six in the restored star example and ten for the cooking table's special day/weekday readings. Readings are attached to the source-visible bases: e.g. 4日 and 5日 have か on 日, other listed date suffixes have にち, abbreviated 月 has げつ while the month number has がつ. All ordinary reading kanji are annotated where printed.
- The full four-position answer-sheet displays for all six examples, including the complete two-step star worked example, numbered solution 3–2–4–1, repeated reply and marking instruction. The abbreviated imported explanation was replaced with the printed instructional content.
- Source underline symbols in three vocabulary instructions, the underlined star instruction, the original hiragana in reading headings 3–6 and the printed comma after こたえは.
- Reading20's printed 書いた後、 in place of imported 書いた あと. Its meaning and key are unchanged.
- Bicycle notice title/paragraph structure, rich-text passage paragraph preservation and the cooking notice's two-line entries. The invented table-header words クラス／作るもの／日／時間／料金 were removed; all actual table data and relationships remain.

The 25 September follow-up restores visible ruby on 家 (Q10), 私／作 (Q11), 弟／私 (Q12), and 行 (Q13) in scored star stems. The additive schema rule accepts rich content with four separated base-text slots and exactly one star. Base wording, slot positions, choices and keys remain unchanged; see below.

The cooking-utensil drawing, notice pins and folded-paper outline are decorative and carry no answer information; text and meaningful table structure are preserved. Dates and weekdays are transcribed as given in the exam notice, without normalizing them to a presumed real-year calendar.

## Answer reasoning and unchanged anomalies

Both answer sources agree with all editorial keys:

- Vocabulary: `2 3 1 1 4 2 4 / 2 2 1 3 4 / 1 4 2 1 3 3 / 2 2 1`.
- Grammar/reading: `4 3 4 1 2 3 2 1 3 / 3 4 1 2 / 1 4 3 2 / 4 1 / 3 2 / 4`.

These were also tested against the complete items. Vocabulary13 requires a quiet voice; 14 takes たいせつな with the mother's watch; 15 needs a mass unit; 16 is trouble after forgetting a wallet; 17 gives straight-ahead directions; 18 counts magazines with さつ; 19–21 test fruit, spaciousness and walking. Grammar1 distinguishes duration ぐらい from clock-time ごろ; 2 uses arrival destination に; 3 uses などの; 4 uses the nominal copula connective で; 5 extends an invitation with も; 6 uses まだ; 7 nominalizes 青い with の; 8 uses きらいでした; 9 offers to turn on the air conditioner.

The star orders are Q10 `4–2–1–3` (に 大きい さくらの木 が, star in fourth slot), Q11 `3–2–4–1` (きのう の 夜 は), Q12 `2–3–1–4` (が あげた ぼうし を), and Q13 `1–3–2–4` (から じゅぎょうの あとで とりに). The last three have the third slot starred. No slot, option order or key changed.

The cloze narratives establish a chronological それから, past affirmative enjoyment 楽しかったです, a visit to a friend with に, and the friend's future arrival 来ます. Reading18 directs a prospective bicycle recipient to call. Reading19 prioritizes tasty fish, selecting the shop next to the bookstore despite its price. Reading20's April15 letter places the new job in May; the return home is already past and the September party is in the writer's home country. Reading21 is chiefly gratitude, expressed twice, rather than congratulations, welcome-back or a party invitation. Reading22 requires both Thursday afternoon and vegetables: only class④ on26日 meets both;①/② are morning,③ is afternoon sweets.

The Yuuki reference prose for vocabulary21 repeats a form of the stem instead of the option wording. Its grammar1 explanation says 毎朝 while both full question copies clearly print 毎日, and grammar2 has the stray text 花川は駅. These are reference-explanation errors; the actual question wording and matching numeric keys are retained. They do not leave a material ambiguity after both full question pages and the question logic were checked.

## Historical material and validation

The unit-local candidate TSV was read completely: a header only, zero written rows. No global fallback was opened. The historical audit and all four ledger records' identities, reasons and context were reviewed. The two full-part creation records were reassessed through the complete baseline and source-page audit; their old high-confidence designation was not inherited. Two navigation-link records concern site navigation outside this written-content output. The old audit's 18-page/43-question coverage claim was independently checked; its obsolete HTML tools and execution instructions were not followed.

The unchanged validator passed with baseline, local cases/fixlog and evidence-derived counts `vocab=21`, `reading=22`. Its 10 warnings concern options for reading Q7,10,11,15,17,18,19,20,21,22 changing representation from plain text to ruby. Exact per-option comparison after removing ruby/markup verifies every option's base text and order are unchanged; all keys match both sources. There are no errors, null keys, empty choices, source-provenance changes or count mismatches.

Independent checks also establish exact ledger replay, preservation of the historical ledger bytes, stable IDs and ordering, all 43 key values, all 172 option texts, the four star permutations, table relations and all indexed hashes. Private artifacts include `new_edits.json`, `ruby_review.tsv`, `ruby_application.json`, `substantive_changes.json`, `validation_final.json`, `verification_final.json` and `source_hashes_final.json`. The unit result is recorded before queue handling. This is the active goal's inclusive endpoint, so state remains `N5_07_2025`; final run reconciliation follows below before overall completion is set.

## Final scoped run reconciliation

The active goal range N1_07_2025 through N5_07_2025 inclusive is complete. Final read-only reconciliation checked all five root JSON hashes against progress, all baseline hashes, imported provenance, exact replay of all 450 new ledger records (including the N3 example placement), all public current values and medium-fix links, evidence-derived counts, audit-note paths and endpoint state. There are 310 questions, nine provisional fixes and seven retained ambiguities across 16 public cases; no paper in this scope is incomplete or blocked. The N2 combined validator still reports its two documented HTTP(S)-URL detector false positives; every match was rechecked within a protocol prefix, and its separate structural run passes. No other validation error remains. Raw reports and the detailed reconciliation are in `audit_work/run_validation_N*_07_2025.json` and `audit_work/run_verification.json`.

Overall progress is `completed` for this active goal range, with the provisional content explicitly retained. State remains `N5_07_2025`. The longer preparation inventory through N5_07_2023 contains 20 later pending entries outside this run; they are not claimed complete.


## Follow-up: scored ★-stem furigana — 25 September 2026

Revisited 4 scored ★ stems. Principal physical pages: 9, 10; complete comparison witness physical pages: 13, 14. Exact paths, hashes, item/page maps and observed readings are in [the focused review](audit_work/star_furigana_20260925/review.json).

Restored 家, 私/作, 弟/私 and 行 in Q10–13 respectively.

Applied 4 high-confidence stem edits, adding 6 ruby groups. Exact base text (including whitespace), four-slot positions, all choices/keys, IDs, imported provenance and every unrelated field are unchanged. Original ledger bytes are preserved; the new records replay exactly from the new byte-preserved follow-up baseline. Original full-audit baselines/reports remain historical evidence.

Follow-up baseline SHA-256: `7a438840073cdcc65430168228b6922a60ec9bcc70bdfd955a444888a6c2b764`. Current editorial SHA-256: `48ff34f01724957356650f58f98e85b57e37705fdf13d7d84573225ae9d3124d`.

The current structural validator passes with evidence-derived counts; no new baseline warnings. The 21 regression tests pass, including inverse rendering. Private previews were visually checked for source-supported ruby placement and slot/option visibility. The combined public-case/ledger check passes. The unit retains 0 public cases.

Separate catalogue assessment: principal `src/日语JLPT历年真题/N5真题（2010-2025.12）/【N5真题】2025年7月/【试题】2025年7月JLPT日语N5真题.pdf`, SHA-256 `de138087b9ab4d78e993f8c3360981e9bf7f61f6d1e286b777ef96dccd074a2a`, index **100** under [method 1](../../principal_uncertainty_method.md). This is unverified provenance plus the documented components in [the catalogue](../../principal_uncertainty_index.json), not authentication or a new evidence-priority rule.

See [scoped follow-up verification](../../pilot_followup_20260925/verification.json). The completed five-paper scope and queue state are unchanged.


## 2026-09-25 — principal-differences and ancestry reporting

Current reporting: 1 public departure record(s) in [principal_differences_N5_07_2025.jsonl](principal_differences_N5_07_2025.jsonl), 0 public uncertainty case(s), principal index **100**. The current exam JSON, source index and correction ledger are byte-for-byte unchanged by this reporting step. The catalogue is now [JSON](../../principal_uncertainty_index.json); [ancestry observations](../../ancestry_record.tsv) are separate low-effort historical evidence. Full comparison scope, fresh physical-page checks, exclusions, source/JSON hashes and validation are in [the reporting pilot](../../pilot_records_20260925/review.md). Its register covers observed current departures and does not certify exhaustive equality.


## Reference scans finalization — 5 October 2026

No editorial edit: both printed 行/い ruby groups were already present. Retired stale PD-001 and corrected the public case’s omission claim. The case stays OPEN under the existing user instruction. Every editorial byte remains unchanged.

This is a bounded execution of the user-approved suggestions, not another full-paper audit. Reused the completed page review and rechecked physical pages 11 at the verified principal identity. No principal, source index, answer key, option order, item ID or import metadata changed.

The [frozen before manifest](audit_work/reference_scans_finalization/before/manifest.json) preserves the editorial, both public registers, root ledger, audit note, principal copy and catalogue/progress entries. All older baselines remain intact. The root ledger appends 0 `editorial_audit_v1` edit record(s) and one separate reconciliation acknowledgement; it retains all prior bytes. Retired difference IDs are historical and must not be recycled.

Final editorial SHA-256: `48ff34f01724957356650f58f98e85b57e37705fdf13d7d84573225ae9d3124d`. Exact replay reproduces the complete final JSON. Editorial validation with this baseline, current cases, root ledger and evidence-derived counts (21 vocabulary / 22 grammar-reading questions) passed; principal-difference validation passed. Warnings: []. Source agreement does not close user-designated open cases.

[Run record](../../audit_runs/reference_scans_finalization/README.md) · [unit result](../../audit_runs/reference_scans_finalization/N5_07_2025_result.json) · [exact edits](../../audit_runs/reference_scans_finalization/editorial_changes_N5_07_2025.jsonl) · [validation](../../audit_runs/reference_scans_finalization/validation/N5_07_2025.json).


## Housekeeping 2 — 5 November 2026

Resolved N5_07_2025-PD-001 without an editorial or ruby edit. The primary agent inspected approved source physical pages 11–12 (printed 6–7), the complete two-composition cloze task, all choices 14–17 and the live markup. Both 行/い spans are printed and already present. Context and answers 1/4/3/2 agree; the readings do not answer a cloze blank. The old omission allegation is rejected, and the already-retired principal departure stays retired.

This is a source-agreement case resolution under the final-housekeeping authority, not a claim of issuer authentication or a new full-paper audit. Source aliases/earlier reviews count as one lineage. No independent conflicting witness is needed to settle the already-legible exact spans. Principal score 100 and all source-concern events remain unchanged.

[Full before/after case, source hashes, visual scope and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N5_07_2025/disposition.json). Baselines and previous fixlog bytes are preserved.
