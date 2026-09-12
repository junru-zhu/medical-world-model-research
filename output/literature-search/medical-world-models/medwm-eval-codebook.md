# MedWM-Eval Preliminary Codebook

Status: Preliminary; requires dual coding and pilot validation

## Purpose

MedWM-Eval records whether the evidence reported by a study matches the capability it claims. It is a structured audit, not a universal leaderboard.

## Capability Tracks

| Track | Necessary model behavior | Core evidence |
| --- | --- | --- |
| Passive forecasting | Predict future state or observation under observed care | Free-running horizon analysis, state and transition validity, calibration |
| Action-conditioned simulation | Change rollout according to a defined action | Action provenance, action-agnostic baseline, valid perturbation tests, support/overlap |
| Counterfactual comparison | Compare outcomes under alternative interventions | Explicit estimand, causal assumptions, treatment strategies, confounding and censoring analysis, counterfactual validation |
| Closed-loop planning | Select sequential actions using model rollouts | Closed-loop task utility, model-mismatch stress tests, constraints, uncertainty-aware fallback, safety |

## Evidence Domains

### State and observation

- State variables and latent-state interpretation are documented.
- Clinically or procedurally relevant outputs are evaluated.
- Missingness and observation timing are modeled or analyzed.

### Dynamics and rollout

- Teacher-forced and free-running regimes are distinguished.
- Performance is reported by horizon.
- Stochastic models use repeated rollouts.
- Constraint violations and joint-state coherence are measured.
- Discharge, death, dropout, and competing events are handled where applicable.

### Actions

- The action represents intent, order, delivery, observed behavior, or simulated control.
- Timing and magnitude are defined.
- Action perturbations remain within observed or clinically plausible support.
- An action-agnostic or shuffled-action comparator is included when valid.

### Uncertainty

- Calibration or coverage is reported by horizon.
- Subgroup and distribution-shift calibration are considered.
- Uncertainty affects abstention, escalation, or planning when claimed.

### Causal validity

- The estimand and treatment strategies are explicit.
- Eligibility and time zero are aligned.
- Confounding, positivity, censoring, and interference assumptions are addressed.
- Individual counterfactual trajectories are not inferred solely from population-level validation.

### External validity

- External, temporal, institutional, device, or population validation is reported.
- Adaptation is distinguished from frozen evaluation.
- Both discrimination or error and calibration transfer are reported where applicable.

### Decision utility

- The downstream decision and user are defined.
- The comparator reflects current practice or a strong policy baseline.
- Decision utility is not inferred from generative fidelity alone.

### Safety

- Hazards and severity are defined for the deployment stage.
- Subgroup worst cases and simulator exploitation are tested when relevant.
- Human override, monitoring, model updates, and incident response are specified for clinical deployment claims.
- Embodied systems report physical constraints and failures; decision-support systems report harmful recommendations and automation-bias controls.

## Applicability Rule

Evidence is coded against the highest capability claim made in the title, abstract, introduction, results, or conclusion. Lower-capability evidence cannot by itself support a higher-capability claim.

## Pilot Output

The pilot table will contain:

```text
Study | Capability claimed | State | Dynamics | Rollout | Action |
Uncertainty | Causal validity | External validity | Decision utility |
Safety | Reproducibility | Reviewer notes
```

Scores will remain ordinal audit codes. They will not be summed into an overall quality rank unless validation shows that aggregation is meaningful.
