# Existing-Review Comparison

Extraction date: 2026-09-12  
Purpose: define the novelty boundary of the evaluation-centred review

## Criterion-Level Crosswalk

| Review | Scope and method | Organizing framework | Empirical evidence accounting | Evaluation contribution | Gap left for this review |
| --- | --- | --- | --- | --- | --- |
| Qazi et al., *Beyond Generative AI* (2025) | Focused narrative survey; no reproducible database flow or eligible-study denominator reported | L1 prediction, L2 action-conditioned prediction, L3 counterfactual rollout, L4 planning/control | Representative systems in a narrative table | Identifies action semantics, calibration, causal grounding, safety constraints, and decision-aligned evaluation as open needs | Does not operationalize or apply a study-level claim-to-evidence codebook |
| Liu et al., *Medical World Models* (2026) | Roadmap review; no database-specific search, screening flow, or frozen empirical denominator reported | Patient-state construction, clinical dynamics, intervention support, and compositional system patterns | Broad examples spanning records, imaging, biology, robotics, and adjacent methods | Calls for trajectory-level evaluation, calibrated uncertainty, causal validation, and procedural safety | Does not quantify which empirical studies supply each required evidence type |
| Chen et al., *Medical World Models in Healthcare* (2026) | Structured narrative evidence map; 1,455 unique screened records, 98-source narrative corpus, and 14 strict empirical studies | Foundations, application domains, L1-L4 capability, and trustworthy translation | Explicit search flow and empirical subset; broader contextual sources retained separately | Detailed synthesis of action semantics, causal identifiability, uncertainty, safety, governance, and clinical maturity | Closest competitor; does not publish an independently piloted criterion-level MedWM-Eval audit across the larger September 2026 empirical corpus |
| Liventsev et al., *Towards Effective Patient Simulators* (2021) | Review and comparative methods article on interactive patient simulators; also introduces three simulator implementations | Simulator goals, state and action representations, transition behavior, rewards, transparency, bias, and validity | Qualitative and quantitative comparison of existing and introduced simulators, including data-derived ICU simulation | Makes intervention-conditioned future-state simulation and simulator validation explicit | Predates current medical-world-model terminology and does not audit a cross-domain empirical corpus against capability-matched evidence requirements |
| Saeed et al., *Medical World Model: From Passive Prediction to Active Simulation in Medicine* (2026) | Narrative preprint defining medical world models and synthesizing clinical application areas; no reproducible study-flow denominator reported | Representation, forecasting, single-arm projection, comparative treatment evaluation, and planning | Representative evidence across imaging, physiology, longitudinal records, and surgical simulation | Centers action definition, causal validity, staged validation, and regulatory oversight | Closely overlaps the claims-to-evidence motivation but does not publish criterion-level dual coding, reliability analysis, or a reproducible empirical evidence matrix |
| Yu et al., *What Makes a Virtual Cell a World Model?* (2026) | Virtual-cell review and framework paper supported by three diagnostic experiments | Dynamics, intervention, and scale, each with an L0-L3 capability ladder | Synthesizes mechanistic simulators, foundation models, perturbation predictors, and multimodal systems, with empirical diagnostics of representation, iterative closure, and intervention effects | Explicitly tests why representation is not dynamics, prediction is not intervention, and multimodality is not multiscale modeling | Provides the closest cellular evaluation framework but not a cross-medical study-level audit of rollout, causal, external, decision, safety, and reproducibility evidence |
| Alharthi, *AI-powered in silico twins* (2025) | Broad narrative review of patient-specific in silico twins across the care continuum | Architecture taxonomy spanning mechanistic and AI models, multimodal data integration, simulation infrastructure, and clinical deployment | Application examples are synthesized narratively rather than through an eligible-study denominator | Adds a verification-and-validation checklist and a translation-oriented deployment blueprint | Provides useful credibility and deployment principles but does not test whether empirical claims are matched by study-level rollout, causal, external, decision, or safety evidence |
| Métayer et al., *Data-driven discovery of digital twins in biomedical research* (2026) | Methodological review of 177 approaches for automated dynamical-system discovery from biological time series, accompanied by a Shiny application | Eight challenges covering data quality, multiple conditions, prior knowledge, latent variables, dimensionality, derivative estimation, library design, and uncertainty | Explicit method count and criterion-based comparison, concentrated on symbolic and sparse regression with emerging deep-learning methods | Identifies hybrid mechanistic, Bayesian, and generative systems as a route to more reliable biomedical digital twins and motivates benchmark development | Deeply evaluates model discovery but not patient/procedural capability claims, intervention-conditioned rollouts, institutional transfer, or clinical decision utility |
| Müller et al., *Can Pharmaceutical World Models Become Scientific Instruments?* (2026) | Adjacent pharmaceutical state-of-the-art review; eligibility concepts are described, but reproducible search strings, record counts, and a study flow are not reported | State, intervention, time, causality, uncertainty, applicability, and scientific-instrument readiness | Narrative examples and conceptual validation layers rather than a frozen clinical empirical corpus | Separates benchmark performance from prospective experimental confirmation and proposes readiness boundaries | Domain is pharmaceutical discovery rather than patient/procedural medical-world-model evaluation; no study-level clinical evidence audit |
| Present review | PRISMA-ScR-oriented public search with AI-assisted dual screening, adjudication, discovery-filter correction, and human verification pending | Capability claim × operating regime × evidence domain | The corrected publication-lineage-resolved corpus contains 85 empirical studies and 8 reviews; all 35 new empirical studies completed dual extraction, coding, and adjudication | Quantifies free-running rollout, action sensitivity, uncertainty, causal validity, external validation, decision utility, safety, and reproducibility against the highest claim made | Submission readiness depends on qualified human verification and codebook content validation rather than on proposing another capability taxonomy |

