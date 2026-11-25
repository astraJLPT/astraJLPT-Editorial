# N3 July 2024 editorial audit

Status: audited_with_uncertainty.

## Start (2026-09-25)

Live state was confirmed after N2 closure and principal-reporting validation. Byte baselines of the current editorial JSON, root fixlog and public cases were preserved before editing. The current index was read in full. Listening and generic answer/scoring files are outside written-content reconstruction. No principal has yet been selected.

## Working checkpoint: original-page review

All 35 indexed file hashes were verified. The complete baseline was read: 35 vocabulary and 38 grammar/reading questions, all 292 choices, ten blocks, headings, keys and five optional explanations. All 83 written candidate rows (R001–R041 and V001–V042) and all 35 written records in the 38-row historical ledger have now been read. Three listening history records are excluded from content adjudication. Historical claims are being rechecked, not adopted.

Original images inspected so far: compact `2024年7月N3真题.pdf` (cae148d3…ed308), physical 1–13, including its complete written material at 2–13; Yuuki Mark Ver 2.0 (0180363a…c3560), physical 1–4, all vocabulary; 45-page booklet `2024年07月日语N3真题试卷.pdf` (75c9f8fb…1e7), physical 1–3, cover/back and vocabulary 1–8; compilation 【2】 (371d4af3…4697), physical 3–4, cover and first vocabulary page. Native extracts are aids and not additional visual coverage. The compact emits xref warnings, but the inspected written bodies are legible. 【2】 pages 3–4 share the compact's layout/body and rare readings; independent corroboration has not been established.

New issues under investigation include V7 考えて/教えて; V10 choice 1 腕/胸; V11 choice 4 違週/遠週; compact V12 duplicates 寒かった as choices 1/4; V16 苦手/下手; V17 走った/走ってきた; V18 missing copular connection, compact で; V20 missing がよくて; V31 choice 2 missing が and choice 3 polarity conflict; V32 choice 4 会社中て/会社内で; V35 choice 4 tense. Usage items V31–35 omit source option underlines. Grammar G5 高校/大学 and G8 option versions need reassessment. Example answer bubble in compact is inconsistent with the correct order (3,2,4,1); its heading 解のしかた also looks defective. G14/G16 explanations differ from the actual option strings. Reading G24 choice 4 is an unrelated teacher statement in the baseline but a relevant sports-definition distractor on compact physical 8. G24/G25/G28/G29 drop interrogative dakuten; G30 drops the quoted underline. Compact long passage physical 11 lacks the second referenced underline and numbers the third reference ②; baseline and other versions require comparison. The notice on physical 13 has selective ruby 封筒/ふうとう and 期限/きげん. No root editorial, fixlog or public-case edits have yet been made.

Next: read the remaining materially distinct witnesses, align Munja written content, inspect useful explanation/key pages and notice images, adjudicate each conflict, then generate exact edits/cases/principal differences and validate. Unit remains in_progress; this checkpoint is not a coverage-completion claim for unviewed witnesses.

## Completed evidence review and proposal (2026-09-25)

This section supersedes the provisional readings and limited coverage in the working checkpoint. In particular, the compact family's V12 option 4 is **塞かった**, not 寒かった; V25 option 2 is **ときとき**, not ときどき; V27 prints **カーブレて**; V35 option 4 prints **繁張**. Focused original-page crops established these readings. The sports-management passage says **考えからだ**, so there is no 考えからだ／考え方だ dispute at that location. The notice also has **確認／かくにん**, in addition to 封筒 and 期限. These corrections to preliminary observations were made before committing the editorial proposal.

### Identity, selected principal, and actual coverage

The title, level, question sequence, repeated item content and written answer tables consistently identify N3 July 2024. There is no authenticated issuer copy or acquisition chain. Fictional dates in the reading notices are task conditions, not a claim that their weekdays match the 2024 calendar. Listening is excluded.

Selected principal: `src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N3真题/2024年7月/【2】2024年07月N3真题.pdf`, SHA-256 `371d4af36b6b598c6dfd4e9fdf763ff8ad67bd6133930b6590f15e93a98a4697`, initial Tier 2, 30 physical pages. Original-page review covers physical **1–15**, with only the written answer row on the upper part of page 2 in scope. Page 3 is the cover; pages 4–15 contain the complete written questions, instructions, worked example, passages, table and notice. The lower listening table on page 2 and listening from page 16 are excluded. The source does not dictate every reconstruction choice.

