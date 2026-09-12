# MedWM-Eval-ICU Reproduction

The current experiment is a passive clinical-forecasting benchmark on the
PhysioNet/Computing in Cardiology Challenge 2019 v1.0.0 data. It does not make
causal treatment or clinical-deployment claims.

## Frozen Data and Splits

- Dataset DOI: `10.13026/v64v-d857`
- Expected patient files: cohort A 20,336; cohort B 20,000
- Audit: `results/dataset-audit.json`
- Split manifest: `results/split-manifest.csv`
- Split seed: `medwm-eval-icu-v1`

The raw patient files are cached locally and are not part of the release
artifact. The audit records aggregate content fingerprints without
redistributing the source data.

## Commands

Run from the project root:

```bash
python -m venv --system-site-packages experiments/.venv
experiments/.venv/bin/python -m pip install -r experiments/requirements.txt

python experiments/src/audit_dataset.py \
  --data-root experiments/cache/physionet-2019 \
  --output experiments/results/dataset-audit.json

python experiments/src/build_splits.py \
  --data-root experiments/cache/physionet-2019 \
  --output experiments/results/split-manifest.csv

python experiments/src/run_baselines.py \
  --data-root experiments/cache/physionet-2019 \
  --split-manifest experiments/results/split-manifest.csv \
  --output-dir experiments/results/baselines \
  --coverage-threshold 0.05 \
  --hour-cap 72 \
  --min-context 12 \
  --stride 1 \
  --horizons 1,3,6,12,24 \
  --splits internal_test,external_test

python experiments/src/summarize_baselines.py \
  --patient-metrics experiments/results/baselines/patient-metrics.csv \
  --output-dir experiments/results/baselines \
  --bootstrap-replicates 2000 \
  --seed 20260912

PYTHONPATH=experiments/src experiments/.venv/bin/python \
  experiments/src/run_ridge_var.py \
  --data-root experiments/cache/physionet-2019 \
  --split-manifest experiments/results/split-manifest.csv \
  --output-dir experiments/results/ridge-var \
  --lag 3 \
  --tuning-horizon 12 \
  --ridge-lambdas 0.000001,0.0001,0.01,0.1,1.0

python experiments/src/build_sanity_baseline_report.py \
  --baseline-dir experiments/results/baselines \
  --ridge-dir experiments/results/ridge-var \
  --output-dir experiments/results/sanity-baselines

# Publication comparison: common 24-hour-eligible anchors at stride 6.
python experiments/src/run_baselines.py \
  --data-root experiments/cache/physionet-2019 \
  --split-manifest experiments/results/split-manifest.csv \
  --output-dir experiments/results/baselines-common-support \
  --coverage-threshold 0.05 \
  --hour-cap 72 \
  --min-context 12 \
  --stride 6 \
  --common-anchor-maximum-horizon 24 \
  --horizons 1,3,6,12,24 \
  --splits internal_test,external_test

experiments/.venv/bin/python experiments/src/run_ridge_var.py \
  --data-root experiments/cache/physionet-2019 \
  --split-manifest experiments/results/split-manifest.csv \
  --output-dir experiments/results/ridge-var-common-support \
  --model-input experiments/results/ridge-var/ridge-var-model.npz \
  --lag 3 \
  --min-context 12 \
  --stride 6 \
  --common-anchor-maximum-horizon 24 \
  --horizons 1,3,6,12,24 \
  --splits internal_test,external_test

experiments/.venv/bin/python experiments/src/run_neural_matrix.py \
  --data-dir experiments/results/neural-data \
  --result-root experiments/results/neural \
  --models grud,transformer,rssm \
  --seeds 20260912,20260913,20260914,20260915,20260916 \
  --training-batch-size 64 \
  --evaluation-batch-size 128 \
  --device mps

python experiments/src/summarize_neural_matrix.py \
  --result-root experiments/results/neural \
  --output-dir experiments/results/neural-summary \
  --models grud,transformer,rssm \
  --seeds 20260912,20260913,20260914,20260915,20260916

experiments/.venv/bin/python experiments/src/analyze_frozen_results.py \
  --result-root experiments/results/neural \
  --baseline-dir experiments/results/baselines-common-support \
  --ridge-dir experiments/results/ridge-var-common-support \
  --output-dir experiments/results/frozen-analysis \
  --models grud,transformer,rssm \
  --seeds 20260912,20260913,20260914,20260915,20260916 \
  --bootstrap-replicates 2000

experiments/.venv/bin/python experiments/src/run_monte_carlo_sensitivity.py \
  --data-dir experiments/results/neural-data \
  --result-root experiments/results/neural \
  --output-dir experiments/results/monte-carlo-sensitivity \
  --models grud,transformer,rssm \
  --seed 20260912 \
  --trajectory-samples 20,50,100 \
  --patients 1000 \
  --device mps
```

## Evidence Boundary

The deterministic and ridge baselines establish parser, split, metric, horizon,
free-running, and cross-site behavior. They are not sufficient to test the
paper's model-ranking or calibration hypotheses. Those hypotheses require the
prespecified probabilistic sequence baselines and state-space model in
`protocol.md`.
