# What survived the ruby research

The investigation separated two questions: **where would reading help be useful or resemble observed JLPT practice, and is this particular reading attached to the right text?** A strong placement score cannot answer the second question on its own. The final process combines ranking, section-level coverage targets, protected tasks, and contextual review.

**Retained:** core character/span/task features, era and original-level distinctions, the third-party modern JLPT kanji grid, features describing earlier *source* glosses, observed-print analogies, section/paper covered-kanji caps, and explicit reading/span/task review. Vocabulary, grammar, and reading are not treated as one undifferentiated pool.

**Rejected:** a universal rule that the second occurrence should lose ruby; blanket special treatment or a reserved allowance for （注） notes; broad frequency features whose apparent ranking gain did not consistently improve selections at matched budgets; and the strict early score thresholds as the final expansion policy. No fixed score floor was used for the final ranked expansion, but guards and contextual rejection still applied.

**Limited role:** exact lexical frequency breaks ties between identical stored scores. Note roles remain diagnostics rather than a multiplier. School grades, Jōyō membership, dictionaries, historical lists, and media frequencies supplied candidate features, checks, or sensitivity studies; their availability did not mean they all entered the final scorer. A dictionary reading is not proof of the reading of a particular person’s name, and a missing annotation in a retype is not a negative printing label.

## Earlier passes and their limits

| Stage | What changed | What the result did and did not show |
|---|---|---|
| First pass, 9 October 2026 | Added 6,295 groups across 79 selected modern units, preserving existing ruby. Sixteen recent approved papers supplied labels; mixed-scope N2 July 2018 was excluded from that first calibration. | Reported 91.0% exact presence/span/reading precision and 63.3% recovery recall on the December 2025 N1–N5 content panel. This was the first pass’s evaluation, with development/exposure limits; it is not the final release’s accuracy. |
| Pass 2, 5 November | Compared 39 regularized model variants, using lineage-aware splits, broader era evidence, and contextual guards. The selected release had 668 groups. | The modern JLPT grid was the strongest tested added family in that comparison. A separate scorer panel gave 30/33 jointly correct and 30/76 recall, but the actual deployment policy added zero in those windows. Those figures therefore do not estimate the accuracy of the 668 deployed groups on retypes. |
| Pass 3, 5 November | Retained the core/era/JLPT model and added earlier verified source-gloss context. Added 53 groups, reaching 721. | Development average precision rose from about .786 to .816. Combining more feature families reached about .821 but produced worse harmful-addition behavior. Strict marginal gates supplied only 76 additional covered kanji, about 0.30% of the modelled positive shortfall. Precision-oriented gates left most estimated reading-help gaps unfilled. |
| Context review, 5 November | Removed two unsupported personal-name readings of 林, leaving 719 starting groups. | A dictionary/name tag did not settle those occurrences. The later policy keeps exact controls for the retired spans, independent of tokenizer tags. |
| Pass 4, 6 November onward | Ranked eligible spans under section and paper allowances, reviewed full context, rejected unsuitable candidates, and refilled in score order. | Reproduces 12,815 new selections plus the 719 starting groups: 13,534 groups. The same agent performed initial and final rereads; these were additional checks, not independent blind validation. |
| Presentation follow-up | Two accepted groups were added in the later presentation repair. | The present installed sidecars contain 13,536 groups. Frozen pass-4 counts remain unchanged in their own records. |

Historical source-class counts also belong to their passes. Pass 4’s roster described 123 Restored, 68 Base, five Workbook, and five Sample units; subsequent publication corrections changed the current workbook classification. Do not copy those old counts into a description of today’s categories.

## Why the final choices survived

### JLPT grids and other difficulty predictors

Removing the modern JLPT grid by refitting the same model reduced reused-development average precision from **0.816414 to 0.664659**. At comparable coverage budgets, the investigation examined 96 disagreement targets in full context. The grid favored more useful lexical targets in those judgments, so it was retained. This did not establish the grid’s original classification method or exclude possible past-exam influence; it remains a third-party study resource, not an issuer syllabus.

Period school grades and frequency families sometimes improved individual development comparisons. That was insufficient to adopt every family. The frozen presence model keeps only `core`, `era`, `modern_jlpt`, and `priorgloss`, with fixed numeric projections for replay. Candidate reading resources and allowance estimation are separate parts of the pipeline.

### Repetition and prior glosses

The user’s “later occurrence gets less ruby” hypothesis was tested in context. Observed print included both omission after a prior gloss and repeated ruby on the same word. The retained feature distinguishes earlier source glosses by word/reading, position, distance, passage/question relationship, and known original-page context. It is not a universal second-occurrence penalty, and newly added ruby does not masquerade as prior source exposure.

### Notes and frequency

Adding note roles alone barely changed development average precision: **0.816414 → 0.817498**. More elaborate combinations did not establish a useful independent note bonus at matched budgets. Note headwords and explanations remain identifiable for analysis and context, without a blanket multiplier or reserved quota.

The first exact-frequency lookup confused inflected surfaces with dictionary lemmas. The repaired lookup uses checked kana-suffix reconstruction and exact lemma/reading matches; irregular or unavailable matches remain unknown. The adopted policy changes **56 rows, or 28 choices**, only within identical ten-decimal scores: known matches first, rarer matched entries first, then stable identity keys. It does not create “near-tie” buckets or override a higher score.

A broader corrected-frequency model reached **0.830924** development average precision, but observed-print hits at matched budgets did not improve consistently. It was rejected as a general ranking family. Frequency retains the narrower tie-breaking role.

### Protected tasks and remaining gaps

Uncertainty masks were narrowed only where the documented dispute could not affect the proposed reading. Exact disputed spans, protected reading/orthography targets, intentional alternatives, original ruby, overlap rules, name controls, and whole-span limits remained guarded. An implementation follow-up excluded leading administrative `問` plus a question number while keeping ordinary prose uses eligible.

The final R8 follow-up reviewed 646 additional passage proposals and 90 item proposals, correcting specific bad readings through new candidate identities and score reconciliation. It did not change the ranking scores or transfer unused allowance between sections. The final recorded shortfall was **2,935 covered-kanji allowance units across 170 sections**. That means no remaining nonrejected whole candidate in the frozen pool fit the applicable caps; it does not mean every possible Japanese expression was enumerated.

## Reading the evidence correctly

Printed presence, correct reading, correct attachment, task safety, and usefulness are different outcomes. The final pass does not claim exact original printing for restored occurrences or a calibrated probability of printing. Its small later print checks used fresh windows within previously used source lineages; they were not a new independent blind evaluation of all installed annotations. Earlier accuracy figures belong to their particular passes.

The packaged [replay](README.md#replaying-the-frozen-release) verifies arithmetic and frozen selection decisions. It does not rerun the linguistic judgments or recreate the full training study. [Research provenance](datasets/research-provenance.json) identifies the original reports used for this summary. Selected final research, allocation, selection, and coverage artifacts remain under [the pass-4 run](runs/ruby4-20261106/); the [manifest](datasets/manifest.json) pins packaged bytes, and [SOURCES.md](SOURCES.md) identifies upstream datasets.