The 21-page compact edition was initially the working coverage reference, but no principal catalogue entry had been published for it. The 30-page compilation is selected because its written bodies are cleaner to inspect, it includes the written answer table, and it preserves ら in 夜になったら where the compact edition loses it. Its many other shared defects remain visible and recorded. This is a legibility/coverage decision, not authentication or an independent vote against other witnesses.

| Indexed witness | Original or native content actually reviewed | Findings and limits |
|---|---|---|
| `pdf_14`, 【2】, hash `371d4af36b6b…` | All original written regions at 1–15; focused crops on 4–7, 10–15, and upper 2 | Selected principal. All 73 embedded written keys checked. Clear copied/reformatted content, but no documented acquisition account sufficient to authenticate it. |
| `pdf_4`, 2024年7月N3真题.pdf, `cae148d3d503…` | Original physical 1–13, complete written 2–13; focused vocabulary and usage crops; native written extraction | Same compact question-body family, including rare errors 塞かった／ときとき／カーブレて. Emits missing-xref warnings; inspected written bodies remain legible. Listening boundary at 14 excluded. |
| `pdf_3`, Yuuki Mark Ver 2.0, `0180363a99c7…` | **All original physical 1–19**, complete written questions, all options, all passages and notice; usage crop at 4 | Materially different retype. Several shared corruptions and altered choices; the unrelated teacher distractor and branded substitutions are not accepted merely because the file was initially Tier 1. Listening 20 onward excluded. |
| `pdf_16`, 2024年07月日语N3真题试卷.pdf, `75c9f8fba356…` | **All original physical 1–30**, including covers/separators, complete available written regions and their omissions | Booklet appearance does not establish authenticity. Numerous copied or retyped errors: damaged grammar stems/options, 私の道, age gap 20 instead of 50, displaced cloze blank, shortened passages, missing 芯, wrong unit 0.5m, misplaced ski-school heading, and truncated notice footer. Its selective instruction/example ruby remains useful where directly printed and coherent. Listening begins at 31. |
| `pdf_13`, 【1】, `5880f756ec81…` | Original pages 3, 5, 7 individually opened; **all 1–30 additionally verified pixel-identical** to the reviewed corresponding `pdf_16` pages at 100 dpi | `booklet_pair_render_comparison.json` records equal raster dimensions and SHA-256 hashes on every written page. This establishes the same reviewed page bodies without claiming a second independent witness or a separate visual opening of every page. |
| Munja JSON, `759589b9f71c…` | All first 12 written sections; all 73 stems/options/keys aligned; all eight text passage bodies; both notice/table images directly viewed | The notice omits the Friday label and final URL; table adds 名前 in its corner. Shares unusual variants with the booklet/17-page explanation family. Different numeric keys at V23/G13 follow different option versions; G8's same numeral identifies a different ending. |
| `pdf_6`, 17-page N3答案解析, `e04db0d41e78…` | All native pages 1–17 read; original page 8 additionally inspected for 会社中で and usage context | Explanations are secondary and share conspicuous wrong distractors/garbled wording with Munja. Native G19 heading says 1 while its explanation argues for 3. Not an original-image claim for its other pages. |
| `pdf_11`, 33-page N3文字语法阅读解析, `397e1b028c44…` | All native pages 1–33 read; originals **3–6 and 11–14** inspected for competing distractors and their explanations | Explicit わかりました at V5, 胸 at V10, 暑かった at V12, the compact adverb/loanword sets at V22–23, きらった at V24, and どきどき at V25. Native OCR alone was not quoted as an original glyph reading. G26/G36 explanations are absent. |
| `pdf_8`, N3阅读译文, `89554b934f98…` | Original pages **1–2** | Chinese translation of cloze/mail/e-sports/karaoke; e-sports choice 4 explicitly concerns an unknown meaning of “sports.” Useful semantic support, not exact Japanese testimony or proven independent ancestry. Remaining translation pages were not needed to discriminate the residual Japanese-wording cases. |
| `pdf_2`, Yuuki answer Ver 2.0, `ef3d4eb04dae…` | Original written pages **1–3** and corresponding native text | G15 wrongly marks option 4 / wrong star position, G26 wrongly gives 3, and some quotations contain additional errors. These do not override the question/answer logic. |
| `pdf_17`, 4-page N3答案解析, `a1be1f47e895…` | Original **1–3 and written upper portion of 4** | Shared unusual quotations with the Yuuki answer file. Extra 3 in the vocabulary problem-3 summary row; G15 summary/order points to 2 but line label says 4; G26 says 3. Written G27–38 checked; lower listening table excluded. |
| `pdf_18`, N3-真题答案, `25b1fe9ec635…` | Original **1–3**, all written key panels | Explicit 名师回忆版. Vocabulary and grammar rows agree with the retained mappings; reading gives unsupported G26=3, G29=3 and G36=3. Page 4 listening excluded. |

