# Original-Paper Figure Contracts

Backend: Python (Matplotlib), used exclusively for drawing and export.

Export contract: 180 mm maximum width; editable SVG and PDF; 600 dpi TIFF;
minimum rendered glyph size 5 pt; source tables retained beside the analysis;
panel alignment checked at 1.5 pt tolerance; PDF text and collision audits
required after every final render.

## IEEE visual refresh - 2026-09-12

Adaptation level: style-only inheritance. The frozen numerical inputs,
statistics, panel roles, axis limits, and figure conclusions were not changed.
All regenerated source-data CSV files matched the prior files byte for byte.

Visual changes:

- unified colorblind-safe model palette across all quantitative figures;
- neutralized deterministic baselines so neural comparisons carry the intended
  visual emphasis without hiding comparators;
- consistent line widths, marker edges, uncertainty fills, axes, and grids;
- shared figure-level legends in place of panel-local or repetitive legends;
- direct labels for the two coverage reference lines;
- clearer raw-versus-spread-adapted encoding using filled circles and open
  triangles in addition to line style;
- white cell separators and a restrained sequential palette for the constraint
  heat map;
- 300 dpi PNG previews while retaining editable PDF/SVG and 600 dpi TIFF
  production exports.

Final QA: all five figures passed source validation, the 1.5 pt rendered panel
alignment gate, the 5 pt PDF glyph-floor audit, and the rendered collision
audit with zero failures and zero warnings. The rebuilt nine-page IEEE PDF was
also inspected page by page after composition.

## Figure 1 — Evaluation design and claim boundary

Core conclusion: MedWM-Eval-ICU tests passive free-running forecasting on
patient-disjoint internal and external cohorts while keeping development,
external calibration, and frozen external testing separate.

Results-level question: What capability and evidence path does the benchmark
actually test?

Figure archetype: schematic-led composite.

Panel map:

- a — patient-level cohort partitions and permitted information flow.
- b — common-support free-running rollout from a real context through 24 hours.
- c — capability-matched outcome families and the explicit boundary excluding
  treatment-effect, counterfactual, policy, and deployment claims.

Evidence hierarchy:

- hero evidence: the patient-disjoint split and frozen external-test path.
- validation evidence: the common 24-hour anchor and recursive rollout.
- boundary evidence: the outcomes measured and claims not identified.

Reviewer risk: arrows must not imply that external-test outcomes informed
calibration or model selection.

## Figure 2 — Horizon accuracy and transfer

Core conclusion: model conclusions must be evaluated across rollout horizon
and cohort because one-hour ranking alone may not represent long-horizon or
external performance.

Results-level question: How do model accuracy, pairwise differences, and
cross-cohort transfer change as the rollout extends?

Figure archetype: quantitative grid.

Panel map:

- a — hero panel: zero-shot external patient-macro NMAE across 1, 3, 6, 12,
  and 24 hours for all seven model families; neural lines show five-seed mean
  and one seed standard deviation.
- b — frozen 12-hour paired patient-bootstrap NMAE contrasts with 95%
  intervals.
- c — internal-to-external 12-hour NMAE change with independent-cohort 95%
  bootstrap intervals.
- d — Spearman rank-correlation summaries across horizon and cohort; the
  pairwise-reversal fraction remains in the publication table as a complementary
  discrete summary.

Evidence hierarchy:

- hero evidence: full horizon trajectory on frozen external data.
- validation evidence: paired model contrasts.
- boundary evidence: transfer degradation and rank stability.

Reviewer risk: seed standard deviation and patient-bootstrap confidence
intervals answer different uncertainty questions and must not share an
ambiguous legend.

## Figure 3 — Uncertainty adaptation

Core conclusion: post-pilot spread scaling changes the finite-draw empirical
distribution, but must be judged jointly with sharpness and proper scores and
cannot improve the underlying point trajectory.

Results-level question: What changes, and what remains invariant, when
predictive spread is adapted on a separate external cohort?

Figure archetype: quantitative grid.

Panel map:

- a — raw and spread-adapted empirical 5th-95th percentile coverage over
  horizon, with the infinite-draw 0.90 target and the 20-draw exchangeable
  expectation shown separately.
- b — raw and spread-adapted interval width over horizon.
- c — raw and spread-adapted CRPS over horizon.
- d — raw and spread-adapted moment-matched Gaussian negative log score over
  horizon.

Evidence hierarchy:

- hero evidence: finite-draw coverage with explicit reference distinctions.
- validation evidence: width and two proper-score diagnostics.
- integrity check: point NMAE and mask Brier invariance reported in the legend
  and source table, not redrawn as redundant panels.

Reviewer risk: changed coverage caused only by wider intervals must not be
described as improved dynamics or intrinsic model calibration.

## Figure 4 — Observation process and chart-state constraints

Core conclusion: observation-process fidelity and narrow chart-state
constraint consistency are distinct checks on a generated trajectory.

Results-level question: Do models that have similar value error also preserve
measurement behavior and the prespecified chart-state constraints?

Figure archetype: quantitative grid.

Panel map:

- a — external patient-macro measurement-mask Brier score across horizon for
  the three neural families.
- b — rollout-state arterial-pressure-order violations per 1,000 sampled
  states across horizon, with deterministic comparators where available.
- c — 12-hour rollout-state constraint profile for pressure ordering and the
  three bounded-variable checks.

Evidence hierarchy:

- hero evidence: pressure-order violations in the actual carried rollout
  state.
- orthogonal validation: mask Brier and bounded-variable checks.

Reviewer risk: a zero violation rate from a constant or median forecast must
not be interpreted as useful dynamics.

## Extended Data Figure 1 — Monte Carlo-count sensitivity

Core conclusion: empirical coverage, CRPS, and sample-mean error are sensitive
to trajectory count, while the state-space underdispersion and pressure-order
patterns remain qualitatively visible in the tested one-seed subset.

Results-level question: How much do key outcomes change when trajectory count
increases from 20 to 50 and 100 on the fixed 1,000-patient external subset?

Figure archetype: quantitative grid.

Panel map:

- a — 12- and 24-hour coverage by trajectory count.
- b — 12- and 24-hour CRPS by trajectory count.
- c — 12- and 24-hour rollout-state pressure-order violations by trajectory
  count.

Reviewer risk: this is a one-seed, separate-stream sensitivity analysis, not a
convergence study, model-selection result, or estimate of training variability.
