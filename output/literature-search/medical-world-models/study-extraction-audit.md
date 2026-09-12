# Study-Extraction Audit

> **Superseded developmental artifact.** This file describes the provisional
> 55-study extraction before the post-extraction eligibility re-audit. The
> authoritative manuscript corpus, extraction, and audit outputs are under
> `final-corpus/`. Do not use the counts in this file for submission.

Freeze date: 2026-09-12  
Records: 55 empirical studies  
Fields per record: 45  
Status: AI-assisted primary-text extraction complete; human author verification pending

## Structural Validation

- Four disjoint extraction batches contain 14, 14, 14, and 13 studies.
- The canonical merge contains every empirical candidate ID exactly once.
- Candidate IDs, titles, and canonical order are preserved.
- No extraction cell is blank.
- Unavailable or inapplicable evidence is represented as `NI` or `NA`.
- Every record contains source anchors and an appraisal of strengths and
  limitations.

## Source-Access Limitations

- MWM-0135 was available as Markdown rather than a stable typeset PDF.
- MWM-0164 had non-blocking PDF syntax warnings.
- MWM-0174 referenced an appendix that was not available.
- MWM-0290 was extracted from arXiv after a TLS issue affected the CVF PDF
  mirror; the official proceedings record was separately verified.
- Full primary text could not be established for MWM-0137, MWM-0154,
  MWM-0176, and MWM-0207; their unavailable fields are coded `NI` and require
  human adjudication before submission.

## Priority Human-Adjudication Set

The extraction reviewers flagged the following studies for especially careful
checking because of causal or capability overclaims, inconsistent cohort
counts or splits, unavailable artifacts, unsupported action/physics claims, or
scope ambiguity:

`MWM-0074`, `MWM-0077`, `MWM-0095`, `MWM-0114`, `MWM-0135`, `MWM-0136`,
`MWM-0149`, `MWM-0157`, `MWM-0164`, `MWM-0166`, `MWM-0174`, `MWM-0175`,
`MWM-0200`, `MWM-0207`, `MWM-0215`, `MWM-0239`, `MWM-0261`, `MWM-0263`,
`MWM-0290`, `MWM-S004`, and `MWM-S006`.

## Evidence Boundary

This extraction is an auditable development artifact. It is not equivalent to
human dual extraction. Before submission, domain authors must verify the
priority set, all `NI` fields that affect synthesis claims, and a random sample
of the remaining records.
