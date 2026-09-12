# Independent Publication-Lineage Audit of Eight Provisional Additions

**Audit cutoff:** 12 September 2026  
**Scope:** Five records in `novel-empirical.csv`, three records in `novel-reviews.csv`, and identity overlap with the 53 records in `final-corpus/included.csv`.  
**Independence:** The existing `review-lineage-audit.md` was not used. Each record was rechecked against its current public primary source, DOI metadata where available, Europe PMC where indexed, and exact-title/author searches for alternate versions or publication successors.

## Interpretation rules

- **Confirmed** means directly supported by a current repository, publisher, DOI-registration, or bibliographic record.
- **No public successor identified** means that exact-title, identifier, author/title, and publisher/repository searches found no newer public record by the cutoff. It does not exclude an unpublished, renamed, under-review, or not-yet-indexed manuscript.
- **Identity overlap** concerns bibliographic duplicates, manuscript versions, and study families. Topical similarity alone is not treated as identity.
- A live source and the absence of a Crossref or Europe PMC retraction flag are negative checks, not an absolute guarantee that no undiscovered notice exists.

## Record-level findings

### 1. MWM-X962473BB89 — Chreode

**Canonical recommended citation/version**

Mufan Qiu, Genhui Zheng, Yinuo Xu, Ruichen Zhang, Ying Ding, Qi Long, and Tianlong Chen. “Chreode: A Cell World Model for One-Step Temporal Dynamics and Perturbation Prediction.” *arXiv* 2605.28111, version 1, 27 May 2026.

**Confirmed facts**

- The current arXiv record remains **v1**, submitted 27 May 2026.
- The arXiv comment says “Submitted to NeurIPS 2026”; this is a submission statement, not evidence of acceptance or peer review.
- The current arXiv page is live and does not display a withdrawal notice.
- No exact title, arXiv identifier, DOI, or full-author duplicate occurs in the canonical corpus.
- Apparent surname matches in the corpus are common-name collisions, not author-identity evidence.

**Unresolved author or venue verification**

- No public NeurIPS proceedings/OpenReview acceptance record or peer-reviewed successor was identified by the cutoff. A renamed or non-public submission remains possible and should be verified with the corresponding author after NeurIPS decisions.

**Evidence URLs**

- Current record and version history: <https://arxiv.org/abs/2605.28111>
- Version-specific record: <https://arxiv.org/abs/2605.28111v1>

**Overlap result:** New bibliographic identity; no canonical-corpus duplicate.  
**Confidence:** High for version and overlap; medium for absence of a publication successor.

### 2. MWM-XC0A20D0271 — Clin-JEPA

**Canonical recommended citation/version**

Yixuan Yang, Mehak Arora, Ryan Zhang, Baraa Abed, Junseob Kim, Tilendra Choudhary, Md Hassanuzzaman, Kevin Zhu, Ayman Ali, Chengkun Yang, A. E. Gent, Victor Moas, and Rishikesan Kamaleswaran. “Clin-JEPA: A Multi-Phase Co-Training Framework for Joint-Embedding Predictive Pretraining on EHR Patient Trajectories.” *arXiv* 2605.10840, **version 4**, 4 July 2026.

**Confirmed facts**

- arXiv lists four versions: v1 on 11 May, v2 on 12 May, v3 on 16 June, and current **v4 on 4 July 2026**.
- The arXiv record has no journal-reference field and remains publicly categorized as a preprint.
- The current arXiv page is live and does not display a withdrawal notice.
- No exact title, arXiv identifier, DOI, or full-author duplicate occurs in the canonical corpus.

**Unresolved author or venue verification**

- No peer-reviewed successor or renamed venue version was identified publicly. Because the manuscript has changed several times, the authors should confirm whether v4 is the version intended for citation and whether a venue submission exists under another title.

**Evidence URLs**

- Current record and complete version history: <https://arxiv.org/abs/2605.10840>
- Canonical version-specific record: <https://arxiv.org/abs/2605.10840v4>
- Public code repository linked from arXiv: <https://github.com/Kamaleswaran-Lab/Clin-JEPA>

**Overlap result:** New bibliographic identity; no canonical-corpus duplicate.  
**Confidence:** High for version and overlap; medium-high for absence of a public successor.

### 3. MWM-XFA677C184B — DRIFT

**Canonical recommended citation/version**

