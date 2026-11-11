# N4 July 2024 editorial audit

Status: in_progress.

## Start (2026-09-25)

Live state was confirmed after N3 closure and reporting checks. Byte baselines of editorial JSON, root fixlog and public cases were preserved before editing. The current index was read. Listening material and generic answer cards are excluded from content review. Historical notes supply leads, not current decisions. No principal has yet been selected.

## Full written review complete (2026-09-25)

Result: **audited_with_uncertainty**. The review recovered all available 57 scored questions (28 vocabulary and 29 grammar/reading), their 228 ordered choices, 11 section instructions and 12 final content blocks: seven worked examples, four passages and one notice/table block. Six examples were missing from the import and were restored with unused IDs. No scored question, answer number or existing item ID/order was changed. All 92 local written candidate rows and all 56 written historical correction records were reassessed. One historical listening record remains in the immutable ledger prefix and was excluded from adjudication.

Baseline SHA-256: `2933d85d7f372f5693c76a4a29cb47d4cdf97732ebff53ed13ffca5f5b7723ff`.

Final editorial SHA-256: `0edec28c940dbef658a21b67b258318b6babc242ba320f9adfe77ce2e65be80d`.

The unit has 58 appended field/item edits: 56 high confidence and two medium confidence. Its public file has 13 current cases: two provisional fixes and 11 retained uncertainties. The current principal register has 30 departures, including inherited choices and confident source repairs. Imported `sources` metadata remains byte-equivalent in value; it describes the historical import and is not represented as the selected principal's provenance.

## Identity, principal selection and actual inspected scope

All 29 unique indexed files were hash-checked against the current index; the saved inventory records paths, hashes and PDF lengths. Hashing excluded listening files does not constitute a content review. Alias metadata was not treated as an independent witness. No source, index, candidate/history original, shared tool, working archive HTML, site or import fixture was modified. No external authenticity search or acquisition-chain claim is made.

Selected principal: Tier 2 `src/日语JLPT历年真题/N4真题（2010-2025.12）/2024年7月N4/2024年7月(暂无解析，后续更新)/2024年7月能力考N4真题+答案.pdf`, SHA-256 `4a2bc6a6cdaea044a153851f0c5515f86dc635d3bf6c4832796392dfadd26cb3`. The indexed OCR label is `pdf_4`. Its 31 physical pages agree with the cover's page count; page 3 identifies `2024-1 N4` and the 75-minute written test. Original page 1 (written key chart) and every original page 3–15 were viewed fully. Vocabulary is on pages 4–8; grammar, worked examples and all reading continuations are on pages 9–15. Page 2 is a listening key and pages 16 onward are listening, excluded from content audit. Page 2 was incidentally rendered but not viewed or used as evidence. The selected catalogue scope is `1,3-15`.

This is the most complete available written witness, including six worked examples omitted from the other question edition. It is **unverified**, not authenticated. Sharp typesetting, the cover, distributor names and cross-copy agreement do not establish acquisition or justify classifying it as a known reconstruction without positive evidence.

Material comparison witnesses:

- Tier 1 `src/Yuuki Bui/Đề thi N4-N5 các năm Yuuki Bùi/2024年7月/N4 T7-2024/Đề N4 T7-2024 Ver 3.0 [Mark].pdf`, SHA-256 `ff4b8f8f8efcf024b27e41bfa274b131f041e1f25018bc9dba3e4f0874d4dc59`, `pdf_3`, 28 physical pages. Every original page 1–14 was viewed fully: all 57 written questions, all options, passages and the notice. Listening from page 15 is excluded. This retype has a different layout, missing examples, distinct errors and competing natural variants; its initial tier is not a verdict of correctness.
- `src/Yuuki Bui/Đề thi N4-N5 các năm Yuuki Bùi/2024年7月/N4 T7-2024/Đáp án N4 T7-2024 ver 2.0.pdf`, SHA-256 `ee60f46dadfea29583cdc642e7c24806889ad319964d08523c818f3fe4a9b626`, `pdf_2`. All originals 1–3 were read; page 4 is branding and not needed for written reconstruction. Page 1 covers V1–20, page 2 V21–28/R1–13 and page 3 R14–29. This is a separate local explanation witness, not independent authentication or a complete four-option transcription. Its own typos (e.g. 騒いて, おこ, missing kanji in V11) and the seven-digit V13–20 summary are not authoritative answer evidence. Detailed solved items and question logic take priority over its malformed summary.
- `src/munjaJLPT/N4/2024-07_N4_vietnam/2024-07_N4.json`, SHA-256 `97aa5e2c0ac3c695d744f1362aa363b594994e2c2b45ba2d82f43c5928990cf4`. Only the first 11 written sections were loaded for content alignment. All 57 question stems, choice arrays and keys were compared at their native identities; the first five sections contain 28 vocabulary questions in total, followed by 21 grammar and eight reading questions. There are no written passage blocks in this source, so it supplies no author/date/notice-passage testimony. R27 has three array entries because choices 2 and 3 were merged; the four current choices are confirmed by both original question PDFs. Shared rare errors with Yuuki prevent counting it as an independent vote.