All 35 indexed source hashes were checked at start and again after proposal construction. Exact paths/hashes are preserved in `audit_work/source_inventory.json` and the read-only unit index. Generic scoring/answer-card files and listening-only material are outside this content audit. The archived HTML remains available as fallback evidence, but there is a suitable non-archive principal and no residual case requiring it; no working archive HTML, global candidates, source files, index, or tools were edited.

### Complete field and answer review

Evidence establishes **35 vocabulary + 38 grammar/reading questions = 73**, **292 ordered choices**, **12 sections**, and **10 blocks** (one worked example and nine passages, including the notice). There are five optional editorial completions. Every stem, choice, key, heading, block, continuation and relevant printed format was reviewed. Stable question IDs retain their separate vocabulary and reading numbering.

`align_written.py` aligns every Munja written item and key; its text report includes all eight text passage bodies. `principal_alignment.py` provides an additional field check against native compact text: 280 exact normalized base-text fields and 106 candidates for visual adjudication, with the raster notice compared separately. Native matches are not treated as proof of formatting or correct option position. The original-page review catches the duplicated V6 choice, reference marks and missing ruby that text matching cannot. False native glyph differences such as long-vowel marks encoded as 一, 期侧 with a visibly traditional 側, and 携带 with the displayed 帯 were checked as rendering/text-layer differences, not copied into the reconstruction.

The public register reconciles **46 current departures** from the selected principal, including inherited wording, punctuation, spelling repairs, added reading aids and repaired reference marks. Grouped choice-array rows explicitly identify the common full-stop convention; they do not conceal a changed option. E/e spelling is disclosed. Exclusions are harmless reflow/spacing, equivalent bracket/slot linework, covers and decorative furniture, logical 文法/読解 navigation labels, and incidental continuation of an underline across a final full stop or whitespace. Actual lexical underline targets, numbered references, the complete answer-sheet demonstration, all instructions and the coupon illustration's printed denomination are preserved. The stack's decorative linework is represented by its text label, not a fabricated count.

The following key strings were transcribed from the inspected principal table, then checked against independent item reasoning and the final proposal:

- Vocabulary: `33114224341312331224214312214343421`.
- Grammar/reading: `42122114313234234134214314124222343134`.
- ★ orders G14–18: `3-2-4-1`, `3-1-2-4`, `4-2-3-1`, `2-1-4-3`, `4-3-1-2`; third-position answers `4,2,3,4,1`. The example is also `3-2-4-1`, hence answer 4.

V18 requires 消極的で, not bare 消極的ので. V20 needs a predicate relating 仲 to the consequence; the exact compact version is preferred provisionally. V22 一度に fits memory overload and the complete adverb set is supported by both question and explanation versions. V23 and G13 keys are mapped to actual choice text, not copied across reordered versions. G8's complete dialogue requires an unmet obligation despite the unfinished report (のに), not the truncated ので version. G12 必ずしも calls for the negative option. Deliberate wrong uses of 知識／ひびく／完成／あわてる／実物 are retained; particle/formatting repairs do not make those distractors correct.