Weixin Liu, Juming Xiong, Congning Ni, Yanfan Zhu, Xingtao Lin, Bradley Malin, and Zhijun Yin. “DRIFT: Direct-Recursive Intervention-Conditioned Forecasting of ICU Physiological Trajectories.” *arXiv* 2607.25864, version 1, 28 July 2026.

**Confirmed facts**

- The current arXiv record remains **v1**, submitted 28 July 2026.
- No journal reference or publication DOI is present on arXiv; external bibliographic metadata resolves only to the arXiv work.
- The current arXiv page is live and does not display a withdrawal notice.
- No exact title, arXiv identifier, DOI, or full-author duplicate occurs in the canonical corpus.

**Unresolved author or venue verification**

- No peer-reviewed successor or renamed submission was identified publicly. The authors should confirm any active journal or conference submission before corpus freeze.

**Evidence URLs**

- Current record and version history: <https://arxiv.org/abs/2607.25864>
- Version-specific record: <https://arxiv.org/abs/2607.25864v1>

**Overlap result:** New bibliographic identity; no canonical-corpus duplicate.  
**Confidence:** High for version and overlap; medium-high for absence of a public successor.

### 4. MWM-X6C3AA8358E — Ultrasound-driven autonomous microrobots

**Canonical recommended citation/version**

Mahmoud Medany, Lorenzo Piglia, Liam Achenbach, S. Karthik Mukkavilli, and Daniel Ahmed. “Model-based reinforcement learning for ultrasound-driven autonomous microrobots.” *Nature Machine Intelligence* 7(7), 1076–1090 (2025). <https://doi.org/10.1038/s42256-025-01054-2>

**Confirmed facts**

- The Nature Machine Intelligence article, published 26 June 2025, is the peer-reviewed **version of record**.
- Crossref explicitly links bioRxiv DOI `10.1101/2024.09.28.615576` as the article’s preprint. The titles and complete author order match.
- The journal article therefore supersedes the bioRxiv version for citation and extraction; the two must not be counted separately.
- The Nature article is live. Crossref reports no update-to relation, and Europe PMC does not flag the article as retracted or withdrawn.
- Neither the journal DOI nor its bioRxiv DOI appears in the canonical corpus.

**Unresolved author or publisher verification**

- No material lineage uncertainty remains. Routine final checks may still confirm that no correction notice was posted after the audit cutoff.

**Evidence URLs**

- Publisher version of record: <https://www.nature.com/articles/s42256-025-01054-2>
- DOI record: <https://doi.org/10.1038/s42256-025-01054-2>
- Preprint: <https://www.biorxiv.org/content/10.1101/2024.09.28.615576v1>
- Crossref article metadata and explicit preprint relation: <https://api.crossref.org/works/10.1038/s42256-025-01054-2>
- Europe PMC record: <https://europepmc.org/article/MED/40709099>

**Overlap result:** No canonical-corpus duplicate; confirmed internal preprint-to-journal duplicate that must resolve to the journal article.  
**Confidence:** Very high.

### 5. MWM-X5E3C456867 — Towards Surgical World-Action Modeling

**Canonical recommended citation/version**

Weiliang Huang, Huanrong Liu, Bob Zhang, Qi Dou, Zhen Chen, Yun Gu, Guy Rosman, and Qingbiao Li. “Towards Surgical World-Action Modeling: A Preliminary Joint Visual-Trajectory Forecasting for Surgical Motion Planning.” *arXiv* 2608.20284, version 1, 20 August 2026.

**Confirmed facts**

- The current arXiv record remains **v1**, submitted 20 August 2026, with no journal reference.
- The current arXiv page is live and does not display a withdrawal notice.
- This manuscript is not the same paper as canonical record **MWM-0175**, “SurgWMBench: A Vision-Based Benchmark for World-Modeling Surgical Instrument Motion Planning” (arXiv:2608.08070).
- It is, however, a confirmed **companion study**: the provisional paper explicitly evaluates its model on SurgWMBench and cites arXiv:2608.08070. Four authors overlap exactly—Huanrong Liu, Weiliang Huang, Bob Zhang, and Qingbiao Li.
- The records have different titles, identifiers, author lists, and contribution types: benchmark versus preliminary forecasting model.

**Unresolved author or venue verification**