## Defensible Novelty Claim

The capability ladder, causal caveats, uncertainty requirements, and broad
translation agenda are not new. The defensible contribution is an operational
and auditable mapping from the highest capability claimed by each empirical
system to the evidence actually reported for that claim.

The review should therefore avoid claiming that it introduces the first medical
world-model taxonomy. Its contribution should be described as:

1. a reproducible, evaluation-centred evidence map with explicit denominators;
2. a study-level MedWM-Eval codebook with source anchors and applicability
   rules;
3. capability-matched quality appraisal without a misleading universal score;
4. dataset task cards that state permissible and unsupported claims; and
5. a real-data benchmark derived from the most persistent cross-study evidence
   gap.

## Source Anchors

- Qazi et al.: abstract; capability rubric and Table 1; limitations and research
  agenda; conclusion.
- Liu et al.: Sections 2-7; Figures 2, 5, and 6; evaluation and translation
  discussion.
- Chen et al.: Sections 2.1-2.5; literature-flow figure; empirical evidence
  table; Sections 4 and 7.
- Liventsev et al.: Sections 1.1-1.2 and 2-4; simulator comparison tables;
  discussion of transition accuracy, transparency, bias, and benchmark
  difficulty.
- Saeed et al.: abstract; capability ladder; domain synthesis; causal-validity
  and translation discussion.
- Yu et al.: Sections 1.1-2.4 and 5.1-5.2; three diagnostic experiments;
  dynamics/intervention/scale ladders and roadmap.
- Alharthi: abstract; architecture taxonomy; verification-and-validation
  checklist; deployment blueprint; clinical-translation discussion.
- Métayer et al.: abstract; 177-method evidence base; eight-challenge framework;
  method comparison; benchmark-development recommendations.
- Müller et al.: review-scope and analytical-framework section; scientific-
  instrument test; validation/readiness framework; conclusion.

Publication-lineage verification is complete for the eight included reviews.
Human authors should recheck bibliographic metadata at submission. The Müller
et al. review remains adjacent context rather than an included core review and
should not be used as an authoritative methodological source without an
explicit venue-quality assessment.
