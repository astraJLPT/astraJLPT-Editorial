# N2_07_2025 editorial audit

The full-audit record below describes the 24 September completion. The dated 25 September follow-up at the end records current hashes, targeted ★-furigana restoration and the secondary principal assessment.

Status: audited_with_uncertainty. Full written coverage and focused investigations are finished; seven public cases accompany the reconstructed paper. None of the reproductions is authenticated as an official original.

## Identity, baseline and coverage

Preserved baseline `audit_work/editorial_before.json` SHA-256 `cabc821e651bf3084be511ea0bfcbf8e1a6b53b9253090906246c3d342e9d05a`. Final SHA-256: `8e4b44a729cf03b148526eb135b41289d634367ad544d931a080a1faf5758a19`. Historical source provenance, stable IDs, section/item order, all71 answer keys and all option order are unchanged. There are51 vocabulary/grammar questions,20 reading questions, two vocabulary blocks (example/cloze) and12 reading blocks across14 sections. All items, choices, passages, instructions, names, notes, meaningful markup and unchanged anomalies were read against written sources. No unknown option, missing scored item or null key remains.

Physical page numbers below are one-based. The principal image reproduction identifies July2025 N2/25-1-II, skips printed7 and19 and ends written content at physical31/printed33. These printing inconsistencies are retained as source cautions, not invented missing questions. All indexed24 source files were rehashed before installation and match index identities. Full paths/hashes remain in the immutable index.

| Source (local label and hash prefix) | Actual review | Lineage and limitations |
|---|---|---|
| 【试题】2025年7月JLPT真题N2.pdf (pdf13, cdc95d99) | Full visual physical1–31, all written questions; focused enlarged glyph/example/gas/math/contact crops | Principal page-image reproduction;43 physical pages, listening after31 excluded. |
| N2-T7-2025 完成版 - Mark.pdf (pdf1, ca42bf14) | Full visual physical1–31, including blank7; all written questions | Yuuki/MOGI retype. Changes names to ユーキ/モギ and contact details to distributor branding. Omits worked example. Shared ancestry cannot be excluded. |
| 2025年7月能力考N2真题+答案.pdf (pdf14, 64618816) | Full visual physical1–15 including cover/key | Reorders early items and repeats several retype mistakes. Omits final notice. Useful alternate wording, not an independent authoritative vote. |
| 2025年07月日语N2真题试卷（高清打印版）.pdf (pdf11, 6d503c14) | Full visual written physical2–23, including inserted notice image22 | Chinese retype; many shared errors with compressed retype. Notice text replaces university URL with sifu branding; embedded image preserves it. |
| 2025年07月N2真题.pdf (pdf4, 08f4b31f) | Full written OCR/alignment against pdf11; original physical2,3,6,9,11,15,18–22 visually checked | Same body/layout family as pdf11, no inserted notice-image page. Meaningful alignment differences investigated. |
| Munja 2025-07_N2.json (39ab7a39) | All71 questions/options/keys and13 nonexample blocks aligned and every difference read; final notice image b0491444 viewed fully | Transcript has corrupted math passage and malformed distractors. Zero-based keys mapped to one-based, all agree with baseline. Notice image may share a reproduction ancestor. |
| Đáp án tham khảo N2 T7-2025.pdf (pdf3, c2eed801) | All6 native pages read; all71 written keys | Keys agree; explanatory text considered as fallible reasoning. |
| 2025年07月N2答案解析.pdf (pdf6, 946f004a) | All17 native pages read | All written 正解 headers agree, but Q43/44 ordering explanations are wrong and Q71 concluding2 contradicts its own header4. |
| 2025年07月日语N2答案解析.pdf (pdf12, 7c8e2b7a) | All4 physical pages visually read | All71 keys agree; actual star orders independently confirmed. |
| Three answer images (5e0aa394, d4520acd, 3722e07a) | All visually read | Identical chart design/shared lineage. Q53=3 is contradicted by question reasoning and other keys; all others agree. |
| 2025年7月N2阅读译文.pdf (pdf8, b8519055) | Visual physical1,3,5,7–10 | Chinese translation useful for notices/child/math interpretation; cannot establish exact Japanese particles. Adds an unsupported year; do not import it. |
| Archived original HTML vocab/reading (39667837, 3666bbde) | Focused original gas/child/course contact passages, plus historical reports | Import lineage with damaged cells/URL, not independent proof. Working HTML untouched. |