- No peer-reviewed successor was identified for the preliminary model.
- The authors should confirm whether this manuscript is intended to remain a separate report or be merged into a later SurgWMBench/model publication. Until then, it should not be treated as independent external validation of the benchmark.

**Evidence URLs**

- Preliminary model record: <https://arxiv.org/abs/2608.20284>
- Version-specific record: <https://arxiv.org/abs/2608.20284v1>
- Full text showing evaluation on and citation of SurgWMBench: <https://arxiv.org/html/2608.20284>
- Canonical companion benchmark: <https://arxiv.org/abs/2608.08070>

**Overlap result:** Distinct paper but confirmed companion-study lineage with canonical MWM-0175; not an independent benchmark validation.  
**Confidence:** High.

### 6. MWM-X9655500E17 — Medical World Model: From Passive Prediction to Active Simulation in Medicine

**Canonical recommended citation/version**

Numan Saeed, Salma Hassan, Shadab Khan, Mohammad Areeb Qazi, Klaus H. Maier-Hein, Salman Khan, and Mohammad Yaqub. “Medical World Model: From Passive Prediction to Active Simulation in Medicine.” *Preprints.org*, version 1, 30 April 2026. <https://doi.org/10.20944/preprints202604.2168.v1>

**Confirmed facts**

- The public record remains **v1**, posted 30 April 2026. Crossref classifies it as posted content/preprint, not a journal article.
- No later version DOI, publication DOI, or explicit Crossref publication relation was identified.
- The current source is live; Crossref reports no update-to relation, and Europe PMC does not flag the record as retracted or withdrawn.
- It is not a bibliographic duplicate of canonical **MWM-0234**, “Beyond Generative AI: World Models for Clinical Prediction, Counterfactuals, and Planning” (arXiv:2511.16333).
- It has confirmed author-lineage overlap with MWM-0234 through Mohammad Areeb Qazi and Mohammad Yaqub. The records are therefore not products of independent author groups.

**Unresolved author or venue verification**

- No peer-reviewed successor was identified publicly.
- The newer preprint describes its capability progression as originating in earlier work, and MWM-0234 is a prior shared-author synthesis with closely matching framing. This supports, but does not by itself prove, direct manuscript lineage. The degree of text, taxonomy, and evidence reuse should be checked side by side before the two papers are treated as independent review evidence. They should remain separate bibliographic items unless the authors identify the newer manuscript as a formal replacement.

**Evidence URLs**

- Current preprint page: <https://www.preprints.org/manuscript/202604.2168/v1>
- DOI record: <https://doi.org/10.20944/preprints202604.2168.v1>
- Crossref metadata: <https://api.crossref.org/works/10.20944/preprints202604.2168.v1>
- Europe PMC record: <https://europepmc.org/article/PPR/PPR1186035>
- Canonical related synthesis MWM-0234: <https://arxiv.org/abs/2511.16333>

**Overlap result:** Distinct preprint with confirmed shared-author lineage and probable conceptual lineage with canonical MWM-0234; do not treat author-group agreement as independent corroboration.  
**Confidence:** High for metadata and author overlap; medium for direct manuscript lineage and the extent of reuse pending side-by-side full-text verification or author confirmation.

### 7. MWM-XA5E34A98D0 — Towards Effective Patient Simulators

**Canonical recommended citation/version**

Vadim Liventsev, Aki Härmä, and Milan Petković. “Towards Effective Patient Simulators.” *Frontiers in Artificial Intelligence* 4:798659 (2021). <https://doi.org/10.3389/frai.2021.798659>

**Confirmed facts**

- The Frontiers article published 15 December 2021 is the peer-reviewed version of record.
- Crossref, PubMed, and Europe PMC agree on title, author order, date, venue, and DOI.
- No linked preprint, later version, duplicate DOI, correction, or successor article was identified.
- The publisher article is live. Crossref reports no update-to relation, and Europe PMC does not flag it as retracted or withdrawn.
- No exact title, DOI, or author-list duplicate occurs in the canonical corpus.

**Unresolved author or publisher verification**

- No material lineage uncertainty remains. A routine final publisher check should still be repeated immediately before submission because notices can appear after the cutoff.

**Evidence URLs**

