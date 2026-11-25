# Editorial and review records — adapted contract

This adapts `preprocess/editorial_contract.md` to the released v4 layout. The earlier audit used older schema versions and kept its ledger beside the editorial. Here, each unit has one maintained compressed ledger under `editorial-json/private/`; historical entries retain their original content and formats.

## Current editorial and ruby

`editorial_<unit>.json` is the authoritative v4 document. Preserve typed string/rich-HTML values, section and item order, stable IDs, options, keys, explanations, and semantic formatting. Keep deliberate distractors. New recovered content needs evidence, unused IDs, explicit placement, and uncertainty where appropriate; missing content must not be replaced by invented inventory.

Source ruby belongs in the editorial. Project-added ruby belongs in `ruby_<unit>.json`, bound to exact fields/spans and the accepted release. Never fold inferred annotations into source testimony. The compositor checks hashes, overlapping spans, protected tasks, and unchanged underlying text. The [modern](../../pdf-render/schema/editorial.schema.json) and [historical](../../pdf-render/schema/historical-1991-2009/editorial.schema.json) schemas retain separate exam-era rules.

Paths in active documents are repository-relative except the editorial-relative ruby-sidecar path. Frozen `src/`, `preprocess/`, and run paths are provenance identities. Use [unit aliases](../unit_aliases.json) and the resource map to locate packaged successors without rewriting a historical observation.

## Public cases

`unresolved_cases_<unit>.jsonl` contains one current object per stable `case_id`. Update current snapshots while preserving previous decisions in history. The filename is retained even when some rows are resolved. An empty register alone is not a completeness certificate.

| Fields | Contract |
|---|---|
| `case_id`, `unit` | Stable case identity and current canonical unit. Historical prefixes need not match a renamed unit. |
| `item_id`, `field` | Stable item/section ID and relative JSON Pointer, with zero-based array indexes. Unit-level gaps use null item and empty field. |
| `current_value` | Exact typed current value; null for a unit-level gap. |
| `status`, `confidence` | See the status rules below. Confidence concerns reconstructed content, not only source legibility. |
| `decision_basis` | `source_comparison`, `japanese_reasoning`, or `combined`. |
| `context`, `rationale` | Enough context to locate the issue and a concise evidence-based editorial justification. |
| `alternatives` | Nonempty value/assessment array including the strongest competing reading. Null can represent missing content. |
| `evidence` | Nonempty inspected evidence: recognizable source label, locator, reading, and hash or public URL. PDF pages are positive, physical, one-based pages. |
| `resolution_attempts` | Specific checks actually performed. |
| `remaining_uncertainty` | What is unproven and what could settle it; nonempty unless resolved. |
| `before` | Exact pre-edit value for `provisional_fix`; null for newly reconstructed material. |

### Case status and closure authority

- **`provisional_fix` / medium**: A justified correction is applied with meaningful residual doubt. Include exact before/current values and the strongest rival.
- **`unresolved` / medium or low**: Alternatives remain unsettled or required content is missing. Record completed checks and the provisional value or gap.
- **`resolved` / high**: Retain the existing identity with supported resolution, current evidence, and updated wording. Do not delete the row merely because it is resolved.

Ordinary high-confidence corrections need the change ledger and any principal departure, but not a new uncertainty case simply because an edit occurred. Applied, accepted, source-matching, and closed describe different things. Earlier user-designated cases may remain open despite a finished investigation; retain the reason accurately without inventing unreadable print. Historic phase-specific closure decisions remain part of their records. The documentation/ID migration does not resolve any case or reopen a completed run.

## Private ledger and audit notes

The maintained ledger is `private/<level>/<unit>/fixlog_<unit>.jsonl.gz`. The current policy, explicitly selected by the project owner on 2026-11-11, is one compressed JSONL history per unit. Before updating it, preserve the exact compressed file and its hash under `gitignored_docs`. Decompress in memory, preserve the historical payload unchanged, append clearly identified records, recompress to a temporary file, validate it, and replace the maintained file atomically. Do not maintain a separate continuation ledger or rewrite old records to match a newer schema or unit spelling.

New records carry unique edit IDs, the current unit, stable targets/pointers, exact before/after values, confidence, reason, evidence and authorization. Medium-confidence changes identify their public cases. Retrospective entries must say that they were reconstructed from a saved baseline, rather than implying contemporaneous logging. Verify gzip integrity, JSONL parsing, historical-prefix equality and new-ID uniqueness. Refresh package bindings only after these checks. The compressed file hash changes when entries are added; historical evidence hashes remain historical.

The established `editorial_audit_v1` ledger format records granular edits. For newly created items, an empty field with `before: null` and the full item as `after` records creation. Avoid whole-section snapshots that conceal later child edits. The archived `editorial_audit.md` records coverage, unchanged disputes, exclusions, and candidate dispositions; it is not replaced by the edit ledger.

Public evidence should stand alone using source titles, hashes, pages/locators, and concise reasons. Private paths, candidate IDs alone, and internal tool chatter are not adequate public explanations. A hash binds bytes, not authenticity. Source interpretation, full coverage, and linguistic correctness still require review beyond schema and release validation.