Listening PDFs2/5/7/10 and listening HTML are excluded. The shared blank answer sheet, scoring workbook and printing advertisement establish no written content. Written explanation/translation files were examined despite parent folders mentioning listening. The complete source files themselves were not edited or OCRed in place. No tool, import or site file changed.

## Decisions and changes

The101 granular field records comprise22 text/format/example/footnote edits,76 fields with printed furigana, and three medium wording edits. Existing89 log records are preserved byte for byte;101 appended gives190 total. Replaying the exact before/after sequence against the baseline reproduces the whole final JSON. All76 ruby-only changes leave base text identical. Eight options have base-text changes: Q10 支援→支接; Q28 開催国→開催地; Q54 感しられる→感じられる; Q62 option1 and all Q69 choices regain final full stops. All other option warnings reflect ruby alone. No answer target was supplied with newly invented readings. The 25 September follow-up restores printed 丁寧/梅雨/寝坊 ruby on Q43/44/47 under the additive ★-stem rich-content rule; see the dated follow-up below.

Q10 is a significant reversal of an early scratch assessment: enlarged principal/Yuuki page2 clearly prints 接 in 支接. Munja and every other question retype agree. The four-option matrix 支接/施接/支設/施設 intentionally contains nonwords; correcting it to real-word 支援 was unjustified. New high-confidence edit restores 支接, accepting V050. Q6 液って versus 渡って and Q9 掘って versus 掴って remain historically ambiguous distractors: all alternatives are wrong for しめって/けずって, so language correctness does not decide. Retain principal/Yuuki readings with public low-confidence cases.

Q13 今回 is supported by principal/Yuuki/compressed retype/compiler and the past-accident context; do not replace it with 今度 from high-resolution/Munja. Q19 締め出した is supported and the retype 揉め出した is corruption. Q28 開催地 is preferred over 開催国 on primary/Yuuki/compiler evidence, but either leaves 熱中 an incorrect collocation with 世界の関心; medium confidence/public case. Q34 key4 おいでくださり expresses gratitude for the benefactor's visit. Compilation key2 is a key error; all other keys support4. Yuuki 図書館で is a contextual replacement; principal 旅館で retained. Q47 それでも is supported and coherent against Yuuki それまで.

Every grammar/cloze key was tested in its full sentence. Star orders are Q43:2–4–3–1, Q44:3–2–4–1, Q45:1–3–2–4, Q46:2–3–1–4, Q47:4–1–2–3; use the printed star position rather than an explanation's incorrect ordering. The complete 山田 worked example is restored with semantic two-row slot layout and answer2 marked, agreeing in principal9/compiler5. Cloze heading ends51, not a retype's mistaken52. Legitimate wrong choices and source-supported kana/kanji variation were preserved.

Reading Q53 retains4: the letter asks for another delivery of existing goods for sale, not creation of a new souvenir as chart option3 would imply. Munja, pdf3/6/12 and compilation key all support4. The shared chart is one error lineage, not three votes. Q68 retains4: the passage objects to forcing a new concept into an existing category to feel that one understands; option3 about knowingly accepting wrong information is different. Q70/71 remain3/4 after every course time, practical-work requirement and deadline/telephone condition was checked. The final notice is a semantic table with source-supported entries; no image-only substitute.