The generic answer card, listening script, listening images and listening archive page supply no useful written evidence. Archived HTML was not needed: suitable non-archive principals and comparison material exist. The Yuuki notice's `/yuukibuibiensoan` branding does not independently support an exam URL; the principal's `https://pizza-arose/kyoshitsu` is retained without visiting or validating that address externally.

## Full content and formatting coverage

Every current question stem, each of four ordered choices, every answer mapping, every instruction and all passages were read in context, including unchanged text. `baseline_dump.txt`, `munja_alignment.txt`, native alignment candidates and the original renders supplied review aids. Native text is not literal testimony by itself. The 39 native alignment flags and 259 substring matches were adjudicated against full originals; a matching substring elsewhere on a page was not accepted as proof of the intended field.

Eleven focused original crops at 260 DPI supplement the complete page views: page 4 underlines and the kanji example; page 6 vocabulary punctuation/conjugation; page 7 instruction; page 9 grammar; page 10 Q12; page 13 newspaper passage, Q23 and bus passage; page 14 Q28; page 15 notice. The crop manifest preserves rectangles, DPI and hashes. These confirmed つき, ぐらお, びしょうに, 投業, からます, loanword voicing and exact underline boundaries. The first notice sentence correctly has ピザ教室; the corrupted pizza occurrence in its introductory paragraph is **おいしいビザ**. No source quotation was inferred from the earlier imprecise summary.

Native mappings `口ボット`, `リょうり`, `每週` and the apparent `ロギ一ルス` long-vowel glyph were considered carefully. Their visually confusable glyph/codepoint distinctions do not by themselves establish distinct exam wording; normal Japanese forms remain, with no invented source-error score. Clear kanji/kana choices such as 入れて/いれて and 食べられます/たべられます are recorded as actual principal departures. Full-width/half-width delimiters, comma grouping of thousands, line breaks, tabular linework, bullet shapes, page furniture and the decorative pizza illustration are equivalent/non-semantic representation exclusions. All table relationships and numeric values are preserved in two real HTML tables. The illustration carries no additional task condition.

No reviewed written question original prints furigana, including the four scored ★ stems. No learner-oriented ruby was added. Existing ★ example `reading-b001` retains its full instruction, four options, solved order 3–2–4–1 and answer-sheet mark at 4. Its inline rendering of boxes and answer-sheet labels is an equivalent representation, not omitted exam content. The six restored examples are placed before the scored questions of their respective sections:

| ID | Principal pages | Tested example and printed key |
|---|---|---|
| vocab-b001 | 4 | 千円 reading, option 4 |
| vocab-b002 | 4–5 | よんで kanji, option 3; 諸/続/読/緒 retained |
| vocab-b003 | 5 | ざっしが2（ ）, さつ, option 1 |
| vocab-b004 | 6 | ゆうべ paraphrase, きのうのよる, option 4 |
| vocab-b005 | 7 | しめる usage, ドアをしめて, option 3 |
| reading-b007 | 9 | 新聞（ ）読みます, を, option 3 |

