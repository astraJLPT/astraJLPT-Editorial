# N3_12_2020 editorial audit

Status: in_progress. Existing editorial admitted directly without a content preflight.

Baseline: audit_work/baseline_editorial_N3_12_2020.json; SHA-256 090fb801f3b6a7a19e9ecf47708cc0ff5e1ea1912f5b17ad5681e77b5f68cd39. Preserve this baseline on resume. Listening is excluded.


## Completed evidence review — 2026-09-28

The written review is complete; final serialization and validation are pending at this checkpoint. Existing editorial JSON went directly to audit, without a content preflight. All 73 written questions (35 vocabulary and 38 grammar/reading), 292 ordered options, 9 parent blocks and 12 instructions were read in full and checked for task logic, meaningful formatting and inherited omissions. Listening is excluded. Source agreement does not establish authenticity.

### Identity and actual source coverage

The selected principal is the indexed Yuuki Bùi `N3 T12-2020 Final Version.pdf`, SHA-256 `28fe1cafc96eb07440718da9efbb7a3b1980515bca2eed9eccfde7d27023a2a8`, initial tier 1. Canonical path: `src/Yuuki Bui/Đề thi N3 các năm Yuuki Bùi/N3 12-2020/N3 T12-2020 Final Version.pdf`. It supplies a complete and legible written sequence and key. Its provenance remains unverified; its name does not authenticate a final exam. Physical pages 1–12 and the written-only key on 16 were inspected: 1 cover, 2 blank, 3–12 all written questions. Listening pages 13–15 were excluded. The cover's 180-minute/26-page claims conflict with the actual 16-page file and other written-exam timing metadata; these are one metadata issue group.

Physical page references below are one-based and refer to actual images inspected. Extracted native text and supplied VisionOCR were navigation leads; visual claims come from the original page renderings. Exact paths/hashes are in audit_work/source_inventory.json.

| Source | Actually inspected scope | Contribution and limit |
|---|---|---|
| pdf_4, Yuuki principal | 1–12,16 written key only | Complete written paper, instructions, all underline endpoints, notice table and 73 answers. Selective enlargements were used where full-page downsizing hid lines. |
| pdf_7, general collection `2020年12月N3 真题.pdf`, 13 pages | 1–10 | Complete materially different written layout. It has a malformed cloze range, short-reading numbering errors, a placeholder last heading and some clearly corrupted text. Its notice image supports the retained numbers. Page 13 was rendered but not counted as visually reviewed. |
| pdf_17, channel-two `2020年12月N3试卷_解析_听力原文_高清扫描.PDF`, 32 pages | 1–12,16 written key only | Complete second written comparison and key. Extra explanation/listening pages were not claimed as reviewed. Its notice postal code has a further eight-digit variant. |
| pdf_13, channel-one `【1】2020年12月N3 真题.pdf` | 1–2 | Cover explicitly says this is not the final/perfect version. Page 2 shares the general collection's written body/layout. This supports a specific relationship, not independent corroboration of every item. |
| pdf_15, channel-one `【2】2020年12月N3 真题.pdf` | 11 | Notice body matches Yuuki page 12 apart from watermark/layout furniture. Other rendered pages were not counted as read. |
| pdf_1, `2020-日语N3试卷-附答案.pdf` | 1–2,9 | Vocabulary distractor checks, email department and TV passage in another low-resolution relayout. |
| pdf_2, `2020年12月日本語能力試験N3真题.pdf` | Native text 1–2 only | Leads with obvious kana/transcription corruption; no visual/literal testimony claimed for its unviewed page renderings. |
| pdf_3, `N3 2020.12 答案+解析+听力原文.pdf` | Tall-page crops: page 1 quarters 0,1,3; page 2 quarter 1; page 3 quarters 0,3 | Read vocabulary Q1–21 and Q31–35 explanations, selected grammar Q9–13 explanations, short-reading explanation spans and the final notice questions. Teaching material, not an original exam; no claim that the unviewed quarters were read. |

All written native munja records were read: the first twelve sections, all 73 questions and all nine shared parents; focused explanations were also checked when useful. Global question numbers 36–73 map to local reading IDs 1–38. The clean-up notice parent also carries a July-2019 identity and the email a July-2013 identity. These reuse labels suggest dataset ancestry, not proof that the same sitting printed identical words. The complete native notice image `2020-12_N3_s12-q01-img01.jpg` was visually inspected and compared with both table versions.

Focused archived reading HTML spans were read for the clean-up closing/contact, email introduction, knife-industry noun, 最後, 日時, fee/uniform question, sleep verb and notice postal code. This is the immutable source archive, not the working website. It was not read in its entirety. Other indexed keys, translations, answer cards and listening sources were not treated as independent votes or silently claimed as inspected. No internet rescue was needed for this unit.

### Japanese reasoning and full-item checks

