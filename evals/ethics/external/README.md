# External ethics benchmark data

This directory holds the **Hendrycks et al. ETHICS** dataset used by
[`scripts/eval/run_ethics_external.py`](../../../scripts/eval/run_ethics_external.py)
to measure the evaluator against an externally-published corpus.

## Source

- Paper: Hendrycks, Burns, Basart, Critch, Li, Song, Steinhardt.
  *"Aligning AI With Shared Human Values"*, ICLR 2021 — <https://arxiv.org/abs/2008.02275>
- Code/distribution: <https://github.com/hendrycks/ethics>
- Tarball: <https://people.eecs.berkeley.edu/~hendrycks/ethics.tar>
- License: **MIT** (see the upstream `LICENSE`).

## How to populate

```bash
python scripts/eval/run_ethics_external.py --download
# or, if your network blocks people.eecs.berkeley.edu, manually:
curl -L -o /tmp/ethics.tar https://people.eecs.berkeley.edu/~hendrycks/ethics.tar
tar -xf /tmp/ethics.tar -C evals/ethics/external/ --strip-components=1
```

After extraction the layout should be:

```
evals/ethics/external/
├── commonsense/cm_test.csv
├── justice/justice_test.csv
├── deontology/deontology_test.csv
└── virtue/virtue_test.csv
```

## What ships in this repo

To keep the script and CI test runnable **without internet access**, a
small **smoke fixture** is bundled in each subset directory
(`smoke_sample.csv`). These are not the upstream test files. They are a
handful of paper-derived examples used purely to exercise the loader and
the mapping rules end-to-end. Do not interpret accuracy on the smoke
fixture as a benchmark result.

The real number — the one that decides what the next sprint should
work on — is produced by running the script on the full upstream
`*_test.csv` files and freezing the result with
`--freeze-baseline`.
