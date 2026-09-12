# Protocol Deviations and Search-Correction History

Status date: 12 September 2026

This supplement preserves the developmental search and eligibility history that
is intentionally condensed in the main manuscript. Dates refer to the final
review-development day because the protocol was not prospectively registered
and the public-search correction, eligibility re-audit, and corpus freeze were
completed within the same work cycle.

## Search and Eligibility Changes

| Date | Stage | Change | Reason | Effect on final analysis |
| --- | --- | --- | --- | --- |
| 12 September 2026 | Discovery quality control | Audited a stratified sample of records excluded by the initial phrase-and-domain discovery filter | Eligible digital-twin, patient-simulator, biological-dynamics, and model-based-control studies did not consistently use explicit world-model terminology | The discovery filter was withdrawn as an eligibility decision |
| 12 September 2026 | Search correction | Added a fresh alternate-term search and screened every remaining record excluded by the original discovery filter | Restore function-based coverage after the sampled audit detected missed eligible records | All 6,692 unique records received title and abstract decisions |
| 12 September 2026 | Inclusion quality control | Operationalized the functional identity rule as a learned or adapted temporal transition, rollout mechanism, or action-conditioned generative process with empirical future, action, counterfactual, or planning evaluation | Prevent ordinary forecasting, static generation, and adjacent methodology from entering the empirical corpus solely through broad terminology | Full-text and conceptual-equivalence exclusions were rechecked before corpus freeze |
| 12 September 2026 | Corpus boundary | Designated 82 directly clinical, biomedical, physiological, or medical-procedural studies as the primary set and retained three health-adjacent records only in an extended sensitivity set | Keep the main analysis aligned with the medical scope while exposing boundary sensitivity | Primary results use 82 studies; extended sensitivity uses 85 |
| 12 September 2026 | Publication lineage | Compared titles, authors, identifiers, dates, preprint and journal relationships, corrections, withdrawals, and retractions | Avoid double counting versions of the same study | Final lineage-resolved corpus contains 85 empirical publications and 8 reviews |
| 12 September 2026 | Reference verification | Checked all 93 included-publication citations and six method or dataset citations in seven disjoint batches against DOI, repository, index, publisher, or proceedings metadata | Remove incomplete citations, incorrect author names, and stale preprint-to-publication lineage before manuscript regeneration | Verified corrections are applied through a shared rendering-time override table used by both the numbered ledger and BibTeX builder |
| 12 September 2026 | Evidence framework | Retained separate denominators for claim-level action evidence and operational action-input tests | One planning paper made an action-level claim without implementing an action input | Ordinal action evidence is applicable to 73 primary studies; comparator and perturbation tests are applicable to 72 |

## Reference Verification

The audit covered author order, title, year, publication type, container title,
volume, issue, pages or article number, DOI, repository identifier, and formal
publication lineage. It corrected, among other records, the journal successor
for the treatment-aware diffusion study, the proceedings versions of CLARITY,
EchoWorld, Surgical Vision World Model, X-WIN, and medDreamer, and incomplete
metadata for the six method and dataset references.

The screening table remains frozen. Bibliographic corrections are stored in
`scripts/reference_overrides.py` and are applied when rebuilding both the
included-study ledger and `manuscript/references.bib`. This preserves the audit
trail while preventing a later rebuild from restoring stale metadata.

This was an AI-assisted source audit. A qualified human should still spot-check
the final rendered bibliography and any journal-specific reference style before
submission.

## Post-Extraction Eligibility Corrections

Six records were re-adjudicated after preliminary extraction. None contributes
to the final 82-study primary analysis.

| Candidate ID | Final disposition | Primary reason | Audit rationale |
| --- | --- | --- | --- |
| MWM-0042 | Excluded | Review not primary | Pharmaceutical-discovery models rather than medical or healthcare world models; retained only as adjacent background |
| MWM-0137 | Excluded | Inaccessible full text | Indexed abstract did not permit audit of the transition mechanism, rollout protocol, or primary empirical results |
| MWM-0154 | Excluded | Inaccessible full text | Indexed abstract did not permit verification of simulator calibration, rollout, or results |
| MWM-0176 | Excluded | Inaccessible full text | Temporal horizon, rollout, and primary dynamics evaluation could not be audited from the available abstract |
| MWM-0207 | Excluded | Inaccessible full text | Insufficient primary text for reliable methods and evaluation extraction |
| MWM-0320 | Bridge-methodology corpus | No learned dynamics | Estimated latent confounding, behavior policies, and action values without a learned future-state transition or generative patient rollout |

## Interpretation

These corrections improve coverage and consistency but do not replace the
remaining submission gates: authenticated engineering/citation-database
updates, information-specialist review, qualified human dual verification, and
expert content validation of MedWM-Eval.
