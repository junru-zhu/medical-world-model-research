# Independent Reviewer 1: Final Targeted Sign-off

## Decision

**Statistical and experimental-design sign-off granted.**

I verified the current manuscript, supplement, figure contracts, final figure
PDFs, frozen result tables, implementation summaries, and audit JSON files. The
minor-revision issues identified in my follow-up review have been resolved.

## Targeted verification

- Figure 1 now uses the appropriately bounded labels “Finite-draw
  uncertainty” and “Chart-state constraints.” The PDF text and rendered figure
  agree.
- Figure 3 labels panel a as empirical 5th–95th-percentile coverage and
  separately identifies the infinite-draw 0.90 target and the 20-draw
  exchangeable expectation. It does not imply underlying-distribution
  calibration.
- The main direct-results table now reports “12 h empirical interval coverage
  (20 draws),” rather than coverage error. Its values—0.8422, 0.8673, and
  0.4981—match the frozen external-results CSV.
- Supplementary Table S1 contains all 24 variables, includes original units
  and target counts, and explains that the values pool observed targets rather
  than decompose the patient-macro outcome. All 96 displayed ridge/neural MAE
  entries match the frozen variable-level CSV at the reported precision.
- Supplementary Table S4 accurately records the training windows, validation
  windows, optimizer, loss weights, scale bounds, seeds, model dimensions,
  parameter counts, and checkpoint behavior. The five summaries confirm epoch
  20 for every GRU-D and Transformer run and epochs 7–20 for the state-space
  runs.
- The contradictory limitation has been corrected: variable-level errors are
  now described as descriptive and lacking clinician-validated importance
  thresholds.
- The figure contracts consistently use finite-draw, spread-adaptation, and
  chart-state-constraint language and no longer claim Monte Carlo convergence
  or general physiological validity.
- All five final figure PDFs are readable and text-extractable. Their
  collision-audit JSON files postdate the final renders by approximately
  67–69 seconds; every audit is `PASS`, with zero failures and zero warnings.
  All alignment JSON files also report `PASS` and were generated in the same
  render cycle.
- A fresh package-validator run reproduced
  `technical_pass_submission_gates_pending`.

## Remaining machine-fixable scientific blockers

**None.** I found no remaining factual, statistical, experimental-design, or
figure-reporting problem that requires another analysis, model run, or
machine-fixable scientific revision.

The stable code and artifact repository remains marked pending in the
validator. This is a technical release gate, not a scientific defect in the
current manuscript.

## Human and institutional submission gates

The remaining gates are clinical-domain review, institutional ethics
confirmation, final author and affiliation metadata, funding/competing
interests/CRediT statements, human verification of references and the
generative-AI disclosure, and final author confirmation that the released
repository is the frozen package reviewed here.

## Final recommendation

**Approve for submission once the outstanding technical-release and human
submission gates are completed.** From the Reviewer 1 statistics,
experimental-design, and reproducibility perspective, no further scientific
revision is required.
