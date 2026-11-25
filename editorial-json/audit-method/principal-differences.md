# Principal differences — adapted contract

`principal_differences_<unit>.jsonl` describes the **current editorial versus its principal**, including inherited departures. It is not merely a list of edits to imported JSON. Current unit IDs use [the alias map](../unit_aliases.json); existing `difference_id` and linked case IDs remain stable.

Compare wording, numbers, option order and boundaries, missing printed content, ruby, underlines, punctuation, and other meaningful formatting. Harmless reflow and decorative furniture are excluded, as are clearly separate editorial explanations and metadata. An unprinted answer key is separately supplied information, not automatically a disagreement with a question page.

Inspect the literal affected source span with enough context to locate it. OCR is a lead, not a quotation of visible print. If the source cannot be read, use `reading_status: "unreadable"` and `reading: null`. Use `absent` only after verifying the relevant coverage. High comparison confidence does not by itself imply high historical confidence in the reconstruction.

## Record format

Keep one current JSON object per `difference_id`; preserve superseded observations privately.

| Field | Contract |
|---|---|
| `format` | `principal_difference_v1`. |
| `difference_id`, `unit` | Stable record ID and current unit. |
| `item_id`, `field`, `current_value` | Stable target, relative JSON Pointer, exact typed current snapshot. Entirely missing content can use null item/value and empty field. |
| `categories` | One or more of `wording`, `numbers`, `option_order`, `boundaries`, `missing_printed_content`, `ruby`, `underline`, `punctuation`, `unreadable_source`. |
| `principal` | Recognizable `source_label`, exact `sha256`, `physical_pages`, precise `locator`, `reading_status` (`legible`, `absent`, `unreadable`), and literal `reading`. |
| `editorial_reading` | Concise affected editorial span, retaining minimal meaningful markup; null for entirely missing content. |
| `comparison_confidence` | `high`, `medium`, or `low` for the observed comparison. Unreadable comparisons cannot be high. |
| `disposition` | `retained_variant`, `supported_repair`, `conjectural_repair`, `editorial_omission`, or `unreadable_source`. |
| `rationale` | Why the current departure is retained, including limits and inherited choices. |
| `linked_case_ids` | Same-unit stable public cases, or an empty array. Material provisional departures need a matching uncertainty record. |

PDF page numbers are one-based physical pages within the actual reviewed member. A source-set manifest hash is not question-page testimony: cite the particular PDF member and its pages. A separately supplied key does not become the question principal. For other formats, use an empty page list and a precise native locator.

## Literal comparison and retirement

A confident repair still needs a difference row when it departs from the principal. Conversely, a verified source-matching field is not a current difference. Retire a stale or false comparison, preserve its history, and update related case prose. Source agreement alone does not resolve the case or authenticate the source.

Reconcile the whole current register with final JSON, rather than checking only newly edited fields. Maintain unique IDs, current values, exact principal hashes, valid locators, and stable case links. An empty register means “reviewed with none found” only when the audit establishes coverage and exact input bindings. It is never an equality or authenticity certificate.

Historical non-principal workbook comparisons used `reference_difference_v1` and `reference_source_manifest_v1` companions. Those describe an explicit aligned scope, with exact member hashes, pages, editorial revision, and comparison IDs. They cannot imply agreement outside that scope. Where such companions are only mentioned in archived records, they are historical references, not additional runnable dependencies in this package.