New reading repairs restore the unmatched initial quote, radio analogy sentence boundary, section11's four-passage range, broken words, full underlines, supported punctuation/footnote wording, and nine missing definitions (elephant4 and child5). Both complete witnesses show those definitions, so old omission dismissals are reversed. The medical notes read しっかりと理解する and 死守する. The long passage's first underline ends after こと before だ, while Q67's quotation includes だ; each original boundary was inspected. Both こっち occurrences and the nested Eureka punctuation are supported. A/B 一つだ。だが is retained as an attested minor segmentation variant; the later full stop after からだ is restored.

Child passage というのでいい is preferred at medium confidence over というのもいい. The page image, Yuuki, both retypes, compiler and archived HTML showで; Munja and the detailed explanation showも. Sufficiency expressed by の+でいい fits それでいい and later curiosity, but additiveも is also natural. Long-reading 全く新しい is restored provisionally from a clearly legible primary crop: other retypes omit全く, and translation 全新 cannot authenticate the exact Japanese qualifier. Full paragraphs, options and language implications were compared before making either decision.

The seven public cases are three provisional fixes (開催地,ので,全く) and four retained disputes (液/渡,掘/掴,gas contacts,course telephone). Each contains exact current values, strongest alternatives, actual focused attempts, recognizable source identities/hashes/pages, lineage cautions and residual uncertainty. Gas .com/063-554-3169 is retained over .co and compiler062-664-3169; the course number021-543-0101 is retained over archived087-965-5014. Arbitrary historical contact strings cannot be settled by grammar or contemporary ownership. Distributor Facebook/0204-2000-8688 and sifu substitutions are identified branding, not credible original contacts.

All89 historical log records were read. Prior high-confidence claims were not inherited: seq292's のも decision is reversed provisionally; seq774's あっち had already been reversed, and presentこっち is upheld; seq787's telephone is now publicly uncertain; seq788's sifu URL had already been replaced and the university URL is upheld; seq8444's example was incomplete and is now fully restored. Seq8440–8443 alternatives were reassessed; seq8445–8464 substantive cloze/contact/math/table restorations are largely upheld. Listening seq8434–8439 is outside scope. Earlier notes remain in legacy files; in-progress root checkpoint is preserved separately.

## Validation and documented detector exception

The standard structural validator was run against final JSON, baseline, evidence-derived counts51/20, full root fixlog and all seven public cases. It verifies the question/options/keys/IDs, balanced rich HTML, provenance, exact case current-values and all medium-log links. Its raw combined report is saved as `audit_work/validation_final.json`: valid=false solely because cases6 and7 contain public HTTPS URLs. The path regex `[A-Za-z]:[\\/]` matches the final protocol letter plus colon/slash (`s:/` or `p:/`). These are NOT local paths. Every regex hit was inspected and independently asserted to lie wholly inside an HTTP(S) protocol; exact matched contexts are saved in `public_path_false_positives.json`. Public prose contains no private references. URLs and exact current values were preserved, and the tool was not modified to hide this defect. This is a documented manual exception to two false path errors, not a claim that the combined command returned success.

The separate unmodified JSON/baseline/count structural run passes with zero errors; saved as `validation_structure.json`. There are51/20 questions,204/80 options,2/12 blocks and zero null keys. All23 baseline option-change warnings are accounted for by the eight exact content changes and printed ruby described above, with order and keys independently asserted unchanged. Exact101-edit replay, public case linkage/current values, historical log byte preservation and all indexed hashes pass. Structural checks do not authenticate historical readings; the seven public cases remain required deliverables. No unresolved content validation defect is being silently suppressed.

Unit result is written before state advances to N3_07_2025. Preliminary scratch checkpoints are superseded by this note, especially the mistaken early rejection of 支接.

## Complete candidate disposition register

All231 unit-local written rows (R001–147 and V001–084) were read. Listening was filtered before loading. Content, not historical line offsets, mapped them to current IDs. This register covers every row exactly once; the script asserts complete coverage.