Each restored example has all four printed options and its filled answer-sheet bubble. IDs were unused and existing block numbers were not reassigned. V21–24 underline the complete target sentence including its final stop. V25–28 are plain headwords, with usage-word underlines in the options; the imported stem underlines and artificial full stops were removed. R23 places ① outside the quotation and underlines the complete quoted speech including quotation marks/full stop. In the newspaper **passage**, however, the underline excludes the final stop; the current passage boundary is correct. Both bus-passage underlines likewise exclude following punctuation. These distinct boundaries were checked, not harmonized by a generic rule.

## Linguistic and answer decisions

V1–12 readings and kanji choices were checked one by one. Deliberate wrong choices such as 明い, 助かなく, 勤かなく, 意上/意下 and 公通/交道 are preserved. V13–20 select さがした, きびしい, ひつよう, にんき, おって, しゅるい, たりなくて and ちゅうい (2,2,1,4,3,3,4,1). V20's stem now has さわいで, the correct conjugation of 騒ぐ and the actual principal reading; both Yuuki files' unvoiced て is an incidental error, not a tested alternative.

V21–24 match とられる/おんな/話/つくる (4,2,1,3). V25–28 usage keys remain 3,1,2,4: city population, congested road, escaped thief, distant bank inconvenient to reach. Incidental repairs do not make deliberately wrong uses correct. V28 option 4 changes は→に at medium confidence: principal and separate explanation support に, but は is also grammatical. V26 option 1 past/nonpast and V28 option 2 present/past remain public. No assumption that a distractor must be fully grammatical or that every unnatural phrase is corruption was used.

R1–13 keys are 4,3,3,4,1,2,3,2,4,2,3,1,1. The cited book in R4 requires によると, not より; the principal key table's 3 is wrong. R7 requires そうじ**の**とちゅうで; restoring の is strongly supported by the other question and explicit solved explanation. R3's ぐらお and R5's びしょうに are incidental spelling errors in otherwise meaningful distractor particles/adverbs, not the grammar-test contrast. R9's surname and R10's viable wrong option remain historically undecided even though their correct answers are clear.

The four ★ items were solved with all fragments and original star positions:

| Question | Order | Star position/key |
|---|---|---|
| R14 | 3,1,4,2 | second = 1 |
| R15 | 1,4,3,2 | second = 4 |
| R16 | 1,4,2,3 | third = 2 |
| R17 | 4,2,3,1 | third = 3 |

R14 supports both 今日/今日は and 予約したいです/予約したいのです; ordinary Japanese cannot authenticate these variants. R17's separate editorial explanation now matches the kana spelling of option 3, きょうみをもつ. Its explanation includes the unchanged following stem なりました and is not attributed to printed exam content.

Cloze R18–21 keys 2,4,3,1 yield という, 休むことにしました, そして and 入ることができます. The passage means one can use the café without paying museum admission. 払わなくても is strongly established, but the **Yuuki question page does not print it**: it has 渡しわなくても, while the principal has 私わなくても. The separate explanation explicitly supplies 払わなくても. The old audit's apparent attribution to the question edition was therefore corrected. ロギールス/コギールス, 先月/先日 and the repeated museum name remain public uncertainties.

R22 asks Yan to tell Nakamura whether 10:00 or 14:00 is preferred; Nakamura will book. R23's quoted speaker is the clerk, and R24's surprise concerns perceived impoliteness. The later suggestion that the customer was a friend does not replace the narrator's initial reason. The principal's 投業 is clearly 授業; からます in R24 option 4 has stray ます. Both are corrected in the current reconstruction while the quotation topic particle and honorific variants remain public.

R25–27 follow the bus passage: ordinary travel costs too much; the narrator enjoys riding and walking near the final stop; he has not chosen a destination when the driver asks. The principal key R27=3 is wrong; 2 is correct. Listening to passengers is distinct from conversing with them. Both と会話 and との会話 describe participation and remain plausible historical wrong choices. R27's historical question tense is separately uncertain.

