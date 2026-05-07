# MUSES Release Inventory

This document is the entry point to the MUSES release for the NeurIPS 2026 Evaluations & Datasets track. It maps every released artifact to the paper claim it supports.

## Release posture

The release follows the **PreScience-aligned minimum**: we release only what we ourselves derived. We do **not** redistribute S2ORC-owned content (text, abstracts, citation contexts, paper metadata) or raw author-response narratives. Reviewers join with S2ORC themselves under the S2ORC license, using the `corpusid` keys we provide.

## What is released

The release is split into two HuggingFace dataset entities and one HuggingFace model entity, all under the anonymized organization placeholder `anon-muses-neurips`:

| Entity | URL (placeholder) | Contains |
|--------|-------------------|----------|
| `muses` (dataset) | `https://huggingface.co/datasets/anon-muses-neurips/muses` | Benchmark identifier files: instance splits, tier targets, candidate-pool corpusids, our derived pool flags |
| `citeroots` (dataset) | `https://huggingface.co/datasets/anon-muses-neurips/citeroots` | Two label layers: rhetoric paper-level labels, human-gold audit, endorsement pairs and subsets |
| `citeroots-rhetoric-judge-qwen3-8b` (model) | `https://huggingface.co/anon-muses-neurips/citeroots-rhetoric-judge-qwen3-8b` | Distilled rhetorical judge: Qwen3-8B base + LoRA adapters + inference reference |
| Code repository | `https://github.com/anon-muses-neurips/muses` | Eval scripts, MC-SPECTER2 inference reference, datasheet, license, maintenance, croissant manifests |

## Artifact-to-claim map

| # | Artifact | Hosted in | Paper claim it backs |
|---|----------|-----------|----------------------|
| 1 | `taxonomy_v7_0.yml` | `citeroots-rhetoric-judge-qwen3-8b` model card + code repo | §3.3.1, Appendix B (taxonomy) |
| 1 | `prompt_v6_literature.txt` (verbatim teacher prompt) | `citeroots-rhetoric-judge-qwen3-8b` model card | §3.3.1, Appendix B.3 (judge prompt) |
| 1 | `qwen3_8b_distilled_judge/` (LoRA adapters + tokenizer + config) | `citeroots-rhetoric-judge-qwen3-8b` (HF model) | §1 contribution 4 ($\kappa = 0.771$ vs. teacher); Appendix B.5 |
| 1 | `judge_inference.py` (single-file reference) | code repo | §1 contribution 4 (open-companion reproducibility) |
| 2 | `endorsement_pairs.parquet` (1,518 author-attested pairs) | `citeroots` dataset | §1 contribution 2; §3.3.2; §4.4; abstract |
| 2 | `endorsement_subsets.json` (435 context-linked, 402 retrieval-evaluable manifests) | `citeroots` dataset | §3.3.2 |
| 2 | `cohort_characterization.parquet` (aggregate field/year stats; no PII) | `citeroots` dataset | Appendix C |
| 2 | `consent_protocol.md` | code repo | NeurIPS RAI; reviewer transparency |
| 3 | `rhetoric_labels_paper_level.parquet` (one row per benchmark-aligned focal→cited pair: ROOT / non-ROOT) | `citeroots` dataset | §1 contribution 2; §3.3.1; §4.3 (Finding 2) |
| 3 | `human_gold_audit.parquet` (~1,200 context-level human-gold labels) | `citeroots` dataset | §3.3.1 ($\kappa = 0.896$ teacher-vs-human) |
| 4 | `instance_splits.parquet` (1.04M instances; train/val/test) | `muses` dataset | §1 contribution 1; §3.2 |
| 4 | `tier_targets/{citenext,citenew,citenew_iso}.parquet` (positive sets per tier) | `muses` dataset | §4 (every retrieval result) |
| 4 | `candidate_pool.parquet` (corpusid only, 2.33M rows) | `muses` dataset | §3.2 candidate universe |
| 4 | `candidate_pool_derived.parquet` (corpusid + our derived flags: time_safe, text_ready, primary_field_kd) | `muses` dataset | §3.2 candidate-pool construction |
| 5 | `eval_test_full.py` | code repo | §4 broad-tier scoring |
| 5 | `eval_test_full_citeroots.py` | code repo | §4 rhetorical and endorsement scoring |
| 5 | `mc_specter2_inference.py` | code repo | §4 headline-retriever reference; §1 contribution 3 |
| 6 | `croissant.json` (per dataset entity) | each dataset entity | NeurIPS 2026 ED submission requirement |
| 7 | `DATASHEET.md` | code repo + each dataset card | NeurIPS reproducibility checklist |
| 7 | `LICENSE.md` | code repo + each dataset card | Distribution boundary |
| 7 | `MAINTENANCE.md` | code repo | NeurIPS ED hosting guidelines |
| 7 | `RELEASE_INVENTORY.md` | code repo + each dataset card | Top-level entry point (this file) |
| 7 | per-subset `CARD.md` | each dataset entity | HF Hub convention |

## What is NOT released

These exclusions are deliberate; do not file issues asking for them:

- **S2ORC-owned content**: paper text, abstracts, citation contexts, parsed PDFs, S2ORC's own field tags, titles, years, venues, author lists. Obtain these from the [S2ORC release](https://github.com/allenai/s2orc) under its CC-BY-NC-SA-4.0 license, joining via `corpusid`.
- **Raw author-response narratives** from the workbench. Authors did not consent to redistribution of their free-text responses; we release only structured pair-level outcomes after human review.
- **Author names, emails, ORCIDs** beyond what is already public via the S2ORC author tables. Author identity in our release is exposed only via `authorid`.
- **Workbench internal logs** and intermediate distillation checkpoints.
- **Per-method prediction parquets** at submission time (deferred to camera-ready). The released eval scripts plus the released model are sufficient for reviewers to reproduce headline numbers; per-method predictions will land at de-anonymization to support spot-checks.
- **Context-level rhetoric labels** at submission time (paper-level aggregated only). Context-level labels can be regenerated by running the released distilled judge over a user's S2ORC join, and will be staged at de-anonymization.

## Reproducing the headline numbers

A reviewer who wants to reproduce the §4 leaderboard can do so as follows:

1. Download S2ORC under its license; join `candidate_pool.parquet` with S2ORC by `corpusid` to obtain text/metadata.
2. Run `mc_specter2_inference.py` to produce headline predictions for the 9 method classes (or any subset; the script also accepts user-supplied prediction parquets).
3. Run `eval_test_full.py --tier {citenext,citenew,citenew_iso}` to score against `tier_targets/`.
4. Run `eval_test_full_citeroots.py` to score against the rhetorical and endorsement slices.

Expected wall-clock: roughly 12–30 hours on a single A100, dominated by candidate-pool encoding (one-time).

## Versioning

This release is `v1.0.0`. See `MAINTENANCE.md` for the versioning scheme and update protocol.

## License

- Derived labels (MUSES + CiteRoots): **CC-BY-4.0**
- Code: **Apache 2.0**
- Distilled judge weights: subject to Qwen3 base license terms; LoRA adapters and inference scripts: **Apache 2.0**

See `LICENSE.md`.

## Citation

Anonymized at submission. Will be filled in at de-anonymization.

## Contact

Anonymized at submission. See `MAINTENANCE.md` for the post-submission contact protocol.
