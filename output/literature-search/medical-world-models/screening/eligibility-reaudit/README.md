# Final Eligibility Re-audit

Date: 12 September 2026

This pass checked every provisionally included empirical record against the
frozen full-text rubric after extraction and MedWM-Eval coding. Three
independent auditors reviewed disjoint empirical batches, and the lead
adjudicator resolved boundary cases. The review-comparison corpus was checked
separately against its medical or healthcare topic requirement.

The re-audit identified six provisional inclusions that should not remain in
the core corpus:

- four records lacked inspectable full text and could not support reliable
  extraction;
- one offline reinforcement-learning paper belongs in the causal-methodology
  bridge corpus because it does not learn patient-state dynamics;
- one pharmaceutical review is adjacent to, rather than primarily about,
  medical or healthcare world models.

The corrected corpus contains 50 empirical studies and three core reviews.
The original AI-assisted screening files remain unchanged as developmental
artifacts. `decisions.csv` records every correction, and the generated
`final-corpus/` directory is the source for the manuscript's final counts.

Human authors must still verify the complete corpus before submission.