R28 uses adult 1,500 yen + child 1,000 yen + one rented apron 200 yen, option 3. R29's party of three eats on site: drink and salad only, option 1; ice cream requires at least five people and the 500-yen voucher is for takeaway. The notice preserves 20 cm/one pizza per person, adult accompaniment for young children, three age-based prices, apron hire, once-monthly 15:00–17:00 classes, homepage date information, booking by phone one week in advance, and exact address/phone/URL. Mixed ビザ/ピザ and エブロン/エプロン in the principal are spelling defects, not visa or apron-price conditions.

## Local candidates and historical decisions

`audit_work/candidate_dispositions.json` accounts for all 92 local written IDs, without loading global candidates. All old accepted/rejected statuses were treated as leads. Routine detector and HTML findings were assessed after reading their item contexts. The following groups make the material dispositions explicit:

- R001–039: ordinary content/markup repairs retained after original review. R002, R006, R008–009, R024–025 and R038–039 require the public surname, request, author/date/reference, tense and quotation/honorific cases. R010 payment attribution is corrected as described above. R012's final から is required. R013–020's bus passage repairs are supported; spacing in のです is not a new lexical issue. R021–023 are markup cleanup; R026–027 correctly recover four separate R27 choices. R031–037 preserve the complete notice while avoiding the principal's loanword typos.
- R040–042: reject regressions from Munja's dropped から, malformed bus-stop phrase and merged choices. R043 is the によると detector false positive; R044's repeated restaurant name is valid heading/footer content. R045–050 historical HTML diagnostics are not content edits; R051–054 are non-content commentary.
- R055–056 confirm wrong principal embedded keys R4/R27; R057 confirms missing の; R058 is the unresolved 今日/今日は issue. R059–062 confirm principal ぐらお, びしょうに, からます and ビザ defects. R063's older decision was superseded by later local repairs; retain the principal-supported 下の文章 introduction.
- V001–013: retain 少し, つぎ, は会社, 水 and 話は repairs. V004/V010 tense and V006/V012 tense now have explicit public uncertainty; do not call a viable alternative impossible. V014's にぎやか is a legitimate wrong option. V015–020 are HTML/boilerplate diagnostics and V021–024 non-content commentary.
- V025 is the medium に preference. V026–027's native character-map warnings are not a basis for invented visual source readings. V028–029's double full stops are actually visible and documented as principal departures.

The 57 historical ledger rows, including later corrections and the excluded listening row, remain an exact byte prefix. The 56 written rows were read and reassessed, including the later example/wording repairs. Earlier high confidence does not override the present public cases. No new ledger was written under `legacy_run/`.

## Public uncertainty and principal reconciliation

The two provisional edits are V28 option 4 に and the short-reading instruction (1)–(2). Both complete question editions contain only passages (1) and (2), with three scored questions Q22–24, then problem 5. This supports repairing the principal's inconsistent (1)–(3) range, but cannot prove the historical heading or exclude an earlier restructuring. No third passage was invented.

The 11 retained cases cover V26 option 1 tense; V28 option 2 tense; R9 surname; R10 option 1; R14 stem; R14 option 4; cloze author/date/reference; newspaper quotation/honorific; the same quotation in R23; R26 option 1 construction; and R27 stem tense. Each case has exact current typed value, strongest alternatives, identifiable hashes/pages or native locators, actual resolution attempts and the residual uncertainty. The complete originals and relevant explanations were read, alternatives tested in full context and answer mapping revisited before leaving these open. Agreement and grammatical naturalness are not presented as historical proof.

The 30-row principal register covers confident repairs, inherited kana/kanji and punctuation variants, a fuller instruction, disputed wording, the structural range, and both erroneous embedded keys. It compares the final JSON to the actual principal, not just the 58 edits. Newly restored examples and repaired fields that now agree with the principal do not generate departure rows. Public cases can remain even when the selected text agrees. All applicable same-field cases are linked. Editorial explanations, import metadata, IDs, archive scoring weights and harmless layout representations are excluded from principal exam-content comparison.

## Verification and delivery