The nine passages were checked through their final sentences: the 70-year-old friend is 50 years older, with blank 20 introducing the shared interest in films; the meeting mail promises a later decision, not a decided postponement; the e-sports question points to the *initial* surprise, not the later discovery of a word meaning; karaoke applicants request practice by May 7 and arrive at 10 on May 29; coffee is taken just before a roughly 30-minute nap (G26=4); spinach needs darkness at night (G29=4); the pencil passage distinguishes the thin, break-resistant 0.5mm lead from the other dimensions and explains small handwriting; the sports passage's overall theme is increasing visitors (G36=1), broader than just entertaining them. The malformed-looking G33 distractor 選手が努力することがなく is consistently printed and remains a wrong causal claim; it was not rewritten for fluency.

The shopping table retains every name/value and its blank corner. Applying at least three shops, five receipts and 5,000 yen identifies only 東さん (G37=3). Printed Sunday April 11 is past the April 9 postal deadline; the remaining Monday April 12 hand-delivery window ends at 17, so G38=4. All address, telephone, URL, eligibility, opening-hour and date details were compared. The Yuuki promotional Facebook substitution is rejected in favor of the complete notice image; no fictional contact was contacted.

### Decisions and public uncertainty

The proposal contains **55 exact field edits: 50 high-confidence and five medium-confidence**. It restores 28 selective ruby groups in total, the 20 usage-option underlines, the G30 quotation underline, the complete example heading/reading aids, four interrogative dakuten, the notice's three readings/denomination/list bullet, and the single sports-note marker. G14/G16 editorial completions now quote the actual supplied options. Imports, item IDs, order, all 73 keys and the legacy source metadata remain unchanged.

The five provisional fixes are V5 option 1 **わたしました**, V20 the **仲がよくて…そうだ** stem, V25 option 2 **どきどき**, V32 option 4 **会社内で**, and G24 option 4 the **unknown meaning of the English word スポーツ**. Each has an exact before/current value, actual inspected source readings, viable competitors, linguistic justification and residual uncertainty. The G24 teacher statement is clear contamination; the exact replacement still has a competing related booklet distractor, so it remains medium confidence even with translation support.

There are **22 public cases: five provisional fixes and 17 retained unresolved variants**. Retained variants cover V7's verb, V10/V11/V12 distractors, V16/V17 wording, V23 guest wording and option set, V24 distractor, V27 speech style, V31 polarity/demonstrative, V35 tense, G3/G13 option versions, G5 school period and G12 distractor ending. These are completed investigations, not deferred work. Public cases explain why syntax/answer logic cannot authenticate two viable distractors, names of school periods, polarity or tense. The old high-confidence label on 高校時代 was explicitly reassessed. Missing authentication alone was not used to mark every item uncertain.

### All local candidate dispositions

All **83 written** rows were read in full before the following dispositions. IDs below abbreviate the common `2024-07-N3-` prefix. The local historical rows remain unchanged; listening rows were filtered before candidate loading.

