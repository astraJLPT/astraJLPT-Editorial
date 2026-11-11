# User-approved reference scans

Release adaptation of `preprocess/user_approved_reference_scans.md`, preserving all recorded hashes, page scopes, exclusions, and rejected candidates. The source file was left unchanged. Local links point to packaged full sources; clearly marked `src/` entries require the separately maintained collection. The [frozen machine registry](../pdf-render/contracts/reference-approvals.json) retains historical and official-workbook page arrays; modern approvals and the restricted N2 July 2018 scope are recorded below. Of the 62 approved full sources, 47 are packaged and 15 workbook components remain external.

## Decisions that remain in force

These are the **five retained editorial departures from approved scan pages**, supported by item-specific repairs or explicit editorial choices. They are exceptions with recorded reasons, not evidence for normalizing other papers. A principal difference describes an actual current departure; it does not automatically mean an error or uncertainty. A clear printed form can still be deliberately repaired when there is a strong reason.

Source-agreement rows and false comparisons are removed from this table. Public review cases are separate and follow the [phase-specific closure authority](audit-method/record-contract.md#case-status-and-closure-authority), including the authorized final housekeeping review after the main audit through 2010. Source agreement alone does not close them. N2 July 2018's missing-page/retyped-page cases are excluded from accepted-page calibration. The approved formatting suggestions have all been applied; their former comparisons and exact before/after values remain in the finalization run.

The links below point to live unit records; they own the current value, alternatives and rationale. Historical approval does not turn a selected repair into witnessed print. The difficulty rationale for the N2 compromise is not proof of exam intent.

| Review identity | Live authoritative records |
|---|---|
| N1_12_2023-PD-001 — name spelling | [Current departure](<N1/N1_12_2023/principal_differences_N1_12_2023.jsonl>), [case](<N1/N1_12_2023/unresolved_cases_N1_12_2023.jsonl>) |
| N2_12_2024-PD-001 — coordination | [Current departure](<N2/N2_12_2024/principal_differences_N2_12_2024.jsonl>), [case](<N2/N2_12_2024/unresolved_cases_N2_12_2024.jsonl>) |
| N2_12_2024-PD-002 — user compromise | [Current departure](<N2/N2_12_2024/principal_differences_N2_12_2024.jsonl>), [case](<N2/N2_12_2024/unresolved_cases_N2_12_2024.jsonl>) |
| N2_12_2024-PD-003 — extra particle | [Current departure](<N2/N2_12_2024/principal_differences_N2_12_2024.jsonl>), [case](<N2/N2_12_2024/unresolved_cases_N2_12_2024.jsonl>) |
| N3_07_2025-PD-004 — explanatory ending | [Current departure](<N3/N3_07_2025/principal_differences_N3_07_2025.jsonl>), [case](<N3/N3_07_2025/unresolved_cases_N3_07_2025.jsonl>) |

Verified style observations are summarized in [reference_scan_style_notes.md](audit-method/reference-style.md); operational defaults belong to [audit_order.md](audit-method/evidence-procedure.md#operational-decision-table). Neither changes this approval registry.

## Reference scope and provenance

Updated 23 October 2026: **62 approved full-source PDF identities — 17 modern sitting papers, 15 historical sources and 30 official-workbook components.** This release copy preserves the workspace registry’s exact files, approved physical pages and exclusions; it grants no new approval. Approval is attached to an unchanged full source; it does not authorize creating a page-selected replacement PDF. Keep answer forms, keys and other excluded pages in the original file and record their exclusion here.

The user corrected the earlier extract-based arrangement and authorized this migration. All 1,690 previously approved historical pages were matched pixel-for-pixel at 72 dpi to the full sources. Their approval boundaries are preserved. Full source hashes below identify the originals; old extract hashes are historical identities only. No new candidate was approved by this migration.

Local links are relative to this release registry. Paths explicitly marked `src/` identify the external source collection; historical workspace records are labelled separately. Page numbers are **one-based physical PDF pages**, not printed book folios. **Every page outside a listed historical or official-workbook range is excluded.** Within approved pages, handwriting, typed answer additions, publisher folios, watermarks and scanner artifacts are outside exam-layout authority. Approval concerns preserved question-page appearance, including section covers and listening where specified; it does not establish full question inventories, correct keys, independent custody, issuer authentication or original sheet dimensions. Old Levels 1-4 are not asserted equivalents of modern N1-N5.

Fourteen downloaded or user-supplied full originals are grouped in **UserApprovedReferenceScans** — external source: `src/CodexDownloads/UserApprovedReferenceScans` (not packaged). The pre-existing 2009 Level 4 source and the 17 modern references retain their existing source paths. Full sources and filenames are unchanged. `zdiamond_scans` is the user's private convenience folder: ignore it; do not read, synchronize, index or modify it as part of this workflow.

The former manual index and active generated extracts are in the stale archive — historical workspace record `stale archived files/2026-10-23_reference_index_integration` (not packaged). Earlier audit snapshots remain historical evidence. Migration record — historical workspace record `audit_runs/2026-10-23_reference_index_integration/completion.json` (not packaged) preserves the moves and page verification. [Source index](private/index_global.json.gz) owns discovery/provenance; the generated **convenience view** — external source: `src/CodexDownloads/UserApprovedReferenceScans/INDEX.generated.json` (not packaged) is disposable and cannot grant approval. Historical receipts and superseded records retain their original statements; use the source index's `previous_paths` to resolve relocated acquisitions.

## Historical full sources and page scopes

The following records replace the former extract targets. Earlier user approvals, including the six RC03 PDFs, the full 1996 question scan and the user-supplied 1993/1990 downloads, apply to these exact source-page spans. Existing modern approvals and rejections follow unchanged below.

### RC-COLLECTION-L4-1991-1999 — Level 4, 1991-1999

- Full source: [日本語能力1991～1999年試験問題集4級.pdf](<../astraJLPT/assets/principals/N4_1991_1999.pdf>)
- SHA-256: `6da6084a74b617608dfaef9bc70072dd8ea7bac410ef77de7ae90f5603c569db`
- Full PDF pages: 361
- Approved physical pages: `15-49,57-88,96-127,135-164,173-200,209-236,245-271,281-307,316-343`
- Approved page count: 267

The downloaded archive member is byte-identical to the previously used local Level 4 volume (same source SHA-256). Source physical 272, the damaged final 1997 reading page, is excluded. All other pages outside the approved ranges are excluded. Collection folios are not original exam pagination.

Year navigation (within the approved ranges above):

| Exam year | Physical pages |
|---|---|
| 1991 | 15-49 |
| 1992 | 57-88 |
| 1993 | 96-127 |
| 1994 | 135-164 |
| 1995 | 173-200 |
| 1996 | 209-236 |
| 1997 | 245-271 |
| 1998 | 281-307 |
| 1999 | 316-343 |

Earlier approval context: 2026-10-23_reference_scan_promotions — historical workspace record `audit_runs/2026-10-23_reference_scan_promotions/promotions.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC-L4-2009 — Level 4, December 2009

- Full source: [2009年日语能力考试四级真题及答案.pdf](<../astraJLPT/assets/principals/N4_2009.pdf>)
- SHA-256: `e988b85954586320fd139cedf003819db8699a0f15b5458d9e1d528e930384cb`
- Full PDF pages: 19
- Approved physical pages: `1-18`
- Approved page count: 18

Source page 19 is the excluded answer key. Typed answer additions on pages 5 and 7 are excluded from layout authority. H17 found ten of 87 scored written questions missing and an answer-key conflict. Faint print, cropping, watermarks and variable scale remain. This pre-existing source stays at its original path; it was not downloaded in this chat.

Earlier approval context: 2026-10-23_reference_scan_promotions — historical workspace record `audit_runs/2026-10-23_reference_scan_promotions/promotions.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### 1996_L1_L2 — Levels 1-2, 1996

- Full source: [Shiken mondai to seikai 1-2 kyuu 1996.pdf](<../astraJLPT/assets/principals/N_1-2_1996.pdf>)
- SHA-256: `aca213ce192a5fcf80f598c624953a533d49aef1971c318316996c7112b20873`
- Full PDF pages: 93
- Approved physical pages: `4-79`
- Approved page count: 76

The user explicitly approved the full 1996 question scan, superseding the earlier demo-only boundary. Vocabulary, listening and reading/grammar at both levels are approved within physical 4-79. Front matter, forms, keys and administration remain in the full file but are outside approval. The cartoon watermark, added book folios, scan speckle and uneven scale are not original exam geometry evidence.

Earlier approval context: 2026-10-23_reference_scan_promotions — historical workspace record `audit_runs/2026-10-23_reference_scan_promotions/online_approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### 1993_L1_L2 — Levels 1-2, 1993

- Full source: [505593162-JLPT-Japanese-Language-Proficiency-Test-1-2-kyuu-1993.pdf](<../astraJLPT/assets/principals/N_1-2_1993.pdf>)
- SHA-256: `fdd0d022acc4a1fffd3f9e5785b4a32d3d5a58d28c3d9c2bdeb9f65b10f5fe43`
- Full PDF pages: 82
- Approved physical pages: `3-74`
- Approved page count: 72

The user supplied the 82-page Scribd volume and delegated the PDF/DOCX choice. The PDF is the fixed-page reference. The 82-image DOCX remains an unselected companion in the RC03 hunt batch, not independent corroboration or proof of superior image quality. Front matter 1-2, answer forms 75-80 and keys 81-82 are outside approval. Printed folios skip 23 and 41; those gaps alone do not establish missing scored questions. Faint print and edge crops remain.

Earlier approval context: 2026-10-23_reference_scan_rc02_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc02_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### 2003_L3_L4 — Levels 3-4, 2003

- Full source: [2003_L3_L4_published_collection.pdf](<../astraJLPT/assets/principals/N_3-4_2003.pdf>)
- SHA-256: `2d6ad4834484c596d11bf48b4d529797d82d2800282d8e7a85d07f63d9913899`
- Full PDF pages: 123
- Approved physical pages: `5-15,24-78`
- Approved page count: 66

Source physical 16-23 are misplaced Level 4 listening transcripts, not question sheets, and remain excluded. Front matter, forms, keys and administration outside the listed ranges are excluded. The local filename is an acquisition alias; the remote original filename was not recorded and is not guessed.

Earlier approval context: 2026-10-23_reference_scan_rc02_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc02_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC03_L1 — Level 1, 1991-1999

- Full source: [日本語能力1991～1999年試験問題集1級.pdf](<../astraJLPT/assets/principals/N1_1991_1999.pdf>)
- SHA-256: `8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f`
- Full PDF pages: 447
- Approved physical pages: `15-45,53-60,62-86,94-131,139-176,185-223,232-272,281-322,331-374,383-431`
- Approved page count: 355

Source physical 61 (1992 vocabulary) is excluded for severe raster corruption. The 1993 and 1996 coverage overlaps other approved volumes; independent ancestry is not established. Added collection pagination, edge cropping and uneven print density remain.

Year navigation (within the approved ranges above):

| Exam year | Physical pages |
|---|---|
| 1991 | 15-45 |
| 1992 | 53-60,62-86 |
| 1993 | 94-131 |
| 1994 | 139-176 |
| 1995 | 185-223 |
| 1996 | 232-272 |
| 1997 | 281-322 |
| 1998 | 331-374 |
| 1999 | 383-431 |

Earlier approval context: 2026-10-23_reference_scan_rc03_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc03_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC03_L2 — Level 2, 1991-1999

- Full source: [日本語能力1991～1999年試験問題集2級.pdf](<../astraJLPT/assets/principals/N2_1991_1999.pdf>)
- SHA-256: `0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64`
- Full PDF pages: 417
- Approved physical pages: `15-46,54-84,92-125,133-166,175,177-210,219-253,262-300,309-334,338-348,357-399`
- Approved page count: 320

Source physical 176 (1995 vocabulary) is excluded for severe raster corruption. Source 335-337 (1998 reading) are publisher notices replacing passages and are excluded. Source 292 remains approved for its visible chart questions despite corruption below the charts. The overlapping 1993/1996 volumes are not assumed independent.

Year navigation (within the approved ranges above):

| Exam year | Physical pages |
|---|---|
| 1991 | 15-46 |
| 1992 | 54-84 |
| 1993 | 92-125 |
| 1994 | 133-166 |
| 1995 | 175,177-210 |
| 1996 | 219-253 |
| 1997 | 262-300 |
| 1998 | 309-334,338-348 |
| 1999 | 357-399 |

Earlier approval context: 2026-10-23_reference_scan_rc03_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc03_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC03_L3 — Level 3, 1991-1999

- Full source: [日本語能力1991～1999年試験問題集3級.pdf](<../astraJLPT/assets/principals/N3_1991_1999.pdf>)
- SHA-256: `4af8ec5c1039430637c36a7bd3ac9c1c031536e32a6f5bc89e405b7210d29ae1`
- Full PDF pages: 382
- Approved physical pages: `15-47,55-84,92-123,131-161,170-201,210-239,248-282,291-322,331-364`
- Approved page count: 289

Source 61 and 63 (1992) retain visible question text despite heavy speckle, dark borders and ghosting. The separate acquisition named 1991-1999_L3_collection.pdf has the same SHA-256 and remains a duplicate acquisition in the RC03 hunt batch, not an additional witness.

Year navigation (within the approved ranges above):

| Exam year | Physical pages |
|---|---|
| 1991 | 15-47 |
| 1992 | 55-84 |
| 1993 | 92-123 |
| 1994 | 131-161 |
| 1995 | 170-201 |
| 1996 | 210-239 |
| 1997 | 248-282 |
| 1998 | 291-322 |
| 1999 | 331-364 |

Earlier approval context: 2026-10-23_reference_scan_rc03_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc03_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC03_2001 — 2001, Levels 3-4

- Full source: [JLPT Shiken Mondai to Seikai 3-4 kyuu 2001.pdf](<../astraJLPT/assets/principals/N_3-4_2001.pdf>)
- SHA-256: `da4f4bb4349572963e4a6c6413370ce8c62c287202b06fc6a701b57b91e12084`
- Full PDF pages: 83
- Approved physical pages: `4-68`
- Approved page count: 65

The approved ranges include vocabulary, listening and reading/grammar at both old levels. Substantial reverse-side show-through, uneven gutter shadow, pale print and edge cropping remain.

Earlier approval context: 2026-10-23_reference_scan_rc03_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc03_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC03_2004 — 2004, Levels 3-4

- Full source: [Nihongo nouryoku shiken shiken mondai to seikai  3-4 kyo (2004).pdf](<../astraJLPT/assets/principals/N_3-4_2004.pdf>)
- SHA-256: `cecff06d3cd84c45aadc4dcc7b40c04af99261a8a09edc30f607806ef6d59cd8`
- Full PDF pages: 120
- Approved physical pages: `4-68`
- Approved page count: 65

The approved ranges include vocabulary, listening and reading/grammar at both old levels. Substantial reverse-side show-through, skew and parts of facing pages remain visible.

Earlier approval context: 2026-10-23_reference_scan_rc03_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc03_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC03_2005 — 2005, Levels 3-4

- Full source: [JLPT Shiken Mondai to Seikai 3-4 kyuu 2005.pdf](<../astraJLPT/assets/principals/N_3-4_2005.pdf>)
- SHA-256: `070da4fbe5bbaccbd606d160b0920e23251c4162332b7cbe4f9bdb3b1535449d`
- Full PDF pages: 120
- Approved physical pages: `4-67`
- Approved page count: 64

The approved ranges include vocabulary, listening and reading/grammar at both old levels. Substantial reverse-side show-through, uneven gutter shadow and pale print remain.

Earlier approval context: 2026-10-23_reference_scan_rc03_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc03_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### 1990_L4 — Level 4, 1990

- Full source: [903181477-4級-問題用紙-1990年度能力試験-4.pdf](<../astraJLPT/assets/principals/N4_1990.pdf>)
- SHA-256: `d1d016993f12e3fce9cebf177bf67534440c2e17668c2865f2d817c41d611395`
- Full PDF pages: 37
- Approved physical pages: `1-33`
- Approved page count: 33

Source physical 1-8 are vocabulary, 9-22 listening, and 23-33 reading/grammar. Forms 34-36 and key 37 are excluded. Handwritten answer marks, including the circled choice on source 31, are outside exam-layout authority. The full source was supplied through the user’s latest RC03 Drive folder and verified against cloud MD5/size and local SHA-256. This establishes a 1990 Level 4 reference, not early-year coverage at other levels.

Earlier approval context: 2026-10-23_reference_scan_rc03_approvals — historical workspace record `audit_runs/2026-10-23_reference_scan_rc03_approvals/approvals.json` (not packaged). Its extract paths and old pending labels are superseded by this record.

### RC04_2007_L3_L4 — Levels 3-4, 2007

- Full source: [pdf-20074_compress.pdf](<../astraJLPT/assets/principals/N_3-4_2007.pdf>)
- SHA-256: `6902181b1ced1babb1aa2eb9ae4f9bc58bb96aa1780141628ff13ed7c03d03f6`
- Full PDF pages: 95
- Approved physical pages: `5-15,17-29,31-37,39-67,69-72`
- Approved page count: 64

The filename refers to Level 4, but the scanned volume contains both old Levels 3 and 4. Level 3 question pages are 5-15, 17-29, 31-37 and 39-42; Level 4 question pages are 43-67 and 69-72. These ranges include vocabulary, listening and reading/grammar section covers and questions. Pattern-only pages 38 and 68, blank pages 16 and 30, front matter 1-4, answer forms 73-78, keys 79-82 and subsequent administrative/back matter are excluded. Black gutter shadows, skew, show-through and fragments of facing pages remain; those artifacts are outside exam-layout authority.

Approval: the user supplied these attachments on 23 October 2026 and explicitly approved them all, authorizing deduplication. The supplied full PDF is preserved without extraction or recompression. Acquisition and deduplication receipt — historical workspace record `audit_runs/2026-10-23_reference_scan_rc04_approvals/approvals.json` (not packaged).

### RC04_2008_L3_L4 — Levels 3-4, 2008

- Full source: [pdf-jlpt3-4kyuu2008_compress.pdf](<../astraJLPT/assets/principals/N_3-4_2008.pdf>)
- SHA-256: `90f934091cf24e333a6a05e58e8c047fc1562793aa07265245562882e0bc6d0f`
- Full PDF pages: 134
- Approved physical pages: `6-16,18-30,32-38,40-68,70-74`
- Approved page count: 65

Level 3 question pages are 6-16, 18-30, 32-38 and 40-43; Level 4 question pages are 44-68 and 70-74. These ranges include vocabulary, listening and reading/grammar section covers and questions. Pattern-only pages 39 and 69, blank pages 17 and 31, front matter 1-5 and all material from 75 onward are excluded. The latter includes forms 76-81, keys 82-85, statistics, listening transcripts 105-115 and 117-124, advertisements and back matter. Library stamps, handwriting, skew and scan artifacts are outside exam-layout authority. The second 2008 attachment is byte-identical; only one canonical source is retained.

Approval: the user supplied these attachments on 23 October 2026 and explicitly approved them all, authorizing deduplication. The supplied full PDF is preserved without extraction or recompression. Acquisition and deduplication receipt — historical workspace record `audit_runs/2026-10-23_reference_scan_rc04_approvals/approvals.json` (not packaged).

### RC04_2009_L3 — Level 3, December 2009

- Full source: [pdf-3-2120092_compress.pdf](<../astraJLPT/assets/principals/N3_2009.pdf>)
- SHA-256: `f926974366388be7fd6b301c6299b59c1b7f07d940549dc6c221cb5a45d6f4c7`
- Full PDF pages: 42
- Approved physical pages: `2-32,34-37`
- Approved page count: 35

This upload contains the old Level 3 selection from the December 2009 annual volume; it does not establish Level 4 coverage. Physical 2-12 are vocabulary, 13-25 listening, and 26-32 plus 34-37 reading/grammar, including their section covers. Book cover 1, pattern-only page 33, answer forms 38-40 and keys 41-42 are excluded. The PDF contains scanned page imagery assembled in a Word-produced container; the container metadata does not establish original sheet dimensions. Variable image scale, cropping and added folios remain outside exam-layout authority.

Approval: the user supplied these attachments on 23 October 2026 and explicitly approved them all, authorizing deduplication. The supplied full PDF is preserved without extraction or recompression. Acquisition and deduplication receipt — historical workspace record `audit_runs/2026-10-23_reference_scan_rc04_approvals/approvals.json` (not packaged).

## Approved files — modern papers

| Paper | Exact source PDF |
|---|---|
| N1_12_2023 | [src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N1真题/2023年12月/【2】2023年12月N1 真题.pdf](<../astraJLPT/assets/principals/N1_12_2023.pdf>) |
| N1_07_2025 | [src/日语JLPT历年真题/N1真题（2010-2026.07）/2025/2025.07/2025年07月N1真题.pdf](<../astraJLPT/assets/principals/N1_07_2025.pdf>) |
| N1_12_2025 | [src/JLPT_N1_N5_202512/25年12月N1/A 2025年12月N1完整原卷.pdf](<../astraJLPT/assets/principals/N1_12_2025.pdf>) |
| N2_07_2018 | [src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道二/N2历年真题/2010-2017.12高清无水印/N2 2010.7-2017.12（真题试题）/2018年7月日语N2真题-第一版（官方试卷版）.pdf](<../astraJLPT/assets/principals/N2_07_2018.pdf>) — SHA-256 `58f26b8a8b300047480495f64daa76b90359b7f4d1631c8f0e9c8f78c9ed6013`; **physical 2–9 and 11–29 only**. See limitations below. |
| N2_12_2023 | [src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道二/N2历年真题/2023.12/2023年12月N2真题.pdf](<../astraJLPT/assets/principals/N2_12_2023.pdf>) |
| N2_12_2024 | [src/Yuuki Bui/Đề thi N2 các năm Yuuki Bùi/N2 12-2024/Đề N2 12-2024 Bản hoàn chỉnh \[Mark\].pdf](<../astraJLPT/assets/principals/N2_12_2024.pdf>) |
| N2_07_2025 | [src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/2025年7月/【试题】2025年7月JLPT真题N2.pdf](<../astraJLPT/assets/principals/N2_07_2025.pdf>) |
| N2_12_2025 | [src/JLPT_N1_N5_202512/25年12月N2/A 2025年12月N2完整原卷.pdf](<../astraJLPT/assets/principals/N2_12_2025.pdf>) |
| N3_12_2023 | [src/Yuuki Bui/Đề thi N3 các năm Yuuki Bùi/N3 12-2023/Đề N3 T12-2023 Full YuukiBui.pdf](<../astraJLPT/assets/principals/N3_12_2023.pdf>) |
| N3_12_2024 | [src/Yuuki Bui/Đề thi N3 các năm Yuuki Bùi/N3 12-2024/Đề thi N3 T12-2024 Bản hoàn chỉnh \[Mark\].pdf](<../astraJLPT/assets/principals/N3_12_2024.pdf>) |
| N3_07_2025 | [src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N3真题/2025年7月/【试题】2025年7月JLPT日语N3真题.pdf](<../astraJLPT/assets/principals/N3_07_2025.pdf>) |
| N3_12_2025 | [src/JLPT_N1_N5_202512/25年12月N3/25年12月N3真题.pdf](<../astraJLPT/assets/principals/N3_12_2025.pdf>) |
| N4_12_2024 | [src/Yuuki Bui/Đề thi N4-N5 các năm Yuuki Bùi/2024年12月/N4 T12-2024/Đề thi N4 T12-2024 Bản hoàn chỉnh \[Mark\].pdf](<../astraJLPT/assets/principals/N4_12_2024.pdf>) |
| N4_07_2025 | [src/日语JLPT历年真题/N4真题（2010-2025.12）/【N4真题】2025年7月/【试题】2025年7月JLPT日语N4真题.pdf](<../astraJLPT/assets/principals/N4_07_2025.pdf>) |
| N4_12_2025 | [src/JLPT_N1_N5_202512/25年12月N4/25年12月N4真题.pdf](<../astraJLPT/assets/principals/N4_12_2025.pdf>) |
| N5_07_2025 | [src/日语JLPT历年真题/N5真题（2010-2025.12）/【N5真题】2025年7月/【试题】2025年7月JLPT日语N5真题.pdf](<../astraJLPT/assets/principals/N5_07_2025.pdf>) |
| N5_12_2025 | [src/JLPT_N1_N5_202512/25年12月N5/25年12月N5真题.pdf](<../astraJLPT/assets/principals/N5_12_2025.pdf>) |

## Approved official-workbook formatting references

The user approved the 2012/2018 workbook proposal in this conversation and confirmed continuation after the proposed 256-question-page scope was stated. These 30 exact full PDFs remain at their original paths. Approval supplies question-page formatting evidence only; publication years do not identify historical sittings. Covers and patterned non-question pages outside the ranges below are excluded. No PDF was extracted or rewritten. The dated RC01 proposal retains its historical pending labels; this registry is current authority.

### OW2012_N1_G — Official Workbook 2012, N1 G

- Full source: **N1G.pdf** — external source: `src/OfficialWorkbooks/2012/N1/N1G.pdf` (not packaged)
- SHA-256: `32ed971bda7ba60859125e2cc78a0e34f5b5f730410d63fd624a5cf2a15a2d89`
- Full PDF pages: 6
- Approved physical pages: `1-6`
- Approved page count: 6

Source: https://www.jlpt.jp/samples/sample2012/pdf/N1G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N1_R — Official Workbook 2012, N1 R

- Full source: **N1R.pdf** — external source: `src/OfficialWorkbooks/2012/N1/N1R.pdf` (not packaged)
- SHA-256: `d8c79e9c8ac33e2e2ff860d0f49bd9c95b84719b51d6498f201eecc4b6698f02`
- Full PDF pages: 20
- Approved physical pages: `1-3,5-17,19-20`
- Approved page count: 18

Source: https://www.jlpt.jp/samples/sample2012/pdf/N1R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N1_V — Official Workbook 2012, N1 V

- Full source: **N1V.pdf** — external source: `src/OfficialWorkbooks/2012/N1/N1V.pdf` (not packaged)
- SHA-256: `75842c9076e08724fc2bec4f0539796c1f9ca1b939e7e5d1c5958d15d3ebcfc7`
- Full PDF pages: 7
- Approved physical pages: `3-7`
- Approved page count: 5

Source: https://www.jlpt.jp/samples/sample2012/pdf/N1V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N2_G — Official Workbook 2012, N2 G

- Full source: [N2G.pdf](<../astraJLPT/assets/principals/N2_2012_Workbook_Grammar.pdf>)
- SHA-256: `54e8adda3364c0aa3f9c015c932abeb0ad2511d7d98a4d60134befdfb932b213`
- Full PDF pages: 7
- Approved physical pages: `1-4,6-7`
- Approved page count: 6

Source: https://www.jlpt.jp/samples/sample2012/pdf/N2G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N2_R — Official Workbook 2012, N2 R

- Full source: [N2R.pdf](<../astraJLPT/assets/principals/N2_2012_Workbook_Reading.pdf>)
- SHA-256: `c8a56a78a7996c426ffff0cf438162c1af1917a7d6927bce624c69c1e573e9fe`
- Full PDF pages: 18
- Approved physical pages: `1-5,7-18`
- Approved page count: 17

Source: https://www.jlpt.jp/samples/sample2012/pdf/N2R.pdf. All unlisted pages are excluded; the full original is retained.

User-authorized range correction, 23 October 2026: physical page 6 is a patterned blank and is excluded; physical page 7 contains the reading passage and is approved. This corrects the swapped page selection in the historical RC01 proposal. The approved count remains 17, and the original PDF and prior content audit are unchanged.

### OW2012_N2_V — Official Workbook 2012, N2 V

- Full source: [N2V.pdf](<../astraJLPT/assets/principals/N2_2012_Workbook_Vocab.pdf>)
- SHA-256: `7e037f5e7380bc0db46e4b064785da44b81604b77e63c5a2a93b083ee52f3855`
- Full PDF pages: 8
- Approved physical pages: `3-8`
- Approved page count: 6

Source: https://www.jlpt.jp/samples/sample2012/pdf/N2V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N3_G — Official Workbook 2012, N3 G

- Full source: **N3G.pdf** — external source: `src/OfficialWorkbooks/2012/N3/N3G.pdf` (not packaged)
- SHA-256: `2739ba38b98ba697f5a16a1a99eef59b25b9ac0cf573b7730a87c6d6f41e00e8`
- Full PDF pages: 9
- Approved physical pages: `3-6,8-9`
- Approved page count: 6

Source: https://www.jlpt.jp/samples/sample2012/pdf/N3G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N3_R — Official Workbook 2012, N3 R

- Full source: **N3R.pdf** — external source: `src/OfficialWorkbooks/2012/N3/N3R.pdf` (not packaged)
- SHA-256: `64bab971e58cac59dfed6486ff6f8786336bd6a6693ff404fc2721cdb65fd35d`
- Full PDF pages: 12
- Approved physical pages: `1-12`
- Approved page count: 12

Source: https://www.jlpt.jp/samples/sample2012/pdf/N3R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N3_V — Official Workbook 2012, N3 V

- Full source: **N3V.pdf** — external source: `src/OfficialWorkbooks/2012/N3/N3V.pdf` (not packaged)
- SHA-256: `e80bfe5be25d1c06df901a6f1b0f590cd7927160e374c12ded18e8dfb0b4eb79`
- Full PDF pages: 7
- Approved physical pages: `3-7`
- Approved page count: 5

Source: https://www.jlpt.jp/samples/sample2012/pdf/N3V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N4_G — Official Workbook 2012, N4 G

- Full source: **N4G.pdf** — external source: `src/OfficialWorkbooks/2012/N4/N4G.pdf` (not packaged)
- SHA-256: `26a1d87cd5292a64ed121d7db20fdd4ba1479eb70682e1f8e0d14f471ad664c3`
- Full PDF pages: 9
- Approved physical pages: `3-9`
- Approved page count: 7

Source: https://www.jlpt.jp/samples/sample2012/pdf/N4G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N4_R — Official Workbook 2012, N4 R

- Full source: **N4R.pdf** — external source: `src/OfficialWorkbooks/2012/N4/N4R.pdf` (not packaged)
- SHA-256: `458d54165382fc24f81ceb9591e689e3a39316f3fe6684eef2a731a46f457c97`
- Full PDF pages: 8
- Approved physical pages: `1-8`
- Approved page count: 8

Source: https://www.jlpt.jp/samples/sample2012/pdf/N4R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N4_V — Official Workbook 2012, N4 V

- Full source: **N4V.pdf** — external source: `src/OfficialWorkbooks/2012/N4/N4V.pdf` (not packaged)
- SHA-256: `57f23ae9022158d7ab19cd73d5034c0b4569381933856032f38bc25d9af3b10f`
- Full PDF pages: 11
- Approved physical pages: `3-11`
- Approved page count: 9

Source: https://www.jlpt.jp/samples/sample2012/pdf/N4V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N5_G — Official Workbook 2012, N5 G

- Full source: **N5G.pdf** — external source: `src/OfficialWorkbooks/2012/N5/N5G.pdf` (not packaged)
- SHA-256: `16fe39e16455c658a2095bfa44313b2259c8ea273bdd9660af7f12ea49bb5332`
- Full PDF pages: 9
- Approved physical pages: `3-9`
- Approved page count: 7

Source: https://www.jlpt.jp/samples/sample2012/pdf/N5G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N5_R — Official Workbook 2012, N5 R

- Full source: **N5R.pdf** — external source: `src/OfficialWorkbooks/2012/N5/N5R.pdf` (not packaged)
- SHA-256: `a4caed63529eef176e052737f2d63a9b3c05d143ac919cc9399030c41d42c795`
- Full PDF pages: 8
- Approved physical pages: `1-3,5-8`
- Approved page count: 7

Source: https://www.jlpt.jp/samples/sample2012/pdf/N5R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2012_N5_V — Official Workbook 2012, N5 V

- Full source: **N5V.pdf** — external source: `src/OfficialWorkbooks/2012/N5/N5V.pdf` (not packaged)
- SHA-256: `33e5648fe40b1c3effb45205fc37f58887e991bd287b06c3c9104e1a6a1c93c4`
- Full PDF pages: 10
- Approved physical pages: `3-10`
- Approved page count: 8

Source: https://www.jlpt.jp/samples/sample2012/pdf/N5V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N1_G — Official Workbook 2018, N1 G

- Full source: [N1G.pdf](<../astraJLPT/assets/principals/N1_2018_Workbook_Grammar.pdf>)
- SHA-256: `7c5e73d4f4a89444b1f98679a99a98a953c0b6ae0dca9eeb09815868b152ea83`
- Full PDF pages: 6
- Approved physical pages: `1-6`
- Approved page count: 6

Source: https://www.jlpt.jp/samples/sample2018/pdf/N1G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N1_R — Official Workbook 2018, N1 R

- Full source: [N1R.pdf](<../astraJLPT/assets/principals/N1_2018_Workbook_Reading.pdf>)
- SHA-256: `1a66842a3c8593bc2cc522fb7e8bf6bc840ae49bceb82dff095474c5efff8fac`
- Full PDF pages: 20
- Approved physical pages: `1-17,19-20`
- Approved page count: 19

Source: https://www.jlpt.jp/samples/sample2018/pdf/N1R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N1_V — Official Workbook 2018, N1 V

- Full source: [N1V.pdf](<../astraJLPT/assets/principals/N1_2018_Workbook_Vocab.pdf>)
- SHA-256: `c315b971250bf68667a8c38d534272c8e3c0bdb4caa517477fcc572b75c01e0d`
- Full PDF pages: 7
- Approved physical pages: `3-7`
- Approved page count: 5

Source: https://www.jlpt.jp/samples/sample2018/pdf/N1V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N2_G — Official Workbook 2018, N2 G

- Full source: [N2G.pdf](<../astraJLPT/assets/principals/N2_2018_Workbook_Grammar.pdf>)
- SHA-256: `b48d6e9002c981ca3d4250db4d0961a97d53145402b5eca058c2eb6fe75185e6`
- Full PDF pages: 6
- Approved physical pages: `1-6`
- Approved page count: 6

Source: https://www.jlpt.jp/samples/sample2018/pdf/N2G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N2_R — Official Workbook 2018, N2 R

- Full source: [N2R.pdf](<../astraJLPT/assets/principals/N2_2018_Workbook_Reading.pdf>)
- SHA-256: `cae736f4da5baa87fedbc9457964d86ca90cbc1e3f6b3f2d7a405e3a33563f23`
- Full PDF pages: 20
- Approved physical pages: `1-3,5-7,9-20`
- Approved page count: 18

Source: https://www.jlpt.jp/samples/sample2018/pdf/N2R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N2_V — Official Workbook 2018, N2 V

- Full source: [N2V.pdf](<../astraJLPT/assets/principals/N2_2018_Workbook_Vocab.pdf>)
- SHA-256: `c16247e1e6dc3c8b06dc0caf0ea94b7201628c3032c18bb2cc2ac0b1e69f79d6`
- Full PDF pages: 9
- Approved physical pages: `3-8`
- Approved page count: 6

Source: https://www.jlpt.jp/samples/sample2018/pdf/N2V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N3_G — Official Workbook 2018, N3 G

- Full source: [N3G.pdf](<../astraJLPT/assets/principals/N3_2018_Workbook_Grammar.pdf>)
- SHA-256: `fe4e17dec0eae246839a7a32423e9e9fc3beaca3a2c693bd5445cafd6f0bfc06`
- Full PDF pages: 9
- Approved physical pages: `3-9`
- Approved page count: 7

Source: https://www.jlpt.jp/samples/sample2018/pdf/N3G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N3_R — Official Workbook 2018, N3 R

- Full source: [N3R.pdf](<../astraJLPT/assets/principals/N3_2018_Workbook_Reading.pdf>)
- SHA-256: `1d56df57040ffe1da41c2cb6f152e3926d84fb5a17b7b25b348b01cfb9c89e69`
- Full PDF pages: 12
- Approved physical pages: `1-7,9-12`
- Approved page count: 11

Source: https://www.jlpt.jp/samples/sample2018/pdf/N3R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N3_V — Official Workbook 2018, N3 V

- Full source: [N3V.pdf](<../astraJLPT/assets/principals/N3_2018_Workbook_Vocab.pdf>)
- SHA-256: `66abec06d2e23d2ee66b94cdf905b34cc87f97a5ce0ce5da47dc304053d647ea`
- Full PDF pages: 7
- Approved physical pages: `3-7`
- Approved page count: 5

Source: https://www.jlpt.jp/samples/sample2018/pdf/N3V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N4_G — Official Workbook 2018, N4 G

- Full source: [N4G.pdf](<../astraJLPT/assets/principals/N4_2018_Workbook_Grammar.pdf>)
- SHA-256: `da3bec0d70fef11aa9291b12d56a964b99064c77d1bac4dbe9f17d01c92f08a7`
- Full PDF pages: 9
- Approved physical pages: `3-9`
- Approved page count: 7

Source: https://www.jlpt.jp/samples/sample2018/pdf/N4G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N4_R — Official Workbook 2018, N4 R

- Full source: [N4R.pdf](<../astraJLPT/assets/principals/N4_2018_Workbook_Reading.pdf>)
- SHA-256: `9cbfae13f485f6cb9cbae58dab79efa9f840377016566adaacd41e9586ad9a08`
- Full PDF pages: 8
- Approved physical pages: `1-8`
- Approved page count: 8

Source: https://www.jlpt.jp/samples/sample2018/pdf/N4R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N4_V — Official Workbook 2018, N4 V

- Full source: [N4V.pdf](<../astraJLPT/assets/principals/N4_2018_Workbook_Vocab.pdf>)
- SHA-256: `acda221ce269e6e60674ee9f340833eb18cf06a95425e97b0f3feed8fa5a66ec`
- Full PDF pages: 11
- Approved physical pages: `3-11`
- Approved page count: 9

Source: https://www.jlpt.jp/samples/sample2018/pdf/N4V.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N5_G — Official Workbook 2018, N5 G

- Full source: **N5G.pdf** — external source: `src/OfficialWorkbooks/2018/N5/N5G.pdf` (not packaged)
- SHA-256: `cba53d2111eec8b33adb85641e5fd41b4c3f775ef4553448b59aa15d638b040a`
- Full PDF pages: 9
- Approved physical pages: `3-9`
- Approved page count: 7

Source: https://www.jlpt.jp/samples/sample2018/pdf/N5G.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N5_R — Official Workbook 2018, N5 R

- Full source: **N5R.pdf** — external source: `src/OfficialWorkbooks/2018/N5/N5R.pdf` (not packaged)
- SHA-256: `1a3ff408e7cdc29243a990d503c4d5dde71cdf9c3cf847245932ffa81322ba7c`
- Full PDF pages: 8
- Approved physical pages: `1-3,5-8`
- Approved page count: 7

Source: https://www.jlpt.jp/samples/sample2018/pdf/N5R.pdf. All unlisted pages are excluded; the full original is retained.

### OW2018_N5_V — Official Workbook 2018, N5 V

- Full source: **N5V.pdf** — external source: `src/OfficialWorkbooks/2018/N5/N5V.pdf` (not packaged)
- SHA-256: `44d6c36e877b5cace8cbbb3d96d7d6114d69d8f48520fc2a7bac0a4273307575`
- Full PDF pages: 10
- Approved physical pages: `3-10`
- Approved page count: 8

Source: https://www.jlpt.jp/samples/sample2018/pdf/N5V.pdf. All unlisted pages are excluded; the full original is retained.

## N2 July 2018 approval scope

The user accepted this exact file on 5 October 2026 as a reference scan for its preserved written pages. Physical **2–7** correspond to printed **1–6**; physical **8–9** to printed **8–9**; physical **11–17** to printed **12–18**; physical **18–29** to printed **20–31**.

Physical **10** is an unnumbered **retyped Q44–49 insert** and is **not approved reference evidence**. Original printed pages **7, 10, 11 and 19 are missing**. Cover 1 and listening 30–42 are outside written style approval. The related Yuuki overlay does not receive approval by association and is not independent corroboration.

The main audit and editorial are accepted, with the requested `<ruby>則<rt>すなわ</rt></ruby>ち` restoration and removal of Q71 options 3/4 terminal stops. All 75 scored questions remain available. The original STAR worked example remains unrecovered. On 9 October 2026 the user changed the practice classification to complete scored-question coverage (`audited_with_uncertainty`); the example gap remains in the open review case without a partial-paper label. Approval boundaries and O5 are unchanged. `TS-SOKUCHI`, `TS-Q45-BOUNDARY` and `TS-COVERAGE` stay **OPEN**. The latter two concern unapproved/absent pages and are not trusted-page style decisions. Source agreement removes PD-001, PD-008 and PD-009 from the current departure register without closing TS-SOKUCHI. PD-002 was also retired as a false comparison: physical 3 has no comma after `ものを`, matching the editorial. The seven approved formatting restorations (PD-003/004/005/007/010/011/012) are now applied and no longer current departures. PD-006 remains on the excluded retyped page 10; it is not a trusted-page style decision.

## Explicitly rejected candidates

These exact files were **rejected by the user on 5 October 2026**, not approved or pending approval. Treat them as **retyped reproductions with substantial effort to imitate JLPT typesetting**, under the user’s classification. Their audit evidence remains useful as secondary transcription evidence, never trusted scan/style evidence. This verdict is limited to the identified files.

| Paper / rejected file | SHA-256 | Recorded reason |
|---|---|---|
| N1_07_2021 — **N1 T7-2021 Ver2.0 Sign.pdf** — external source: `src/Yuuki Bui/Đề thi N1 các năm Yuuki Bùi/N1 7-2021/N1 T7-2021 Ver2.0 Sign.pdf` (not packaged) | `16c875fd8c3bbcae41e0b34287b99917103183a7f7c6f40e7a8fbaced3b4d0da` | Q26 option2 prints `ならまだし`, losing the final `も` of `ならまだしも` (archived PD-071); contact text prints `チケットオフィステ155-8547` (PD-106); many further departures. |
| N2_07_2024 — **【3】2024年07月N2 真题.pdf** — external source: `src/日语JLPT真题1992～2025.12（及时转存，避免丢失）/渠道一/日语N2真题/2024年7月/【3】2024年07月N2 真题.pdf` (not packaged) | `4fbc5a5eedf27b9afb9516103dd1058f7919cdb49ab8acc0c0bc9c3389060952` | Q3 prints `髪の毛がに`, omitting `くし` (archived PD-061); many further departures. |

Their former main audits/principals are restored exactly. See the restoration and archive map — historical workspace record `audit_runs/2026-10-05_user_verdict_restore/README.md` (not packaged). Historical hunt candidate/pending labels are superseded by this verdict. Neither rejected file was in the earlier approved-file table or its cached approved-scan inventory.