The private verifier replays every new edit exactly, including six example placements, and confirms equality with the proposed final JSON. It verifies unchanged import metadata, existing scored IDs/order and keys; all 57 independently adjudicated keys; the two principal-key differences; agreement with the aligned structured keys; four ★ arrangements; six new example options/keys/bubbles; block counts; all meaningful passage/quotation underline boundaries; absence of invented ruby; and the notice's two tables and material conditions. Source hashes were rechecked. The case/difference validators accepted exact snapshots and links.

The structural validator was run with the saved baseline, root-compatible cases/ledger and evidence-derived `vocab=28`, `reading=29`. It passes. Its 17 warnings are fully explained: six newly restored IDs, one section-membership/order notice caused solely by those insertions, and ten changed option arrays (V21–28, R22 and R24) caused by restored final punctuation, plus the documented V28 particle repair. No choice was reordered and no key changed. An initial unsupported private `placement` member was removed from creation log rows; placement remains in the evidence text and private replay map. An initial numeric literal in principal-key reading prose was serialized as a string, preserving integer `current_value`. These were record-format fixes, not content changes.

`audit_work/verification.json`, `validation_report.json` and `principal_validation_report.json` preserve final results. Root deliverables are written only after proposal verification and baseline guards; the ordinary validator is rerun on the root files. Progress result is recorded before the separate principal catalogue/reporting step and state advance. Validation checks structure and consistency, not authenticity. Sources remain unauthenticated and the 13 public cases remain material limitations of historical reconstruction.

## Separate reporting and queue closure

The selected principal entry was added after the unit result was recorded. Method 1 is unverified 100 + metadata 1×2 + missing 0×10 + major 3×5 + minor 10×2 + uncertain 10 = 147. Each event is documented; duplicate same-field concerns are absorbed. The full 14-entry catalogue and this 30-row principal register passed the required CLI validators with no errors. One concrete ancestry observation was appended. State advances to N5_07_2024 only after these checks.


## H11 continuous-reading amendment — 2026-10-15

Removed 21 explicitly reviewed phrase separators in 6 actual reading fields. Exact before/after values, reversible position maps, intact ruby proofs and live canonical binding are in `pdf-render/evidence/handoff11/N4_READING_AUTHORING_PREPARED.json` and the appended unit fixlog. Grammar, examples, scored facts and existing unresolved-case statuses are preserved.


## Housekeeping 2 — 5 November 2026

N4_07_2024-PD-028: provisional_fix. Retain HK1's 分から→わから choice with explicit historical uncertainty. The complete principal task prints kana, while the complete Yuuki task prints kanji. Approved N1 source pixels now verify the earlier editorial-proxy comparisons in ordinary cognition clauses. Those parallels support viability, not a universal spelling rule or proof of the N4 item's history. The bus passage makes Q27 option 2 correct because no destination was planned; option 3 must retain its deliberately wrong misunderstanding explanation. Preserve every answer distinction and all current keys.

The narrator cannot afford frequent rail/air travel, so enjoys an ordinary 210-yen bus ride to its final stop and walks there before returning. Having selected no destination, the narrator cannot answer the concerned driver's question after being woken, not because the Japanese question was misunderstood. All choices confirm current keys 4/3/2 for Q25–27. The disputed option 3 is an intentional wrong explanation and stays wrong with either script. Principal pixels use わから; the Yuuki version uses 分から. Newly inspected approved N1 passages use わかる for ordinary recognizing/knowing, supporting kana as a viable spelling but differing in level, task and polarity. They do not prove the 2024 distractor's exact script. Existing snapshot-only removals were separately inspected: stray line-wrap spaces split words such as 旅行, 大丈夫 and いました or stand at Japanese clause boundaries; no characters, digits, option boundaries or substantive judgments change.

Unchanged 147. The principal's separately charged Q27 key error and other concerns remain; this harmless option spelling creates no new source defect.

Rebound 4 older case snapshots to existing v3 typography only; these are not counted as substantive reviews.

Rebound 14 principal-difference snapshots to existing typography; comparison readings, reasons and dispositions are unchanged. These are record maintenance, not substantive reviews.

No editorial or ruby content changed. Historical fixlog bytes and all case identities are retained. [Source hashes, before/after cases and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N4_07_2024/disposition.json).