| Candidate IDs | Current disposition |
|---|---|
| R-001 | Correct 文章/文章全体 retained; source-supported instruction spellings and selective ruby restored. |
| R-002–003 | G23's 15時 and かどうか already correct; full mail/options/key rechecked. The principal's かとうか is separately recorded. |
| R-004 | G38 time spacing was already repaired; complete notice and the exceptional 17時 closing time checked. |
| R-005 | Historical malformed HTML/tag concern is absent from the balanced JSON. Notice heading/escaped angle brackets preserved. |
| R-006–021 | Reviewed word-boundary/repeated-string/募集 detector leads in full current question and passage contexts; no substantive correction warranted from the detector proposal. |
| R-022 | Munja section-number/heading alignment mismatch, not a reason to rename the ★ problem. Current source instruction spelling restored from originals. |
| R-023 | Reject かとうか; current voiced かどうか is correct. |
| R-024 | The old tiny なれた/なわた dispute obscured an unrelated teacher option. Replaced the whole G24 option 4 provisionally after original-page, translation and full-item review. |
| R-025–026 | Formal instruction variants reassessed against originals; 答え and the two-passage と wording restored where printed. No invented passage or question renumbering. |
| R-027–030 | G37 name-option full stops are an inherited punctuation convention; names/order/table/key unchanged and principal differences disclosed. |
| R-031 | Copied comment about listening is outside written-content adjudication. |
| R-032 | G11 duplicate-answer comment is stale; actual four options are distinct and key 3 is supported. |
| R-033 | Courtesy comment, no exam content correction. |
| R-034 | Coffee key complaint investigated with the complete paragraph and all choices: current G26=4 retained; separate keys giving 3 are wrong. |
| R-035 | Vague comment referring to “41” does not locate a supported new written defect; no guessed mapping or edit. |
| R-036–041 | Earlier HTML diagnostics/boilerplate do not constitute current JSON content errors; balanced JSON and substantive spans checked. |
| V-001 | 全部売れました retained; all V26 choices and answer 2 verified. |
| V-002 | 暗くなって retained; complete V27 context and tense variants reviewed. |
| V-003 | Stray historical `1)00` corruption is absent; current question numbering valid. |
| V-004–006, V-009, V-011 | Reviewed instruction kana/kanji and detector variants. Current vocabulary instructions agree semantically with the original; decorative linework/width is not an error. |
| V-007 | 遠慮 retained over truncated 遠; the noun + する choice has direct complete-source support. |
| V-008 | きらった retained over もらった with a public unresolved record; both can be wrong choices. |
| V-010 | 暗くなって retained over malformed 断くなって. The explanation original also shows 暗. |
| V-012 | V31 option 1 punctuation variant does not justify changing its deliberate 知識 misuse; printed underline restored. |
| V-013 | Retain final question か; restore source-supported が in はさみがどこ…, preserving the wrong target word and its underline. |
| V-014 | V31 option 3 polarity/wording reviewed beyond the old fragment; retain complete positive-polarity version with a public case. |
| V-015 | V31 option 4 その／この remains publicly uncertain; correct use of medical 知識 and key 4 retained. |
| V-016–018 | V32 options 1–3 punctuation variants rejected as substantive errors; target underlines restored, wrong uses preserved. |
| V-019 | V32 option 4 contains a real 会社中て defect, not merely punctuation. Prefer **会社内で** provisionally; public case includes 会社中で from the inspected explanation. |
| V-020–022 | V33 options 1–3 are intentional wrong uses; underlines restored without normalizing them into correct choices. |
| V-023 | 今 in V33 option 4 retained from principal/Yuuki; the truncated alternative does not justify deleting it. |
| V-024–027 | V34 punctuation variants reviewed; underlines restored; only option 2 is the appropriate rushed-action use. |
| V-028 | V35 option 1 full-stop/spacing difference is harmless; correct physical-object meaning and underline retained. |
| V-029 | Reject the secondary option's garbled そのことは…わかるためだ reconstruction; complete principal/Yuuki sentence retained. |
| V-030 | V35 option 3 intentional 実物 misuse retained; optional object-particle difference recorded against principal. |
| V-031 | Reject the garbled 劇場／実演 version, but disclose the genuine past/nonpast dispute in the intact competing sentences. |
| V-032–036 | Copied comment leads assessed as for R-031–035: listening comment excluded, G11/key issues resolved as above, courtesy/vague numbering not treated as evidence. |
| V-037–042 | HTML diagnostics/boilerplate have no supported corresponding content defect in the current JSON. |

### Historical ledger, verification and reporting preparation

All 35 written records from the existing 38-record ledger were reassessed; three listening records remain preserved but unadjudicated. Earlier HTML cleanups, source-formal headings, G23/G34/G38 repairs, notice deadline/contact/table restoration, 申請, G3 subject/context, 青木, quoted-dialogue repairs and ★ punctuation were checked against full items. Older V23 repairs now have explicit uncertainty about the guest phrase and option version. G8 option ordering remains the complete coherent version. The example's inherited correct answer 4 remains, while its previously missed heading defect is repaired. The whole historical ledger is retained byte-for-byte as a prefix, with no rewriting of old confidence claims.

Private proposal files are reproducible from `build_review.py` and `build_principal_report.py`. `verify_review.py` checked the exact edit replay, unchanged metadata and keys, all 35 source hashes, the independent key vectors, ★ completion strings, all five table rows and the eligibility calculation. It counted **28 ruby groups and 60 underline spans** (including the five existing editorial explanations). Field and reading-aid manifests are preserved under `audit_work/`.

