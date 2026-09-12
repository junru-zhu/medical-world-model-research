# Frozen Analysis Specification

Freeze date: 2026-09-12  
Status: fixed after the implementation-seed audit and before completion of the
remaining seed matrix

## Interpretation target

The primary estimand is performance averaged over the five fixed trained model
instances with seeds 20260912 through 20260916. It is not an estimate of the
expectation over all possible training runs. Across-seed standard deviation and
range describe computational variation. Patient resampling quantifies
uncertainty for the patient population represented by each test cohort.

Seed 20260912 was inspected during implementation. The primary tables retain it
after regeneration under the final pipeline; every neural summary is repeated
without that seed as a post-pilot sensitivity analysis.

## Weighting and metric order

For value metrics, errors are first summed across eligible anchors and observed
variables within a patient and divided by that patient's observed-target count.
The split-level metric is the unweighted mean across patients, so each patient
has equal weight. Variables are robustly scaled by the cohort-A training IQR
before aggregation.

For measurement masks, Brier losses are averaged across anchors and variables
within patient and then equally across patients. Interval coverage, width,
CRPS, and Gaussian NLL follow the same patient-first aggregation.

Neural patient metrics are averaged across the five fixed seeds after alignment
by patient identifier. Deterministic models contribute one value per patient.
Patient-bootstrap intervals resample patients, not anchors or observed targets.

Physiological-constraint rates are pooled over sampled trajectory states within
a run and reported per 1,000 sampled states. They are summarized across seeds
with mean, standard deviation, and range. The current artifacts do not support
patient-bootstrap intervals for constraint rates, so no patient-population
inferential claim is made for them.

## Derived estimands

Let \(M_h\) be a patient-macro split metric at horizon \(h\), with
\(H=(1,3,6,12,24)\). The normalized rollout-area estimand is

\[
A(M)=\frac{1}{23}\sum_{j=1}^{4}
\frac{M_{H_j}+M_{H_{j+1}}}{2}(H_{j+1}-H_j).
\]

For internal metric \(M_A\) and zero-shot external metric \(M_B\):

\[
\Delta_{\mathrm{external}} = M_B-M_A,\qquad
R_{\mathrm{external}} = 100\frac{M_B-M_A}{M_A}.
\]

Cross-cohort intervals independently resample patients within the internal and
external cohorts because the cohorts contain different patients.

The primary physiological outcome is arterial-pressure ordering in the actual
rollout state after sampled-mask application and carry-forward. Bounded
O2Sat, SaO2, and FiO2 rates and all decoder-emission violations are separate
outcomes and are not combined into one omnibus count.

## Research-question map

| Question | Population and models | Metric and horizons | Estimand and uncertainty | Status |
| --- | --- | --- | --- | --- |
| Does one-hour ranking represent long-horizon ranking? | Internal and zero-shot external test; all seven models | Patient-macro NMAE at 1, 12, and 24 h | Spearman rank correlation and fraction of model pairs whose order reverses; distribution across five seeds | Protocol defined; descriptive |
| Do probabilistic and physiological conclusions change with horizon? | Both test cohorts; three neural models | Coverage error, CRPS, NLL, width, pressure ordering, bounded-variable violations at 1, 3, 6, 12, 24 h | Horizon profile, normalized area where applicable, seed variation; no formal monotonic-trend test | Protocol defined; estimation focused |
| How does zero-shot external performance differ from internal performance? | Internal cohort A and frozen external cohort B; all models where applicable | NMAE at 12 h, with secondary metrics | Absolute and relative degradation; independent-cohort patient bootstrap for NMAE; cross-site rank correlation and reversal fraction | Protocol defined |
| Does observation-mask evaluation change model interpretation? | Both test cohorts; neural models | Patient-macro mask Brier at all horizons | Horizon profile and seed variation; exploratory pairwise interpretation, without confirmatory p-values | Protocol defined |
| Is the recurrent state-space model necessarily better calibrated? | Three neural families | Raw coverage error, CRPS, NLL, and width | Descriptive model-family comparison with seed variation | Post-pilot exploratory |

## Frozen 12-hour NMAE contrasts

The following model-A minus model-B differences are reported on internal and
external test cohorts:

1. GRU-D-style model minus Transformer;
2. GRU-D-style model minus ridge VAR;
3. Transformer minus ridge VAR;
4. recurrent state-space model minus ridge VAR; and
5. ridge VAR minus last observation carried forward.

For each patient, neural predictions are averaged over the fixed five seeds.
The 95% percentile interval resamples aligned patients. Negative values favor
model A. No retrospectively specified p-values are reported.

## Recalibration analysis

The initial protocol anticipated a separate cohort-B recalibration partition.
The exact horizon-wise pooled scalar-spread procedure was fixed after the first
implementation seed and before the remaining seeds; it is a post-pilot
adaptation analysis.

The multiplier is fitted across observed targets, so its fitting objective is
target weighted, whereas reported test metrics are patient macro. This
weighting difference is disclosed. The procedure adjusts only marginal spread
at each horizon and does not establish variable-specific, patient-conditional,
joint, or measurement-mask calibration.

Raw and recalibrated external evaluations use identical split-specific Monte
Carlo streams. The frozen analyzer must verify that patient NMAE and mask Brier
are invariant within numerical tolerance. Coverage, interval width, CRPS, and
NLL are reported together.

## Monte Carlo sensitivity

The main evaluation uses 20 trajectories per anchor. Before final manuscript
freeze, a deterministic subset analysis will compare 20, 50, and 100
trajectories for stability of coverage, CRPS, NLL, and constraint rates. This
analysis is a numerical-convergence check, not a model-selection experiment.

## Claim boundary

All analyses concern passive forecasting. They do not identify treatment
effects, counterfactual outcomes, policies, clinical benefit, or deployment
safety.