| IDs (prefix2025-07-N2-) | Reassessed disposition |
|---|---|
| R-001-013 | Routine detector false positives at Japanese word/particle boundaries; preserve supported wording. |
| R-014 | Duplicated short-text (1) label was already repaired; sequence checked. |
| R-015,130 | Reject Munja omitted もの and added/removed particles; remove the unmatched opening quote as a new supported repair. |
| R-016,131 | Duplicated また and Chinese 开 already corrected; complete letter and its key checked. |
| R-017,132 | Reverse prior punctuation dismissal: restore 小説のように。; repair 感しられる to 感じられる in Q54 option2. |
| R-018 | Gas URL punctuation previously repaired. Exact .com/.co and telephone readings remain public uncertainties after full source comparison. |
| R-019,087 | Correct ので retained in gas question; no edit. |
| R-020,133 | Reject 専門 for 部門; restore broken-word spaces in どんな and 人たち. |
| R-021 | Prior (3) decision was wrong: four passages establish range (1)–(4); corrected heading. |
| R-022,134 | 頭 is supported over 首. Full elephant passage checked and four previously omitted footnotes restored. |
| R-023,088 | 重さ is correct; retain. |
| R-024,090 | 脳 is correct; restore printed ruby without changing base text. |
| R-025,135 | 見て already repaired correctly; entire writer passage checked. |
| R-026-029,092-095 | Q59 choices are unpunctuated から clauses in the principal page; retain their wording and endings. |
| R-030 | Child passage text was present but five footnotes were missing; restore them and provisionally choose ので over のも. |
| R-031,097 | Q61 option punctuation already supported; retain. |
| R-032,098 | Restore printed terminal full stop in Q62 option1. |
| R-033,136 | ひとり and 意味で already correct. Restore footnote と and lemma 死守する. |
| R-034-041,100-107 | Medical Q63–64 choice punctuation differences do not justify wording changes; printed 患者 ruby restored. |
| R-042 | A/B heading correct; both passages and two questions complete. |
| R-043,137 | Retain 一つだ。だが, attested in Yuuki/retype; restore the sentence stop after 戦略が分かるからだ. |
| R-044-047,109-112 | Q65 choice endings without added punctuation match the reviewed source; retain. |
| R-048,114 | Q66 option1 was already restored correctly. |
| R-049,115 | ほうが is correct; no further edit. |
| R-050 | Long-reading heading style only; retain. |
| R-051,065,138 | Reject corrupt Munja whole-passage replacement. Both こっち occurrences are supported. Restore underlines/notes and provisionally 全く; do not change Eureka wording. |
| R-052-054,116-118 | Q67 choice endings are supported; no added punctuation. |
| R-055,119 | Munja omission of と is corruption; preserve the complete option. |
| R-056,120 | どの is supported; retain. |
| R-057-059,121-123 | Q68 choice punctuation only; wording/key4 retained after full interpretation. |
| R-060-063,124-127 | Restore all four printed Q69 terminal stops; earlier かい/十る/ほうか corruption already repaired. |
| R-064,129,139 | Wrong video-contest heading and circled course reference already fixed; complete notice/table verified. |
| R-066-071 | Historical HTML/parser diagnostics are not exam-text errors in schema-v2 content. |
| R-072 | Semantic table already restored; all cells, dates, times and conditions checked. |
| R-073 | Q68 remains4: misclassifying an unknown concept under an existing box, not knowingly accepting a wrong idea. |
| R-074 | Website route request outside editorial scope. |
| R-075 | Reported missing Q61 passage is present; newly recovered five notes are separately logged. |
| R-076-077,079 | Non-content thanks/feedback; no editorial action. |
| R-078 | Prior dismissal was wrong: elephant four and child five explanatory notes were absent and are restored. |
| R-080 | PDF download request is not an additional exam item. |
| R-081 | Reported long-passage truncation already repaired; full source reviewed again. |
| R-082 | Listening request excluded. |
| R-083 | 今回 supported; source variant 今度 does not outweigh the complete page and context. |
| R-084 | 選手 already correct. |
| R-085 | Reject 致学 recognition error. |
| R-086,096 | Q61 stem was already correctly restored. |
| R-089 | Elephant question punctuation retained as printed. |
| R-091 | Restore the printed full stop in Q59 stem. |
| R-099 | によると is correct; no change. |
| R-108 | どれか is correct; no change. |
| R-113 | Q66 stem already complete and correctly restored. |
| R-128 | Q70 punctuation source-compatible; retain. |
| R-140-144 | Notice word/鉢/守り/circled reference repairs already supported; keep. |
| R-145 | Retain021-543-0101 against archived087-965-5014 provisionally; public uncertainty after all notice/contact witnesses checked. |
| R-146 | Nomura university URL supported by notice images; reject identifiable sifu distributor substitution. |
| R-147 | Eureka wording and nested punctuation match the principal image; retain. |
| V-001-004 | Routine particle-boundary false positives; no edits. |
| V-005,018 | Heading style differences only. |
| V-006-009 | Extra heading separator already repaired. |
| V-010,051 | 戻 spelling variant does not establish a correction. |
| V-011 | ゆっくり is correct. |
| V-012 | よい heading already corrected. |
| V-013,053 | たんす is supported. |
| V-014,054 | びりびり is a deliberate distractor; preserve. |
| V-015,055 | Q28 毎日/ばかり/着たがる already repaired; new 開催地 correction is medium/public. |
| V-016,057 | ことが is supported. |
| V-017,058 | スーパー is supported. |
| V-019 | お越しになり is supported; Q34 key4 confirmed. |
| V-020-021,063-064 | Q35 らしく and いたら already correct; reject retype corruption. |
| V-022-024,067-069 | 乗 spellings are intentional choices; preserve. |
| V-025-026,084 | Cloze heading/key range48–51 is correct; reject source typo48–52. |
| V-027,081-083 | Cloze 脳, title の and punctuation already repaired; five printed ruby targets restored. |
| V-028-033 | HTML/parser/template issues do not identify missing content in current JSON. |
| V-034 | Duplicate Q68 key allegation; retain4 after discourse review. |
| V-035 | Website route request outside scope. |
| V-036 | Duplicate missing-Q61 report: passage present, notes now restored. |
| V-037-038,040 | Non-content feedback/thanks. |
| V-039 | Request for notes is valid: nine missing footnotes now restored. |
| V-041 | PDF availability request; no new scored item. |
| V-042 | Math passage truncation already repaired and rechecked. |
| V-043 | Listening request excluded. |
| V-044 | 今回 already supported. |
| V-045 | 選手 already correct. |
| V-046 | Reject 致学 recognition error. |
| V-047 | Q61 stem and 子ども already repaired. |
| V-048 | Reject Chinese 每 glyph. |
| V-049 | Q7 増える already restored; printed ruby now added. |
| V-050 | ACCEPT 支接: enlarged principal/Yuuki glyph is 接. Replace baseline 支援; earlier checkpoint rejection was a visual misreading. |
| V-052,061 | り is supported; no change. |
| V-056 | 和やか heading already correct; printed ruby restored. |
| V-059 | 建設 supported. |
| V-060 | ございます supported. |
| V-062 | 来る is a permissible attested variant; no unnecessary rewrite. |
| V-065 | Q36 punctuation only; retain. |
| V-066 | Q37 ので supported. |
| V-070 | 司会 supported. |
| V-071 | Q42 が supported. |
| V-072-075 | Star-slot typography only; preserve four separated plain slots and correct answer mapping. |
| V-076 | Q47 する already repaired correctly. |
| V-077-080 | Cloze placeholder questions are present and correctly linked; no missing items. |


