# Round 1 Revision Log

Status date: 2026-09-12  
Manuscript status: developmental; not submission-ready

| Reviewer issue | Revision or evidence | Status |
| --- | --- | --- |
| Human verification pending | Manuscript, validation output, and figure footer retain a hard submission gate | Open: requires qualified human reviewers |
| Literal world-model search boundary | Removed publisher exclusion; resolved the 170-record audit to eight additions; completed dual title/abstract and dual full-text review, third adjudication, independent QC, and conceptual-equivalence review for both exhaustive tracks; retained 26 expanded-search and 6 residual-rescreen core records; completed cross-source lineage adjudication of all 40 novel records with 40 retained as distinct publications | Screening correction and lineage resolution implemented; corrected corpus is 93 publications (85 empirical, 8 reviews); novel-study extraction is in progress |
| Missing engineering and citation databases | Public OpenAlex and Crossref supplements added; authenticated IEEE Xplore, ACM DL, Scopus, and Web of Science remain unavailable | Open submission gate |
| Corpus boundary instability | Added strict-core versus extended-corpus sensitivity coding | Implemented; rerun after search update |
| Re-audit chronology and stale artifacts | Marked provisional 55-study files superseded and added canonical-artifact routing | Implemented |
| Agreement statistics incomplete | Added study-bootstrap confidence intervals and linear/quadratic weighted kappa for ordinal fields | Implemented |
| Sampled-audit additions require independent extraction and coding | Completed two source-grounded extraction and MedWM-Eval coding passes for five empirical additions; the coding passes agreed on 91/105 decisions (86.67%), and all 14 disagreements across four studies were source-grounded and adjudicated. The remaining 30 novel empirical studies are partitioned into three disjoint ten-record batches for independent extraction and coding. | Implemented for five additions; dual review in progress for the remaining 30 |
| AI coding provenance incomplete | Added provenance record that explicitly documents unavailable model and prompt metadata | Implemented with limitation |
| Structured source-quality sensitivity | Added peer-reviewed versus preprint or unreviewed analysis and study-characteristics export | Implemented; rerun after search update |
| Planned methodological-quality appraisal | Added a non-scored, source-anchored domain appraisal of missingness, censoring, calibration, external validation, causal estimands, action testing, closed-loop setting, safety, code, and reproducibility; no universal risk-of-bias score is claimed | Implemented for development snapshot; regenerate and human-verify after search update |
| Capability by evidence missing | Added capability-by-evidence and domain-by-evidence heat map | Implemented; rerun after search update |
| Original experiment embedded in review | Removed PhysioNet selection and sanity-baseline results from the review | Implemented |
| Figure 1 arithmetic and exclusions | Figure builder now supports citation, filter-audit, re-audit, and exclusion-reason branches | Implemented in code; awaiting final counts |
| Figure 2 unresolved denominators | Added unclear counts and explicit total-corpus denominator convention | Implemented |
| Table numbering and callouts | Added titles and callouts for the quantitative summary, review comparison, and capability-evidence matrix | Implemented |
| Unsupported temporal rhetoric | Replaced “advancing faster than evaluation” with evidence-specific wording | Implemented |
| Five inaccessible records | Corrected limitations text and figure data model | Implemented |
| Reference integrity | Added authoritative publication overrides for key peer-reviewed records | Partially implemented; final corpus audit pending |
| Central empirical versus aspirational claims | Added a study-level claim-provenance audit linking each highest claim to extracted claim boundaries, causal language, decision utility, safety evidence, source anchors, and capability-specific absent or partial evidence; the routing priority is explicitly not a quality score | Implemented for development snapshot; regenerate after search update and verify with human reviewers |
| Study-level overlap with Chen et al. | Reconstructed a high-confidence 14-study strict empirical roster from the review text and source package; mapped 13/14 to the development snapshot and documented EchoJEPA as the boundary disagreement | Implemented provisionally; roster was reconstructed rather than author-supplied and requires final verification |
| Human content validation of MedWM-Eval | Requires clinical, causal, embodied-control, and measurement experts | Open submission gate |

The manuscript's count-dependent figures must be regenerated only after
extraction and MedWM-Eval coding are frozen. The graphical abstract is
count-independent and has been finalized with an action-agnostic comparator and
real-world transfer terminology.
