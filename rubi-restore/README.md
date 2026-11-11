# Rubi-restore

Rubi-restore was developed using ruby observed in approved scans, workbooks, and samples. It estimates a target amount of ruby for each section, ranks possible annotations, and adds suitable readings after checking their context. Existing ruby counts toward those targets, and some sections remain below target when suitable additions run out.

I gave the agent a collection of datasets—JLPT kanji grids, school levels, Jōyō kanji, Jiten frequency lists, BCCWJ frequency lists, and more—and asked it to investigate what correlated with the observed ruby, with minimal steering. I also suggested hypotheses: separating vocabulary, grammar, and reading; treating （注） notes differently; and expecting less ruby on later occurrences of the same word. The research tested those ideas rather than assuming they were all true.

I don’t claim the restored ruby matches the actual JLPT 100%. The aim is to provide roughly comparable reading help and bring the difficulty closer to the original. That is a practical aim, not a measured claim of equal difficulty. No-rubi PDFs and HTML are also available.

The [research history](RESEARCH.md) explains what survived and what failed. In brief:

- **Retained:** the observed-print ranking model, section and paper coverage allowances, context-sensitive source-gloss features, protected-task checks, and occurrence-by-occurrence reading review.
- **Rejected:** a universal second-occurrence penalty, a blanket note bonus/reserve, broad frequency additions without consistent selection benefit, and the earlier strict score gates as the final expansion policy.
- **Limited role:** frequency breaks exact score ties; notes remain useful diagnostics; school and dictionary resources inform research and candidate interpretation without becoming universal JLPT rules.

See [SOURCES.md](SOURCES.md) for considered, tested, retained, and packaged resources, with upstream downloads. Early accuracy figures belong to their particular research passes, not the final release as a whole.

## Replaying the frozen release

The delivered annotations are the final `ruby_<unit>.json` files in [editorial-json](../editorial-json/README.md); this directory does not contain a second installed copy. This package preserves the frozen scorer, adopted policy code, final decisions, exact replay inputs, and selected research datasets, without the superseded experiment trees.

Install the renderer requirements plus the research requirements, then run:

```sh
python -m pip install -r rubi-restore/requirements.txt
python rubi-restore/replay.py
```

The replay checks the frozen data hashes, reproduces all 321,988 candidate scores across 201 owners, reruns the allowance and contextual selection, and validates the installed final sidecars. It reproduces 12,815 new selections plus 719 retained starting annotations (13,534 groups). The later accepted presentation repair adds two groups, giving 13,536 installed final annotations. Typography changes do not change the accepted readings.

Ranking uses the frozen feature order, centered/scaled inputs clipped to [-8, 8], and a logistic score `sigmoid(intercept + X · coefficients)`. The feature projection preserves the exact numeric inputs and their binding to each ranked row. Print analogy adjusts the score by `0.04 × (positive_lineages − negative_lineages) / (2 + positive_lineages + negative_lineages)`, clipped to [0, 1] and rounded to ten decimal places. These are ranking scores, not calibrated probabilities that a reading was printed at a particular occurrence.

Candidates are considered by descending score. Frequency is only an exact-score tie-break: matched corpus counts sort before unavailable counts, with lower matched counts first; stable owner/pointer/span/reading keys settle remaining ties. This does not override score order.

Allowances count covered kanji, not annotation groups. The adopted allocation uses half-up rounding of the total covered-kanji target, subtracts existing union coverage and reconciles positive section deficits proportionally by largest remainder, with section-ID ties. Selection skips overlapping candidates and whole spans that exceed either section or paper allowance. Rejections do not transfer allowance between sections.

Contextual review checks reading, attachment and task safety. The final ledger retains both the initial judgment and a separate final reread, reasons and exact field/span bindings. It does not claim independent human evaluation. Rejected readings are not silently edited: corrections have new identities and explicit score/replay reconciliation. The replay uses those frozen judgments; it does not generate new judgments or grant permission to alter current annotations.

`datasets/manifest.json` lists every included research payload and its checksums. `datasets/features/` contains the compact lossless scoring inputs in the exact ranked-file order. Frozen ranked queues, policy versions, allocations, corrections, final context ledger, decisions and coverage records remain under their research run IDs. Large final records use deterministic gzip; `replay.py` reads them directly. Old path strings inside those records are provenance identifiers, not dependencies on another workstation. Historical acquisition and full training experiments are not the regeneration entry point; the supported offline entry point is `replay.py`.

## Identity and output contracts

The frozen model’s retained families are `core`, `era`, `modern_jlpt`, and `priorgloss`. Its 58 numeric input columns and coefficients are preserved, not refitted during replay. The candidate scorer predicts placement rank; dictionary matching and contextual review address whether a proposed reading and span make sense. Neither stage proves what was printed at an unrecovered occurrence.

Historical queues and ledgers retain the old sitting-like IDs. Join them to current workbook/set IDs through [unit_aliases.json](../editorial-json/unit_aliases.json). The installed sidecars use current `unit_id` values while preserving every annotation ID, reading, span, and evidence record. Replay validates the frozen decisions and then the current installed sidecars against the accepted release contract.

Source ruby remains in the editorial and inferred ruby in the sidecar. No-rubi renditions strip textual ruby through the shared rendition layer. The explicitly accepted original-image exceptions remain documented in [the raster policy](../pdf-render/config/norubi-raster-assets.json); some images retain their original printed ruby. This does not alter the regular edition’s source or inferred annotations.
