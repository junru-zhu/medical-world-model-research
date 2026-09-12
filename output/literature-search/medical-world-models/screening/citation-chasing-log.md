# Citation-Chasing and Coverage Audit

Audit date: 2026-09-12  
Final database-search candidate count: 409  
Citation-chasing records assessed: 6  
Citation records duplicated in final database search: 2  
Unique citation-chasing records: 4  
Combined unique title/abstract screening count: 413

## Purpose

The public database search preserves the exact results returned by PubMed, Europe PMC, OpenAlex, Crossref, and the arXiv HTML fallback. A separate citation-chasing stratum was added because bibliographic search ranking and incomplete indexing can miss a named world-model paper even when the paper is eligible. Citation records later recovered by the arXiv fallback are treated as database duplicates rather than additional unique records.

## Seed sources

- the empirical and reference tables in Chen et al., *Medical World Models in Healthcare* (arXiv:2607.25242);
- backward citation checking from treatment-response and surgical world-model studies;
- exact-title and identifier checks against OpenAlex, arXiv records, and official CVF pages.

## Supplemental records

| ID | Record | Reason it was added |
| --- | --- | --- |
| MWM-S001 | EchoJEPA | Included in the closest competing review's empirical subset, but not returned by the frozen ranked search because its title does not use “world model.” |
| MWM-S002 | Xray2Xray | Initially found through citation chasing; subsequently recovered by the final arXiv HTML fallback and counted as a database duplicate. |
| MWM-S003 | Treatment-aware Diffusion Probabilistic Model (TaDiff) | Operationally models treatment-conditioned future MRI and tumor evolution without using “world model” in the title. |
| MWM-S004 | Cosmos-H-Surgical | Surgical policy learning via world modeling; absent from the ranked candidate result despite a stable arXiv identifier. |
| MWM-S005 | Surgical Vision World Model | Initially found through citation chasing; subsequently recovered by the final arXiv HTML fallback and counted as a database duplicate. |
| MWM-S006 | Surgical Procedural Planning as 3D World Modelling: Towards Automated Pulmonary Resection | Official CVPR 2026 Workshop paper identified during forward citation and exact-title checking. |

## Anchor coverage in the database stratum

The final 409-record database stratum contains EHRWorld, HealthFormer, ChronoMedicalWorld, the intervention-aware cardiology model, MeWM, CLARITY, Brain-WM, Cardiac Copilot, EchoWorld, SAW, Surg-UniWorld, Surgical WAM, SurgVista, SWoMo, CheXWorld, GazeWorld, DreamReg, Policy4OOD, the acute-kidney-injury offline-RL world model, CrossScope (arXiv:2608.03211), SurgWMBench, HounsWorld, Xray2Xray, and Surgical Vision World Model.

Both database and supplemental strata undergo the same independent screening rubric. Human author verification and full-text eligibility review remain required before submission.