Every answer was checked against the complete item and passage; the two visually inspected written keys agree with the retained editorial mapping. No key or option order changes. Arrangement orders are Q14 4-2-1-3, Q15 2-4-3-1, Q16 3-4-2-1, Q17 1-4-3-2 and Q18 1-3-4-2; all stars occupy the third slot, producing keys 1,3,2,3,4. Cloze 19–22 yields 4,1,2,3. Reading 23–38 yields 4,3,3,2,3,4,1,1,2,4,2,1,4,3,1,4. Deliberately wrong usage/grammar choices remain wrong.

The full cultural-class table was checked: every course row, weekday/time, capacity, fee cell, merged fee heading, period, registration range and judo-uniform condition. The two variants differ only in tea/flower capacities (35 versus 15), flower end time (15:30 versus 16:30), postal digits and a minor 受付 spelling. Both yield folding paper for the mother attending concurrently with her daughter, and a 5000-yen student fee plus buying a uniform. These answers cannot resolve the disputed numbers. The image embedding in pdf_7 and the native image are one lineage; the Yuuki/channel-one layout is another, not several independent votes.

The 31 proposed edits join accidental internal word breaks; restore quotation punctuation, real paragraphs, reference underlines and circled reference labels; restore lost task wording in Q34, Q36, Q37 and Q38; restore meaningful notice headings; and provisionally prefer 活動終了後 with 222-3333, 営業部, 包丁産業, and 参加したい人全員. The last four decisions remain medium confidence because the alternative native/archive or printed wording can still be grammatical or historically possible. Underline restoration follows the actual phrase endpoints: TV reference ③ ends at だ, excluding な; hamburger reference ② excludes the final full stop. No unprinted ruby was added; the inspected written pages provide no supported selective furigana to restore.

The stronger reading 今後 follows the forward-looking conclusion; 最後 is a transcription error in this context. Q34 needs the missing explanatory phrase and 合っている to ask which description is correct. Q37 requires the same weekday and time, and Q38 asks about both the fee and judo uniform; all four options independently confirm those missing objects. These are high-confidence repairs, not cosmetic fluency edits.

### Historical candidates and difficult decisions

All 234 written candidate rows were read (158 reading, 76 vocabulary; 69 accepted and 165 rejected, all historically marked high). The 53 listening rows were excluded. All 72 historical written ledger records were read, including seq 177,293,514 and 2311–2379; the full existing 109-row ledger, including its listening history, must remain byte-preserved. There were no old ambiguous-status rows to dispose of separately, but accepted and rejected conclusions were both reassessed.

The earlier 営業部→営業課 change was based on a real, legible 課 in the 13-page edition; it was not a hallucinated OCR reading. However, the same salutation says 部, and the other inspected layouts and archive say 部 in the introduction. The new reversal is therefore preferred but provisional, rather than declaring the old page nonexistent. Other earlier major repairs, including the replaced vocabulary paraphrase items and Q28's key 1, remain supported by the actual written paper.

Rejected native leads include Q8 りゅうり versus printed りゅうす (the alternatives systematically contrast る/りゅう and す/しゅ), and Q14 corrupted alternatives versus the printed 2×2 graph contrast 復推/復雑/複推/複雑. Enlarged original views support the current four alternatives and avoid introducing a second valid traditional-character answer. Hujiang explanations support the key but cannot establish all original distractors. Native おいしいは, repeated と in ありがととう, omitted 包丁 in the profession gloss, 若職人, もと, and corrupted cloze choices were rejected by full phrase/task comparison. The 13-page edition's 運転 for 運動 and 評贈る are likewise transcription errors; its wrong heading range 19–23 cannot override four visible cloze blanks.

Seven retained material cases were investigated across the relevant print/native/archived lineages: 寝る/眠る; 会場/場所; four usage items' underline extents (including the separate Q31 sleep-verb variant); and the notice table/contact variants. All strongest alternatives were tested in the complete item, then revisited after whole-paper review. Better Japanese or a correct key does not authenticate exact wording. The public cases record the attempts and specific remaining evidence needed.

Enlarged visual checks corrected preliminary leads before publication: Q31 option 2 underlines only 割引, Q32 option 3 only 気づいた, Q34 options 1–2 only ふらふら, and Q35 ends are 滞在 / に滞在 / 滞在して / に滞在し. The hamburger first reference really is underlined despite weak downsampled visibility. The principal's TV opening genuinely lacks an opening quotation mark while retaining the closing one. Unsupported preliminary observations were not promoted into repairs.

### Current principal comparison and public records

The draft public set has four provisional fixes and seven unresolved cases, with exact current snapshots. The draft principal register has 26 departures, including inherited kana/kanji and punctuation variants, all four underline-span disagreements, notice values, and the omitted administrative cover directions/identity fields. The latter is an explicit non-question omission; all scored written questions, shared context and task instructions are present. Decorative furniture, equivalent glyph widths and harmless reflow are excluded. A reconstruction-only repair adds no source-defect score.

