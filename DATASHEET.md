# Datasheet for MUSES + CiteRoots

This datasheet follows the structure of Gebru et al., *Datasheets for Datasets* (CACM 2021). It documents the MUSES benchmark and the two CiteRoots labeling layers as released for the NeurIPS 2026 Evaluations & Datasets track.

---

## 1. Motivation

### For what purpose was the dataset created?

MUSES was created to evaluate prospective intellectual-roots prediction: given an author's documented publication history at time *t*, can a system surface the prior works the author will engage with in their next paper? The two CiteRoots labeling layers were created to tighten the retrieval target from "any future citation" to citations that play generative roles in local text (CiteRoots-Rhetoric) and to citations the citing-paper authors themselves identify as intellectual roots (CiteRoots-Endorsement).

The dataset addresses a gap that conventional retrieval suites do not measure: those benchmarks evaluate topical retrieval, claim verification, or representation quality, whereas MUSES evaluates whether a system can recover the prior works that enter an author's next paper under progressively stricter familiarity and functional constraints.

### Who created the dataset and on behalf of which entity?

Anonymized for double-blind review. Will be filled in at de-anonymization.

### Who funded the creation of the dataset?

Anonymized for double-blind review.

---

## 2. Composition

### What do the instances represent?

The release comprises three classes of instance:

- **MUSES retrieval instances** are `(authorid, focal_corpusid)` tuples evaluated against a fixed candidate pool of 2,330,779 papers. Each tuple has three target sets derived from the bibliography of the author's first subsequent eligible paper after time *t*: CiteNext (any future citation), CiteNew (excludes citations the author had already used before *t*), and CiteNew-Isolated (also excludes citations explainable through coauthor diffusion within a five-year social neighborhood).
- **CiteRoots-Rhetoric labels** are paper-level aggregated rhetorical-role labels: for each benchmark-aligned focal→cited edge whose citation is linked to a local context window, a binary `ROOT` / `non-ROOT` label is emitted under a precision-first aggregation rule (positive iff at least one linked context is judged ROOT). A 1,200-context human-gold audit set with rater agreement metadata is included.
- **CiteRoots-Endorsement labels** are author-attested generative-inspiration pairs: 1,518 `(focal_corpusid, candidate_corpusid)` pairs collected through an author-response adjudication workbench, of which 435 are context-linked back to explicit focal-paper bibliography evidence and 402 are evaluable as retrieval targets within the released MUSES pool.

### How many instances are there in total?

| Subset | Count |
|--------|-------|
| MUSES instances (full) | 1,038,780 |
| MUSES test slice (CiteNext) | 168,613 |
| MUSES test slice (CiteNew) | 167,568 |
| MUSES test slice (CiteNew-Isolated) | 166,180 |
| Candidate pool | 2,330,779 |
| CiteRoots-Rhetoric paper-level positive labels (CiteNew slice) | 5,702 |
| CiteRoots-Rhetoric paper-level positive labels (CiteNew-Iso slice) | 4,483 |
| CiteRoots-Rhetoric human-gold audit contexts | ~1,200 |
| CiteRoots-Endorsement author-attested pairs | 1,518 |
| CiteRoots-Endorsement context-linked subset | 435 |
| CiteRoots-Endorsement retrieval-evaluable subset | 402 |
| CiteRoots-Endorsement focal papers | 753 |

### Does the dataset contain all possible instances or is it a sample?

The candidate pool is a fixed time-safe, text-readiness-filtered slice of the upstream S2ORC release. The release pool of 2,330,779 papers is smaller than the upstream time-safe S2ORC substrate (81.6 M papers globally; 18.2 M text-ready), but it is reused unchanged for every broad-tier, rhetorical, and author-endorsed retrieval result reported in the paper, so difficulty differences reflect target tightening rather than changes in the candidate universe.

### What data does each instance consist of?

The released artifacts contain only `corpusid` keys and identifier-derived fields that we ourselves computed (split assignment, tier membership, time-safety pass, text-readiness pass, our own primary-field classification, paper-level rhetorical role, author-confirmed endorsement audit status). They do not contain S2ORC text, abstracts, citation contexts, titles, years, venues, or author-name lists. Users must join with S2ORC by `corpusid` under the S2ORC license to obtain text or those metadata fields.

### Is there a label or target associated with each instance?

Yes. Targets are `corpusid` lists (CiteNext / CiteNew / CiteNew-Isolated), rhetoric-role binary labels, and endorsement-audit verdicts.

### Is any information missing from individual instances?

For privacy and consent reasons, we do not release: raw author-response narratives, author email addresses, free-text rationales, internal review logs.

