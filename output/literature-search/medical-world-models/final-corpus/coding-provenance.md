# MedWM-Eval Coding Provenance

Freeze date: 2026-09-12

Canonical corpus: 85 empirical studies  
Separate coding decisions: 1,785 study-field pairs per reviewer pair  
Adjudicated disagreements: 214 across 71 studies

## Preserved materials

- Frozen rubric: `../medwm-eval-pilot-rubric.md`
- Full codebook: `../medwm-eval-codebook.md`
- Independent coding exports: `medwm-pilot-reviewer-a.csv` and
  `medwm-pilot-reviewer-b.csv`
- Pre-adjudication disagreements:
  `pilot-comparison/disagreements.csv`
- Final adjudicated coding: `medwm-eval-final.csv`
- Reliability analysis: `reliability-analysis.json`

## Independence boundary

The two coding passes were executed as separate AI-assisted review contexts
against the same frozen rubric and primary-text extraction. Each pass was
completed before adjudication. The final coding file preserves the fields that
required adjudication and the source anchors used for resolution.

The 35 studies added by search correction were processed as a five-study
completed audit sample and three disjoint ten-study batches. Each batch used
separate extraction and MedWM-Eval passes before source-grounded adjudication.

## Unresolved provenance

The exact model build identifiers, system prompts, sampling parameters, and
runtime package versions for the original two coding passes were not captured
in a durable machine-readable manifest. Those details must not be reconstructed
from memory or implied in the manuscript.

This omission limits exact computational replay. Before submission, the coding
should be repeated or verified by two human reviewers, and any future AI-
assisted replication should record model identifier, prompt files, sampling
parameters, execution date, evidence access, and independence controls.