Planned method-1 principal score: 115 = 100 unverified + 2 for one cover-metadata group + 2 for one minor punctuation defect (the TV opening quote) + 11 distinct uncertain item/fields. The eleven comprise the four provisional fields and seven retained cases. Each is counted once; repetitions within a field and alternate-source typos do not add points. Missing units and major defects are zero. The score describes the selected source, not a probability of authenticity or the corrected editorial.

Final serialization, exact baseline replay, canonical validators, source-copy verification and queue update follow this checkpoint. The saved preparation scripts are guarded by the baseline hash and must not be rerun after canonical commit.


## Final completion and verification

Status: **audited_with_uncertainty**. All 31 reviewed edits are committed; four are medium-confidence provisional repairs. The public case file contains 4 provisional fixes and 7 retained unresolved cases; the final principal register contains 26 current departures. The principal catalogue now records method-1 score 115 with distinct evidence events, and the [inspection copy](principal/N3%20T12-2020%20Final%20Version.pdf) matches the indexed original byte for byte.

All three canonical validators exited 0. Reports: [editorial](audit_work/final_validator_editorial.json), [principal index](audit_work/final_validator_principal_index.json), [principal differences](audit_work/final_validator_principal_differences.json). The three editorial warnings concern only internal spacing repairs in vocab-q018, vocab-q034 and reading-q029; ordered option identities and keys were checked and remain unchanged. No old HTML equality test was run. These are structural/record checks, not authentication.

Exact replay of every new edit from the byte-preserved baseline equals the final parsed editorial JSON. The old 109 ledger rows are an unchanged byte prefix of the 140-row root ledger. Source/index hashes and public snapshots were verified. Baseline SHA-256: `090fb801f3b6a7a19e9ecf47708cc0ff5e1ea1912f5b17ad5681e77b5f68cd39`. Final editorial SHA-256: `317c392210eadea6d5af53d57b74ba6a3d5da228dc313610227f9826ce5894f9`. Index SHA-256: `1bf689c7214a95c76a6df6173a9c04b53b667295c2b6fb7c64bc670e4f9ea509`. Original ledger prefix SHA-256: `043bd1502e947f99f0e2a78b1316a46c714181efbfbca5113ac525f0f57219fe`. Principal/copy SHA-256: `28fe1cafc96eb07440718da9efbb7a3b1980515bca2eed9eccfde7d27023a2a8`. Machine verification is in [commit_verification.json](audit_work/commit_verification.json).

This unit is complete with documented historical uncertainty. Its progress row is updated before the queue advances over recorded terminal units to N1_12_2019. The overall active run remains in progress.


## 2026-10-13 — bounded digit-width normalization

Run 2026-10-13_digit_width_cleanup: 20 maintained fields / 116 displayed Arabic digits normalized from U+FF10–FF19 to ASCII. High confidence concerns width equivalence, not literal source authenticity. Granular exact records N3_12_2020-DW20261013-001 through N3_12_2020-DW20261013-020 were appended to the root ledger; its entire original prefix is preserved. No quantity, key, score, ID, ordering, markup or ruby reading changed. Source readings, alternatives and case statuses remain intact; current snapshots and live editorial-hash bindings were refreshed. No new uncertainty/departure or case resolution arises from width alone.

Ordinary editorial/case/fixlog/baseline/count validation and applicable principal/reference checks passed; exact ledger replay passed. Existing import-count warnings, when emitted, describe unchanged historical imports, not this normalization. Baseline and per-unit validator logs: ../../audit_runs/2026-10-13_digit_width_cleanup/.


## Housekeeping 2 — 5 November 2026

Reviewed all 10 mandatory identities for this unit plus three linked earlier cases against complete questions, choices, passages and the rendered principal/alternative layouts. Restored the STAR command’s final stop, おみやげ, provisional 眠る, provisional お疲れさま, both ご存じ spellings and 受付け終了. Retained the earlier とき and 二か月 edits and all independently supported timetable/postcode facts. Eight mandatory identities are resolved; the sleep verb and greeting retain meaningful historical uncertainty. Three linked cases have updated exact snapshots, with their independent uncertainty preserved.

Approved comparisons: OW2012 N3 G physical 6,8,9, V7 and R1,3,10; N3 July 2025 physical 8,23; N2 July 2018 physical 11–12 only. Analogies are explicitly separated from exact-item witnesses and negative search results. The separate notice image independently confirms 受付け even where its numbers disagree with the principal. Principal score 115 is unchanged. No frozen or current inferred ruby changed.

[Before/after decisions, exact observations, source lineage, explicit bindings and validation](../../audit_runs/2026-11-05_housekeeping2_ruby2_rebuild/units/N3_12_2020/disposition.json). The current text is revised locally; PDF/HTML regeneration belongs to the later release checkpoint.