For license-boundary reasons, we do not release: any S2ORC-owned content (text, abstracts, citation contexts, S2ORC's own metadata fields).

### Are relationships between individual instances made explicit?

Yes. MUSES instances reference a focal `corpusid`; targets reference candidate `corpusid`s; rhetorical and endorsement labels reference `(focal_corpusid, candidate_corpusid)` pairs. The `instance_splits.parquet`, `tier_targets/*.parquet`, `rhetoric_labels_paper_level.parquet`, and `endorsement_pairs.parquet` are joinable on `corpusid` and `authorid`.

### Are there recommended data splits?

Yes. The release ships author-disjoint career-midpoint splits. Authors with career midpoint before 2018 are in `train`, 2018–2020 in `val`, 2021–2023 in `test`. Splits are exposed in `instance_splits.parquet`. Author-disjointness is enforced at the split-construction step and verified at release time.

### Are there errors, sources of noise, or redundancies in the dataset?

Two known sources of noise are bounded by the release audit:

1. **Author disambiguation**: S2ORC author tables include some merge errors; we audit the headline cohort and report sensitivity bounds in Appendix A. The discovery-gap headline result is robust to this noise.
2. **Cohort selection on the endorsement layer**: the 753 focal papers and 1,518 author-attested pairs come from authors who responded to the workbench. A chi-square test on journal-family distribution detects no strong skew (*p* = 0.48 at current *n*), but responder-selection effects beyond field distribution cannot be ruled out at current *n*. We treat this as a known robustness item and document it in Appendix C.

### Is the dataset self-contained, or does it link to external resources?

The release is **deliberately not self-contained**. Text and abstracts must be obtained from S2ORC under its license; we ship only identifier-derived files we ourselves produced. This decision is documented and reflects the upstream S2ORC license terms (CC-BY-NC-SA-4.0) plus best practice for S2ORC-derivative releases (e.g., PreScience, BEIR-Sci, SciFact).

### Does the dataset contain data that might be considered confidential?

No. The release does not contain: raw author-response narratives, author email addresses, internal lab references, or any data that authors did not consent to redistribute. See `consent_protocol.md` for the workbench consent boundary.

### Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or otherwise cause anxiety?

Not to our knowledge. The released artifacts contain identifier keys, label categories, and aggregate statistics. They do not contain free-text content.

### Does the dataset relate to people?

Yes, indirectly. The MUSES task is conditioned on author identity (`authorid`). Author identity in our release surfaces only via `authorid`, which keys into S2ORC's public author tables. We do not redistribute author names or email addresses.

### Does the dataset identify any subpopulations?

The release exposes aggregate field-of-study distributions (Biology, Computer Science, Medicine, Engineering, Chemistry, etc.) for the candidate pool and the endorsement cohort. No demographic subpopulation labels are released.

### Is it possible to identify individuals from the dataset?

Yes, indirectly: an `authorid` keys into the public S2ORC author tables, where an author's name and publication list are publicly available under S2ORC's license. We do not add any new identifying information beyond what S2ORC already exposes.

### Does the dataset contain data that might be considered sensitive in any way?

Author-response data was collected with explicit consent for use in a research benchmark (see `consent_protocol.md`). We do not redistribute the raw responses; we redistribute only the structured pair-level outcomes after human review. Authors retained the right to opt out at any point during collection; opt-outs are excluded from the released cohort.

---

## 3. Collection process

### How was the data acquired?

The MUSES retrieval benchmark is derived deterministically from S2ORC by applying time-safety filters (publication-cutoff enforcement), text-readiness filters (parsed-PDF availability), and author-disjoint career-midpoint splits. The CiteRoots-Rhetoric labels are produced by a frontier LLM teacher (`gpt-5.4-mini` with the v6_literature prompt at medium reasoning effort), with a distilled Qwen3-8B + LoRA open companion released for scalable inference. The CiteRoots-Endorsement labels are produced by an author-response adjudication workbench: recent-paper authors are contacted with a focal paper of theirs and asked which prior works they regarded as generative inspirations; responses are then human-reviewed before entering the released cohort.

### Over what timeframe was the data collected?

Source S2ORC release: as licensed by Allen Institute (timestamp documented in `MAINTENANCE.md`). MUSES instance construction: 2026. Author outreach for CiteRoots-Endorsement: rolling collection 2026.

### Were any ethical review processes conducted?

The author-outreach protocol was reviewed for consent boundaries before launch. See `consent_protocol.md` for the exact protocol.

### Does the dataset relate to people?

See §2.

### Did the individuals in question consent to the collection and use of their data?

Yes. Authors contacted by the workbench were informed of: the research context, the intended use of their responses (research benchmark publication), the redistribution boundary (only structured pair-level outcomes, never raw text), and their right to opt out. Only consenting responses entered the released cohort.

### Was the data collected from the individuals in question directly, or obtained via a third party?

Directly, for CiteRoots-Endorsement. MUSES retrieval instances and CiteRoots-Rhetoric labels are derived from S2ORC, which was originally constructed by the Allen Institute for AI from the public scientific literature.

---

## 4. Preprocessing / cleaning / labeling

### Was any preprocessing/cleaning/labeling of the data done?

Yes. Preprocessing steps include:

1. **Time-safety filtering**: candidate-pool papers published after the relevant focal-paper cutoff are excluded. 0 of 44.7 M label rows violate the cutoff; this is verified at release time.
2. **Text-readiness filtering**: only papers whose S2ORC text was parsed cleanly enter the candidate pool.
3. **Author-disjoint splits**: career midpoints are computed per author and used to assign splits.
4. **Familiarity tiering**: CiteNew strips author-history-overlap citations; CiteNew-Isolated additionally strips coauthor-diffusion citations within a five-year window.
5. **Rhetorical labeling**: each benchmark-aligned citation context is labeled into one of six categories, then aggregated to paper-level binary labels under a precision-first rule.
6. **Endorsement adjudication**: author-response pairs are human-reviewed for review-paper status, self-citation conflicts, and consent before entering the released cohort.

### Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?

Internally yes (for our own audit purposes); externally no. The release ships only processed labels and identifier keys, not raw S2ORC payloads or raw author responses.

### Is the software used to preprocess/clean/label the instances available?

Yes. The released code repository contains the eval scripts, the MC-SPECTER2 inference reference, and the distilled judge inference script. Pipeline construction code is available in the repository under the same license (Apache 2.0).

---

## 5. Uses

### Has the dataset been used for any tasks already?

Yes — the experiments reported in the accompanying NeurIPS 2026 paper, including the headline retrieval leaderboard across 9 method classes, the rhetorical compression analysis (Finding 2), and the rhetorical-vs-endorsement separability analysis (Finding 3).

### Is there a repository that links to any or all papers or systems that use the dataset?

The code repository will list known users at `https://github.com/anon-muses-neurips/muses` (placeholder). At de-anonymization, we will start a "users of MUSES" page to track adoption.

### What (other) tasks could the dataset be used for?

- Comparative evaluation of retrieval methods on prospective scientific-literature tasks
- Studying the structure of citation graphs for inspiration vs. background separation
- Training paper-level endorsement classifiers
- Evaluating LLM-based scientific-text understanding
- Cohort-level analyses of how authors describe their own intellectual debts

### Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?

Yes. Three caveats:

1. The candidate pool is a time-safe, text-readiness-filtered slice of S2ORC; open-corpus retrieval is deferred and may change absolute K=1000 unsolved fractions while preserving the relative ordering of method classes.
2. The endorsement cohort is responder-conditioned; absolute endorsement-rate statistics may not generalize to non-responders.
3. The rhetorical layer uses a single canonical judge family (`gpt-5.4-mini`) plus its distilled student; cross-family judge robustness is documented in the paper as a known robustness item.

### Are there tasks for which the dataset should not be used?

The dataset should not be used to:

- Re-identify individual authors beyond what S2ORC already publicly exposes
- Generate adversarial citations targeting specific authors
- Train production systems that displace human peer review or research evaluation
- Make hiring, funding, or career-advancement decisions about individual researchers

---

## 6. Distribution

### Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?

Yes. The release is public under CC-BY-4.0 (derived labels) and Apache 2.0 (code) at the URLs documented in `RELEASE_INVENTORY.md`.

### How will the dataset be distributed?

Two HuggingFace dataset entities (`muses`, `citeroots`), one HuggingFace model entity (`citeroots-rhetoric-judge-qwen3-8b`), and one GitHub code repository, all under the placeholder organization `anon-muses-neurips`. URLs are anonymized at submission and de-anonymized at camera-ready.

### When will the dataset be distributed?

At the NeurIPS 2026 ED submission deadline (anonymized) and at de-anonymization (canonical URLs).

### Will the dataset be distributed under a copyright or other intellectual property (IP) license, and/or under applicable terms of use (ToU)?

- Derived labels: CC-BY-4.0
- Code: Apache 2.0
- Distilled judge weights: subject to the Qwen3 base license terms; LoRA adapters and inference scripts under Apache 2.0
- S2ORC content (NOT redistributed): remains under its original CC-BY-NC-SA-4.0 license; users must obtain it from the upstream S2ORC release

### Have any third parties imposed IP-based or other restrictions on the data associated with the instances?

S2ORC content is governed by its original CC-BY-NC-SA-4.0 license, which we do not modify and do not redistribute. Author-response data is governed by the consent boundary documented in `consent_protocol.md`.

### Do any export controls or other regulatory restrictions apply to the dataset?

No.

---

## 7. Maintenance

See `MAINTENANCE.md` for the canonical maintenance plan, versioning scheme, and contact protocol. Summary:

- **Maintainer**: anonymized at submission
- **Versioning**: SemVer; this release is `v1.0.0`
- **Update cadence**: minor patches as needed; major releases tied to expansions of the endorsement cohort or judge re-training
- **Erratum protocol**: documented in `MAINTENANCE.md`
- **Long-term hosting**: HuggingFace Hub for datasets and models; GitHub for code; archival mirrors as the release matures

---

## Appendix: cross-references

- `RELEASE_INVENTORY.md` — top-level artifact-to-claim map
- `consent_protocol.md` — workbench consent boundary
- `LICENSE.md` — license summary
- `MAINTENANCE.md` — maintenance and versioning
- `cards/muses.md`, `cards/citeroots.md` — per-subset HuggingFace dataset cards
- `muses/croissant.json`, `citeroots/croissant.json` — Croissant metadata with RAI fields
- Paper §3 (benchmark construction), §4 (experiments), Appendix A (S2ORC pipeline), Appendix B (CiteRoots-Rhetoric), Appendix C (CiteRoots-Endorsement)