## Follow-up: scored ★-stem furigana — 25 September 2026

Revisited 5 scored ★ stems. Principal physical pages: 9, 10; complete comparison witness physical pages: 10. Exact paths, hashes, item/page maps and observed readings are in [the focused review](audit_work/star_furigana_20260925/review.json).

Only Q43 丁寧, Q44 梅雨 and Q47 寝坊 receive ruby; Q45/46 have none to restore.

Applied 3 high-confidence stem edits, adding 3 ruby groups. Exact base text (including whitespace), four-slot positions, all choices/keys, IDs, imported provenance and every unrelated field are unchanged. Original ledger bytes are preserved; the new records replay exactly from the new byte-preserved follow-up baseline. Original full-audit baselines/reports remain historical evidence.

Follow-up baseline SHA-256: `8e4b44a729cf03b148526eb135b41289d634367ad544d931a080a1faf5758a19`. Current editorial SHA-256: `19bf25398b3ca094b3931d8211afea4067d6d809a8d2c0d72ceb01ad5f16aabb`.

The current structural validator passes with evidence-derived counts; no new baseline warnings. The 21 regression tests pass, including inverse rendering. Private previews were visually checked for source-supported ruby placement and slot/option visibility. The combined check still reports only the two previously documented HTTP(S)-URL detector false positives; every match was independently verified inside a protocol prefix. The unit retains 7 public cases.