- Publisher version of record: <https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2021.798659/full>
- DOI record: <https://doi.org/10.3389/frai.2021.798659>
- Crossref metadata: <https://api.crossref.org/works/10.3389/frai.2021.798659>
- PubMed record: <https://pubmed.ncbi.nlm.nih.gov/34977561/>
- Europe PMC record: <https://europepmc.org/article/MED/34977561>

**Overlap result:** New bibliographic identity; no canonical-corpus duplicate.  
**Confidence:** Very high.

### 8. MWM-X198B3126D0 — What Makes a Virtual Cell a World Model?

**Canonical recommended citation/version**

Chang Yu, Jingbo Zhou, Cheng Tan, Stan Z. Li, Xiaodong Liu, Xiaoming Zhang, Zhaoxiang Zhang, Zhen Lei, and Zhongqi Wang. “What Makes a Virtual Cell a World Model? Three Gaps, Three Experiments, and a Roadmap.” *Research Square*, version 1, 21 July 2026. <https://doi.org/10.21203/rs.3.rs-10404367/v1>

Use this Research Square version for claims or extraction involving the “three experiments,” because it is the later and more extensive public manuscript.

**Confirmed facts**

- Crossref records Research Square **v1**, posted 21 July 2026, with nine named authors and no journal-publication relation.
- A related earlier record exists on OpenReview: “What Makes a Virtual Cell a World Model? Three Gaps, Three Axes, and a Roadmap,” presented as a poster at the ICML 2026 Workshop on Foundation Models in the Wild and published 28 May 2026.
- The workshop record shares the first five authors—Chang Yu, Jingbo Zhou, Cheng Tan, Stan Z. Li, and Xiaodong Liu—and has a closely corresponding title and abstract. The Research Square manuscript adds four authors and changes “Three Axes” to “Three Experiments.”
- Chronology therefore rules out the workshop poster as a newer successor. The Research Square manuscript is the later public branch, while the OpenReview page supplies an earlier workshop-poster lineage record. The public page does not establish the workshop's review procedure strongly enough to label this a peer-reviewed predecessor.
- The Research Square source is live; Crossref reports no update-to relation, and Europe PMC does not flag it as retracted or withdrawn.
- Neither version duplicates a record in the canonical corpus.

**Inferred lineage requiring author verification**

- The shared title stem, first five authors, framing, and chronology make a common manuscript lineage highly likely, but neither primary record exposes a formal identifier relation. The authors should confirm whether the Research Square version supersedes the workshop poster or should be treated as a substantially expanded companion work.
- No later peer-reviewed journal or conference successor was identified by the cutoff.

**Evidence URLs**

- Research Square version: <https://www.researchsquare.com/article/rs-10404367/v1>
- DOI record: <https://doi.org/10.21203/rs.3.rs-10404367/v1>
- Crossref metadata: <https://api.crossref.org/works/10.21203/rs.3.rs-10404367/v1>
- Europe PMC record: <https://europepmc.org/article/PPR/PPR1282602>
- Earlier ICML workshop poster: <https://openreview.net/forum?id=65aPZeNQVJ>
- Workshop poster PDF: <https://openreview.net/pdf?id=65aPZeNQVJ>

**Overlap result:** New relative to the canonical corpus; probable expanded-version lineage with an earlier ICML workshop poster, which must not be added as an independent review.  
**Confidence:** High for metadata, chronology, and shared authors; medium-high for formal supersession pending author confirmation.

## Corpus changes required

1. **Clin-JEPA:** cite and extract from **arXiv v4**, not v1–v3 or an unspecified version.
2. **Microrobot study:** retain only the Nature Machine Intelligence version of record; record bioRxiv `10.1101/2024.09.28.615576` as its preprint and never count it separately.
3. **Surgical preliminary model:** retain as a distinct report, but link it to canonical **MWM-0175 SurgWMBench** as a companion study and do not label its benchmark use as independent external validation.
4. **Saeed review:** retain as a distinct preprint, but tag its shared-author/probable conceptual lineage with canonical **MWM-0234** and avoid treating author-group agreement as independent corroboration.
5. **Virtual-cell roadmap:** use Research Square v1 as the canonical expanded manuscript; link the earlier ICML workshop poster as the same probable lineage and do not add the poster as an independent record.
6. **Chreode, DRIFT, Towards Effective Patient Simulators:** no lineage-driven merge, deletion, or replacement is required. Preserve current preprint/article status and repeat the dated successor/retraction check immediately before corpus freeze.
