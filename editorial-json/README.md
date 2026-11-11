# Editorial JSON

This is mostly for machines. The idea is to make the content easy to convert into whatever you want: another reader, a study tool, a printable format, or something I haven’t thought of. Give it to your LLM agent and go wild.

For the audit, I gave the LLM guidelines and let it investigate the material in my `src/` folder. It used OCR or extracted text to find content, inspected source pages, compared useful witnesses, and worked through problems in the questions. Mistakes were fixed by GPT-6 Astra at max reasoning effort. The result still includes uncertain reconstructions and missing content; those are part of the record, not something to hide.

Changes were saved in the per-unit **fixlog** ledger, maintained as one compressed history under `private/<level>/<unit>/fixlog_<unit>.jsonl.gz`. The audit also produced the public **unresolved cases** and **principal differences** beside each editorial. [The adapted audit guide](audit-method/README.md) explains how the work was done and includes the essential supporting contracts. It is adapted from the workspace’s `preprocess/readme.md`, not a verbatim copy or a new instruction to restart its completed runs.

“Private” means: I didn’t originally intend to publish these working records, but they may be useful if you want to continue the work or understand why things are the way they are. These files are included in this repository.

[`private/index_global.json.gz`](private/index_global.json.gz) indexes selected source material and acquisition records. It excludes audio/video and some other files in `src/`. That source tree is maintained separately and is not uploaded here in full. A `src/` path in an old record identifies that external collection; it is not a broken promise that the file exists inside this checkout.

## Reading the files

For a unit such as `N2_workbook_2012`, look in `N2/N2_workbook_2012/`:

| File | Purpose |
|---|---|
| `editorial_<unit>.json` | Authoritative question content, source ruby, answers, explanations, layout, and provenance. |
| `ruby_<unit>.json` | Installed project-added ruby, kept separate from witnessed source ruby. |
| `principal_differences_<unit>.jsonl` | Current meaningful departures from the principal source. |
| `unresolved_cases_<unit>.jsonl` | Higher-risk provisional fixes, unsettled alternatives, missing content, and retained resolutions. |

Each nonblank JSONL line is a separate JSON object. Empty public registers mean no rows are recorded; they do not by themselves prove complete comparison or perfect source fidelity. Investigation coverage belongs in the archived audit note.

The public [reference-scan registry](user_approved_reference_scans.md) preserves approved full-file hashes, page scopes, exclusions, rejected candidates, and decisions still in force. It includes clearly marked external sources as well as local principal links. Approval does not necessarily cover an entire PDF.

## For developers and agents

The release editorials use schema **4.1.0**. Their historical audits used earlier schemas, and the historical fixlog entries are not a patch stream to apply blindly to v4. The active [modern schema](../pdf-render/schema/editorial.schema.json) and [historical schema](../pdf-render/schema/historical-1991-2009/editorial.schema.json), along with the [record contract](audit-method/record-contract.md), describe the current representation. Scored sentence-composition questions also carry [structured STAR solutions and review evidence](STAR.md). Retain stable item IDs, answer-option order, typed values, explanations, and meaningful ruby/underline/table markup. A string and `{ "html": "…" }` are different representations; do not discard the distinction.

Defaults and rendering paths are relative to the repository root; the ruby sidecar path is relative to its editorial. Source ruby stays in the editorial. Apply the selected sidecar through the compositor, which checks field hashes, spans, overlaps, protected tasks, and release bindings. [PDF regeneration](../pdf-render/README.md) documents that entry point. Scraping the rendered HTML discards some editorial structure.

Use [unit_aliases.json](unit_aliases.json) when joining frozen records to current units. Eight misleading sitting IDs became `N#_workbook_2012` or `N#_workbook_2018`; two expanded sets became `N1_set_2011_2012` and `N3_set_2011_2012`. Historical fixlogs, source-set identities, research queues, annotation IDs, and public case/difference IDs keep their original spelling. Match the row’s current `unit`, then preserve its stable record ID; do not infer identity from an ID prefix alone.

The [publication registry](publication_registry.json) distinguishes complete workbook owners from workbook content contained within a larger set. Its earlier revision hashes remain historical; `release_content_binding` identifies the renamed live editorial. The N1/N3 expanded sets include all the respective 2012 workbook’s scored questions plus additional material; they are not interchangeable with the official downloads.

The current [Uncertainty Index](uncertainty_index.json) uses `method_version: 2`; its format tag remains `uncertainty_index_v1`. It describes browsing order for the written collection. The archived [principal uncertainty index](private/principal_uncertainty_index.json.gz) assesses selected historical sources on a different scale. Read [the assessment methods](audit-method/assessment-methods.md) before joining or comparing their numbers.

`private/<level>/<unit>/` also contains `editorial_audit.md` and `index_<unit>.json`. Those and the compressed fixlogs preserve historical path strings and observations. [The resource map](../pdf-render/contracts/resource-map.json) resolves packaged dependencies; [source references](../pdf-render/contracts/source-references.json) distinguish local files from historical evidence that is not packaged. A source-set manifest’s hash is its own identity, not the hash of any PDF member.

For a change to authoritative content, first preserve a baseline, review the relevant sources and public records, and update the relevant evidence and bindings together. Hash checks detect changed inputs; they do not prove linguistic correctness, source authentication, or visual fidelity. The supported release checks are `python verify.py`, the renderer’s validation/emission command, HTML body verification, and the frozen ruby replay described in their respective READMEs.
