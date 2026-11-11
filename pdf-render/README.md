# Regenerating the accepted written editions

The authoritative inputs are in [editorial-json](../editorial-json/README.md). Each unit has one `editorial_<unit>.json` and its installed final `ruby_<unit>.json`. There is no second `preprocess/` copy. Current workbook IDs identify their publication year; expanded practice sets have explicit set IDs. [The versioned alias map](../editorial-json/unit_aliases.json) connects ten historical sitting-like IDs to these current identities.

All 201 release editorials use schema `4.1.0`, with separate modern and historical validation/presentation policies. The release omits legacy root `sources`, HTML import line numbers, unused question weights/categories, listening documents, redundant survey/review pointers, inspection receipts and repeated descriptive metadata. Answer explanations, exact question content, source ruby, final restoration sidecars, effective layouts, defaults and validated source/page facts remain. The local workspace's `preprocess` editorials are not migrated.

Active defaults and asset paths are relative to the repository root, such as `pdf-render/schema/N1/defaults.json` and `editorial-json/assets/...`. The ruby sidecar path remains relative to its editorial. `src/...` identifies the external source tree and can be retained when that tree is hosted separately; generating these editions uses the packaged rendering resources. `source-set:UNIT` is an explicitly reference-only identity for a frozen workbook source-set manifest, not a filesystem path. Its original hash and member identities remain in the accepted contract. Frozen research/audit records can retain original logical paths; the resource map supports those records without requiring a local `preprocess` directory.

STAR solutions are stored on scored questions in the editorial JSON; see [the STAR contract](../editorial-json/STAR.md). The web adapter reads those canonical records directly. The printed payload excludes solution metadata, so aggregate question-group/section typography bindings remain unchanged. STAR evidence separately binds the authored question ID, stem, ordered options and key, excluding the solution record itself and display-only ruby restoration.

Existing browser answer tokens remain in the installed HTML shells and are reused only after checking both the answer-token list hash and the accepted semantic question digest for that rendition. This preserves saved answers through metadata-only migration without storing a second question-token map. Later question or token changes require explicit review and refreshed reader bindings; harmless shell reserialization does not invalidate the tokens. The accepted contract's ruby release ID is unchanged because annotation contents and decisions are unchanged; `editorial_schema_version` separately identifies the v4 storage contract.

Use Python 3.14 and LuaLaTeX (LuaHBTeX 1.24.0 / TeX Live 2026 for the recorded comparison). Install the pinned Python dependencies in an environment outside versioned files:

```sh
python -m venv .venv
# Activate .venv using the command for your shell, then:
python -m pip install -r pdf-render/requirements.txt
python pdf-render/render.py --unit N4_workbook_2018 --variant both
```

Install a full TeX Live distribution with LuaTeX-ja, fontspec, lua-ul, tabularray, mdframed, tikz, TeX Gyre and the standard LaTeX packages. Add `lualatex` to PATH. Alternatively, set `ASTRAJLPT_LUALATEX` to your own executable path. The code discovers the checkout from `__file__` and sets its TeX resource root in the child process; no drive, username or working directory is assumed. Full pinned fonts are unpacked under `fonts/`, deduplicated by SHA-256. Their bytes and roles are unchanged. `fonts/manifest.json` records the exact files; inclusion does not establish new redistribution permissions.

```sh
python pdf-render/render.py --all --variant both --no-compile
python pdf-render/render.py --all --variant both
```

The first command validates composition and native TeX emission for all 201 paired owners. The second compiles them. Regular PDFs go to `output/`; no-rubi PDFs go to `outputnorubi/`. Both directories, intermediate TeX, font caches and diagnostics are ignored. The published accepted PDFs remain under `../astraJLPT/assets/pdfs/` and `../astraJLPT/assets/pdfs-norubi/`; rendering does not replace them automatically. Listening is outside this package's rendering scope.

`contracts/accepted-release.json` replaces the historical runtime dependence on handoff directories and parent release snapshots. It records the fully validated current roster, editorial and sidecar hashes, accepted annotation digests, public identities, exact source/page facts and typography digest transitions. The compositor still checks field hashes, task protection, overlaps, IDs, source ruby, layouts and image exceptions. The contract does not grant approval to new source material. Altered authoritative inputs require explicit review and a new contract; do not silence a failed hash check.

`contracts/source-references.json` distinguishes locally available principals from validation-only historical evidence. Some alternate scans and superseded research witnesses are not included. Their frozen hashes and accepted facts remain explicit. Actual rendering resources are local and hash-checked; a reference-only record is never opened as a substitute file. `contracts/resource-map.json` resolves old logical provenance IDs such as `preprocess/...` into the current package layout. It contains no workstation path. Active historical artwork has been retained under deliberate resource bindings rather than deleted because of its former directory name.

HTML is delivered as the verified static site. Its maintained shells, shared CSS, illustrations and font subsets are preserved. Native body projection code and source CSS/JavaScript are included in `web-tools/` and `web-src/`. To verify or refresh reader bodies against those existing shells:

```sh
python pdf-render/web-tools/rebuild.py --unit N4_workbook_2018
python pdf-render/web-tools/rebuild.py --unit N4_workbook_2018 --write
```

Omitting `--unit` checks all owners. `--write` preserves the page shells and memory settings and reuses shared CSS. It checks text and stable IDs before replacing a body. This is a maintenance workflow for the packaged site, not a replay of the old release assembly scripts.

The packaging verification record is in `contracts/package-validation.json`. At the earlier schema-v4 migration, comparison with the saved v3 baseline covered all 201 units: 402 native bodies, all authored covers, 402 HTML bodies, navigation, answer tokens, and rendering assets. Ten regenerated PDFs covered modern restored, workbook 2012, workbook 2018, early historical, and reconstructed historical-cover cases, both editions. All 266 sampled pages preserved extracted text, dimensions, and exact 96 dpi RGB pixels. Six regenerated PDFs were byte-identical; the workbook files had equivalent content with different PDF object serialization after font deduplication. That migration left the installed PDFs and website bytes unchanged.

## Publication ID migration

The later ID migration preserves all 402 installed PDF byte streams and the content of all 402 reader bodies. It compares native body and cover TeX for both renditions of the ten renamed units. Active editorial/sidecar paths, schemas, layout owner bindings, collection metadata, and accepted contracts use the new IDs. Eight workbook PDF filenames retain their already-correct publication names, such as `N4_2018.workbook.pdf`; the two expanded-set PDF filenames use their new set IDs. No printed content is relabelled by this migration.

The supported renderer and HTML-check commands accept either current IDs or the ten legacy aliases. Era dispatch and historical applicability checks resolve the original identity where needed to preserve accepted rendering. Frozen source manifests, source observations, research decisions, historical audit entries, annotation IDs, and public case/difference IDs remain historical. New fixlog entries are merged into each maintained compressed ledger under the editorial record contract. The intermediate body PDF’s legacy identifier metadata is preserved; the accepted final PDF title still comes from its public-output contract.

Reader URLs use current unit IDs. Earlier reader and review URLs redirect while retaining query strings and fragments. The page-data `storage_unit` preserves the old browser key for renamed readers, and existing answer tokens are unchanged. The shared application uses that key before falling back to `paper.unit`. This preserves local progress on the same browser/origin; it does not transfer storage between origins.