The structural validator passed on the proposal with expected counts 35/38, baseline, combined append-only fixlog and public cases. Its eight option-change warnings concern V5, V25, V31–35 and G24: five usage arrays gain rich underline markup (with the separately logged particle/location repairs), and the three other arrays have the explicit provisional choice replacement. No option ordering or answer number changed. These warnings were reviewed, not suppressed. Final committed-file and principal-reporting checks are recorded in the closure entry below.

Method-1 principal assessment prepared separately: provenance **unverified (100)**, metadata flags 0, missing units 0, major defects 3, minor defects 16, uncertain fields 20, giving **167 = 100 + 15 + 32 + 20**. There is one event per affected field at its highest severity. The example/reference-system problems count as whole-block issues; spelling defects absorb the separate unresolved tense/style concerns in V27/V35. Printed instruction-ruby losses count once per heading, not per reading. Minor punctuation/case conventions and errors in separate answer keys do not penalize this principal. This ordinal assessment is not an authenticity probability.

## Committed-file closure (2026-09-25)

The reviewed proposal was committed after checking the current JSON, case file and ledger against their preserved byte baselines. All 55 new field edits are present: 50 high-confidence and five medium-confidence changes. The 38 historical ledger rows remain an exact byte prefix. The public file contains 22 current cases (five provisional fixes, 17 retained disputes); the principal register contains 46 current departures. No question, choice order, key or historical provenance was silently changed.

Committed-file structural validation passed with 35 vocabulary and 38 grammar/reading questions, 292 choices and ten blocks. There are no null keys or structural errors. Its eight option-change warnings have the dispositions recorded above. Exact replay and content-specific checks passed before commitment; committed JSON SHA-256: `385bbdc271dbee0030516f6372493d9f4704b067766c9c10ab14e2621b4d21bf`.

Evidence review is complete; residual historical wording uncertainty is disclosed in the public cases. The unit result is recorded before queue advancement. Principal catalogue and ancestry reporting follow as a separate reporting step.

Principal catalogue validation passed with 13 entries; this unit has method-1 score **167**. The principal-differences validator passed all **46** rows with no errors or warnings. Three page-specific ancestry observations were appended with acquisition method left unknown. Their scope is the inspected pages; the booklet pair additionally has saved identical-render hashes across written pages 1–30. All reporting is local; source files remain immutable.

Queue advanced to **N4_07_2024** after the recorded unit result and successful reporting checks.


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 9 maintained fields / 32 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N3_07_2024-DW20261013-001 through N3_07_2024-DW20261013-009 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.


## Housekeeping 2 — 5 November 2026

N3_07_2024-PD-028: Adopt lowercase e for the quoted competition name. The selected reproduction directly prints it; the compact body is the same lineage. The Mogi version prints capital E; the abridged booklet substitutes computer competition entirely. The contemporaneous Ministry of Finance publication uses lowercase e for the same activity, independent evidence for usage rather than proof of exam printing. Case alone does not change what surprised the narrator. Keep the separate だるう→だろう repair and reference underline.

N3_07_2024-PD-035: The selected and Mogi versions repeat their respective lowercase and uppercase initial in the first distractor as well as the passage. The difference is the spelling of the competition, not the distractor’s premise (a high-school student in a famous contest). Use the same, independently supported lowercase form on both occurrences. Keep choice 4’s intended later-discovery distraction, option order, punctuation and the key. The official N3 socks task illustrates why later true information can still be a wrong answer.

N3_07_2024-reading-q024-options-3: The main Japanese passage and the translated version support the current fourth choice. It accurately describes what the narrator learns later, but not why he initially finds the competition odd. The school teacher claim has no referent; the shortened booklet gives a different plausible sports distractor. Retain the already repaired fourth choice. Its credibility comes from the exact question and alternatives, not from an assumption that a wrong choice must be obviously false.

The principal index remains 167: the printed だるう, question defects and distractor disagreement are separate from the lowercase letter. This spelling adjudication does not alter a scored source concern. 2 editorial fields changed. 5 public and 13 principal snapshots rebound to pre-existing field changes; not substantive reviews.

[Before/after decisions and receipts](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N3_07_2024/disposition.json).