Separate catalogue assessment: principal `src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/2025年7月/【试题】2025年7月JLPT真题N2.pdf`, SHA-256 `cdc95d992bce7bb212deb9e732a33095d2112b7f5bfc1337d4c117d0268f52b0`, index **109** under [method 1](../../principal_uncertainty_method.md). This is unverified provenance plus the documented components in [the catalogue](../../principal_uncertainty_index.json), not authentication or a new evidence-priority rule.

See [scoped follow-up verification](../../pilot_followup_20260925/verification.json). The completed five-paper scope and queue state are unchanged.


## 2026-09-25 — principal-differences and ancestry reporting

Current reporting: 1 public departure record(s) in [principal_differences_N2_07_2025.jsonl](principal_differences_N2_07_2025.jsonl), 7 public uncertainty case(s), principal index **109**. The current exam JSON, source index and correction ledger are byte-for-byte unchanged by this reporting step. The catalogue is now [JSON](../../principal_uncertainty_index.json); [ancestry observations](../../ancestry_record.tsv) are separate low-effort historical evidence. Full comparison scope, fresh physical-page checks, exclusions, source/JSON hashes and validation are in [the reporting pilot](../../pilot_records_20260925/review.md). Its register covers observed current departures and does not certify exhaustive equality.


## Housekeeping 2 — 5 November 2026

N2_07_2025-PD-001: resolved. Retain the user's kana くる in 帰ってくることもある. The complete approved question, instruction and all choices were visually checked, and the fixed stem agrees with the current text. The former 来る spelling is grammatically possible but not printed here. Close the source-agreement identity under final-housekeeping authority; keep the existing four choices, key and typography unchanged.

The father apparently makes a habit of walking for health and sometimes walks home for an hour. 歩くようにしているらしく (option 3) links the observed habit to the example; the competing intention, means and conditional phrases do not supply that connection. The return-motion phrase is fixed outside the blank. 来る would remain intelligible, so grammar is not historical spelling evidence; the actual page prints くる. The current key is 3 and all choices match.

Unchanged 109. The pagination flag and seven distinct uncertain targets do not charge this spelling.

Rebound 4 older case snapshots to existing v3 typography only; these are not counted as substantive reviews.

No editorial, ruby or principal-departure content changed. Historical fixlog bytes and all case identities are retained. [Source hashes, before/after cases and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N2_07_2025/disposition.json).


HK2 additional written-page reviews, 5 November 2026: 7 record-only decisions, no canonical edits. Exact sources, competing evidence and all before/after records: [N2_07_2025](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/later-direct/N2_07_2025/report.json).
