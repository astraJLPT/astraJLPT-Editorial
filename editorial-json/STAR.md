# STAR answer records

Schema 4.1.0 stores the full solution on each scored `sentence_composition`
question as a `star` object. The website consumes this object directly; there is
no separately maintained order inventory. The [record schema](../pdf-render/schema/star-answer.schema.json)
is referenced by both modern and historical editorial schemas.

| Field | Meaning |
| --- | --- |
| `status` | `verified` for agreeing independent reviews and source placement; `accepted` for an explicit editorial disposition; `held` while a decision is pending. The linked public case records whether an accepted issue remains open or is resolved. |
| `order` | The four option numbers in sentence order, each of 1–4 exactly once. Held records use `null`. |
| `star_position` | The actual position of the star among the four blanks, numbered 1–4. It must match the current stem. |
| `question_sha256` | SHA-256 of the authored `id`, `stem`, `options` and `key`, serialized as UTF-8 JSON with sorted keys, compact separators and unescaped Unicode. The `star` object is excluded. |
| `order_evidence` | Linguistic review and any supporting explanation or prior accepted review, with concise reasoning and review-record hashes. |
| `position_evidence` | Separately observed source placement: source identity/hash, one-based physical PDF page and/or a `locator`, observed position, inspection method and limits. Image evidence may also retain its `source_url`. |
| `hold_reason` | Required only for held records. Explains the unresolved conflict without publishing a speculative solution. |
| `decision` | Required only for accepted records. Binds the authority, date, question, order, position, key, rationale, residual uncertainty and linked public cases. |

A verified record needs two distinct independent linguistic reviewers and at
least one inspected position witness. Initial judgments precede access to
inherited keys, explanations and other reviewers' results. Later reconciliation
is recorded separately. Agreement between models does not authenticate a source,
and agreement with a key does not prove the location of a star. Source evidence
must state relevant retype, lineage or historical limitations.

Each `independent_linguistic_review` entry uses the following fields. The
`source_explanation` and `existing_review` methods may supply supporting evidence,
but do not count as independent reviewers.

| Review field | Meaning |
| --- | --- |
| `method` | `independent_linguistic_review`. |
| `reviewer` | Required stable reviewer identity. Multiple entries from the same identity count as one reviewer. |
| `basis` | Required reasoning for this judgment. |
| `reviewed_order` | Required permutation of 1–4 recording the reviewer's actual judgment, including a contrary initial judgment. |
| `reviewed_question_sha256` | Required hash produced by `question_binding(question)` from the authored question. It must match the current question, or the validated original snapshot allowed for an accepted record below. |
| `stage` | Optional `initial` or `post_review`; omission means `initial`. A later judgment is appended as `post_review`, preserving the initial entry. |
| `review_binding_sha256` | Required hash produced by `review_binding(evidence)` over the judgment fields described below. |
| `record_sha256` | Optional link to an immutable raw review record. This separate hash does not establish agreement with the published order. |
| `source_path`, `source_sha256`, `physical_page` | Optional supporting source reference. These fields do not enter the review binding. |

`pdf-render/tools/star_answers.py` exposes both hash functions. `review_binding`
hashes an object containing exactly `method`, `reviewer`, `basis`,
`reviewed_order`, `reviewed_question_sha256`, and `stage`, normalizing an omitted
stage to `initial`. It uses SHA-256 over UTF-8 JSON with `ensure_ascii=False`,
`sort_keys=True`, and `separators=(',', ':')`, as `question_binding` does. It
excludes `review_binding_sha256` itself, `record_sha256`, and source references.

For example, after a reviewer has supplied an order and rationale:

```python
from star_answers import question_binding, review_binding

evidence = {
    'method': 'independent_linguistic_review',
    'reviewer': reviewer_id,
    'basis': rationale,
    'reviewed_order': reviewed_order,
    'reviewed_question_sha256': question_binding(question),
    'stage': 'initial',
}
evidence['review_binding_sha256'] = review_binding(evidence)
```

Every independent review must retain a valid content and review binding, even
when the question is held or the judgment has been superseded. For each reviewer,
validation uses all `post_review` entries if any exist; otherwise it uses all
initial entries. A verified record requires at least two reviewer identities,
and every effective judgment must endorse the published `order`. Conflicting
entries at the same effective stage cannot be resolved by their list order.
Held records allow contrary judgments without requiring agreement.

An `accepted` record also retains at least two independent reviewer identities,
but does not claim that their effective judgments unanimously endorse the chosen
answer. Its `decision.authority` is `user` or `delegated_source_adjudication`.
The decision repeats the exact `question_sha256`, `order`, `star_position` and
`key`; validation requires agreement with the current question and solution.
It also records `date`, `rationale`, `remaining_uncertainty`, and `case_ids`.
For a resolved intended answer, `remaining_uncertainty` states that none remains;
the linked public case uses `resolved` / `high`. This does not relabel earlier
independent judgments or imply that those judgments unanimously agreed.
`decision_sha256` hashes the entire decision except that hash field itself,
using the same canonical JSON encoding as `question_binding`. The helper is
`decision_binding(decision)`. User-reported consultation is `user_report`
evidence; an inspected online discussion is `public_discussion` with its URL.
Neither is relabelled as a new independent blind review.

When an accepted key or slot correction changes the question hash, a prior
independent judgment may carry its exact `reviewed_question` snapshot containing
`id`, `stem`, ordered `options` and `key`. Its original review hash is retained.
Validation recomputes the snapshot's question hash and requires the same item,
surrounding sentence text and option text as the current question, allowing only
grading/slot differences. A changed linguistic question requires fresh evidence;
an old snapshot cannot authorize changed fragments or context. The snapshot is
validated separately and does not alter the original review-binding hash.

Each position witness requires `source_path`, `source_sha256`,
`observed_position`, `method`, and `basis`, plus at least one of `physical_page`
or `locator`. Both may be supplied, such as page 4 and a locator identifying the
upper question row. Every supplied page or locator must independently satisfy
its field constraints. `physical_page` is a one-based integer; `locator` is a
nonempty string. Accepted methods are `visual_page_review`,
`visual_image_review`, `pdf_geometry_review`, and `web_text_review`. A web witness
names its URL and a precise locator, and identifies exactly which captured bytes
its hash describes. `position_scope` defaults to `question_blank`; explicit
`worked_constituent` observations describe a worked solution and do not establish
an original empty-slot layout.

For a verified record, `order[star_position - 1]` must equal the existing question
key. Held records preserve the current question and key, with no full-order
reveal. A held source observation may disagree with the current position; that
disagreement remains visible in its evidence rather than being silently repaired.
Accepted records may retain contrary placement witnesses under the explicit
decision, but still require question-layout evidence and exact order/key/stem
consistency. Their full order is published using the existing reveal interaction;
the linked public case records the current resolution or any remaining linguistic
or historical issue.

The native printed payload excludes `star` metadata. Optional ruby restoration
is applied to that printed payload, while solution hashes continue to bind the
authored fields. This keeps printed question content, typography bindings and
existing saved-answer tokens independent of solution provenance updates.

Run `python -B pdf-render/validate_editorials.py` to validate all release schemas,
STAR records and accepted input bindings. Runtime composition also validates
STAR coverage and semantic invariants before rendering. Tests under
`pdf-render/tests` cover positions 1–4, stale content, malformed solutions,
independent-review requirements, display ruby and held-question behavior.
Run the focused suite with
`python -B -m unittest discover -s pdf-render/tests -p 'test_*star*.py' -v`.
