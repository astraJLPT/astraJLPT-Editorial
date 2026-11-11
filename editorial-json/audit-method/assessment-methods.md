# Current browsing index and archived principal assessments

## Current Uncertainty Index

The release’s [uncertainty_index.json](../uncertainty_index.json) has method version 2. Its formula is:

```text
evidence_base
+ 2 × metadata_flags
+ 10 × missing_units
+ 5 × major_defects
+ 2 × minor_defects
+ uncertain_fields
```

Concern points are **uncapped**. Use only the highest applicable content category per field; duplicated records and repeated occurrences of one concern are not separate errors. Evidence bases are:

| Evidence category | Base |
|---|---:|
| `authenticated_edition` | 0 |
| `predominantly_issuer_corroborated` | 100 |
| `user_approved_reference_scan` | 500 |
| `unverified` | 1000 |
| `known_reconstruction` | 2000 |

The issuer-corroboration threshold recorded in this method is 0.9. Sorting uses samples-last, evidence tier, uncapped concern points, descending date, and stable unit ID. It is not simply a numeric sort of the displayed sum. Lower indicates stronger evidence/fewer weighted concerns under the heuristic, not a calibrated probability or a measured count of all mistakes.

Metadata flags concern unresolved identity or structural issues; missing units count absent/unreadable questions or blocks; major/minor defects distinguish substantive content effects from lesser confirmed defects; uncertain fields capture material unresolved disagreements. A deliberately wrong option is not automatically a defect. Neither public difference counts nor open case counts can be substituted directly for these components.

## Archived principal uncertainty index

[`private/principal_uncertainty_index.json.gz`](../private/principal_uncertainty_index.json.gz) is a frozen source-assessment catalogue. Its exam/workbook/sample method versions describe their own selected source/publication. The earlier core arithmetic is:

```text
provenance_points + min(99, 2*metadata_flags + 10*missing_units
                          + 5*major_defects + 2*minor_defects + uncertain_fields)
```

Its provenance bands are 0 for an authenticated source of the relevant kind, 100 for unverified, and 200 for known reconstruction. The workbook extension authenticates the workbook edition, not an exam sitting; the sample extension likewise identifies a sample publication. This differs from the current index’s categories, bases, and uncapped concerns. Do not merge the two scales or reinterpret earlier scores as current ones.

These assessments do not choose a principal or override page-level source authority. A repair to imported JSON adds no principal defect unless the defect was actually present in the principal. A separate key’s error is not automatically an error in the question source. Low scores and exact hashes do not replace source inspection or prove authenticity.
