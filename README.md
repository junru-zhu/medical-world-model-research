# Medical World Model Research

This repository contains an anonymous research package for evaluating
free-running ICU chart-process world models across patient-disjoint internal
and external cohorts.

The current manuscript studies passive forecasting of recorded values and
measurement masks. It does not establish treatment effects, counterfactual
validity, clinical benefit, deployment safety, or suitability for clinical
use.

## Current paper

- IEEE-format paper: [`output/pdf/medical-world-model-ieee.pdf`](output/pdf/medical-world-model-ieee.pdf)
- Markdown manuscript: [`manuscript/original-paper.md`](manuscript/original-paper.md)
- IEEE LaTeX source: [`submission/ieee/medical-world-model-ieee.tex`](submission/ieee/medical-world-model-ieee.tex)
- Supplement: [`supplement/original-paper-supplement.md`](supplement/original-paper-supplement.md)

The paper remains an anonymous review version. Author metadata, funding,
competing interests, institutional determination, and the final release record
must be completed before submission.

## Repository structure

- `experiments/` - protocols, model/evaluation code, and aggregate results
- `figures/original/` - editable publication figures, previews, source data,
  and QA reports
- `manuscript/` - review and original-paper manuscripts and bibliographies
- `output/literature-search/` - literature-screening and extraction trail
- `scripts/` - literature, analysis, validation, figure, and PDF build tools
- `submission/` - IEEE source and technical validation records
- `ccfa-review-reports/` - independent review and revision records

## Data and artifact boundary

The study uses the public PhysioNet/Computing in Cardiology Challenge 2019
dataset under its published terms. This Git repository intentionally excludes:

- downloaded patient files and source archives;
- the patient-ID split manifest;
- patient-level derived metric tables;
- prepared patient tensors;
- trained model checkpoints;
- third-party full-text article PDFs;
- local environments, caches, and temporary rendering files.

Aggregate publication tables, data fingerprints, protocols, analysis code,
figure source data, and validation reports remain included. Excluded artifacts
can be regenerated after obtaining the source dataset separately.

## Reproduction

Create the experiment environment:

```bash
python -m venv experiments/.venv
experiments/.venv/bin/python -m pip install -r experiments/requirements.txt
```

Detailed data preparation and experiment commands are documented in
[`experiments/README.md`](experiments/README.md).

Regenerate the publication figures:

```bash
PYTHONPATH=/path/to/nature-figure/scripts \
experiments/.venv/bin/python scripts/build_original_figures.py \
  --analysis-dir experiments/results/frozen-analysis \
  --data-summary experiments/results/neural-data/summary.json \
  --monte-carlo-dir experiments/results/monte-carlo-sensitivity \
  --output-dir figures/original
```

Build the IEEE PDF after installing Pandoc and Tectonic:

```bash
python scripts/build_ieee_pdf.py
```

## Validation status

The current technical package passes the automated methods, results,
reference, figure-layout, rendered-collision, and PDF checks. Human submission
gates remain documented in
[`submission/original-paper-validation.json`](submission/original-paper-validation.json).
