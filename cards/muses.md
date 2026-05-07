---
license: cc-by-4.0
language:
  - en
size_categories:
  - 1M<n<10M
task_categories:
  - text-retrieval
tags:
  - benchmark
  - prospective-citation-prediction
  - intellectual-roots-prediction
  - scientific-literature
  - retrieval
  - s2orc
pretty_name: MUSES — Prospective Intellectual-Roots Prediction Benchmark
configs:
  - config_name: default
    data_files:
      - split: train
        path: instance_splits.parquet
      - split: validation
        path: instance_splits.parquet
      - split: test
        path: instance_splits.parquet
---

# MUSES — Prospective Intellectual-Roots Prediction Benchmark

**MUSES** (Mining Unexplored Scientific Evidence to Spark novel hypothesis generation) is the first million-instance benchmark for prospective intellectual-roots prediction. Given an author's documented publication history at time *t*, the task is to rank a fixed pool of 2.33M scientific papers by how likely each one is to enter the author's next paper's bibliography.

The benchmark is hard along two orthogonal axes:

- **Familiarity**: CiteNext (any future citation) → CiteNew (excludes prior reading shadow) → CiteNew-Isolated (also excludes coauthor diffusion).
- **Functional**: any citation → rhetorical ROOT evidence → author endorsement (latter two layers shipped in the companion [`citeroots`](https://huggingface.co/datasets/anon-muses-neurips/citeroots) dataset).

## Dataset structure

| File | Schema | Size | Purpose |
|------|--------|------|---------|
| `instance_splits.parquet` | `(authorid, focal_corpusid, split)` | ~14 MB | Defines the 1.04M instances and their train/val/test assignment under author-disjoint career-midpoint splits |
| `tier_targets/citenext.parquet` | `(focal_corpusid, target_corpusid, is_influential)` | ~28 MB | CiteNext positive sets per focal paper |
| `tier_targets/citenew.parquet` | `(focal_corpusid, target_corpusid, is_influential)` | ~25 MB | CiteNew positive sets (excludes author-history overlap) |
| `tier_targets/citenew_iso.parquet` | `(focal_corpusid, target_corpusid, is_influential)` | ~22 MB | CiteNew-Isolated positive sets (also excludes coauthor diffusion) |
| `candidate_pool.parquet` | `(corpusid)` | ~30 MB | The fixed candidate universe: 2,330,779 corpusids |
| `candidate_pool_derived.parquet` | `(corpusid, time_safe, text_ready, primary_field_kd)` | ~50 MB | Our derived flags for the candidate pool |

## Counts

| Split | Count |
|-------|-------|
| Train | 687,624 |
| Validation | 182,543 |
| Test | 168,613 (CiteNext) / 167,568 (CiteNew) / 166,180 (CiteNew-Isolated) |

## Important: this dataset does NOT include S2ORC text

The release contains only `corpusid` keys and our derived flags. To use MUSES, you must obtain text and metadata from the upstream [S2ORC release](https://github.com/allenai/s2orc) under its CC-BY-NC-SA-4.0 license, joining via `corpusid`.

## Quick start

```python
from datasets import load_dataset
splits = load_dataset("anon-muses-neurips/muses")
test_citenext = splits["test"]  # 168,613 instances
```

To score a method, output a top-1000 ranked list of `corpusid`s per instance and run the eval script from the `code/` folder of this dataset repo:

```bash
python code/eval_test_full.py \
  --predictions my_method.predictions.parquet \
  --tier citenew \
  --splits muses/instance_splits.parquet \
  --targets muses/tier_targets/citenew.parquet
```

## Code, scripts, reproducibility

The `code/` folder of this dataset repo ships everything needed to reproduce paper claims:

- `code/verify.py` — runs all 22 paper-claim numerical checks against the released parquets (no compute needed; ~30 s).
- `code/mc_specter2_inference.py` — single-file MC-SPECTER2 retriever reference (no fine-tuning, no reranker, no LLM call).
- `code/judge_inference.py` — runs the [distilled rhetorical judge](https://huggingface.co/anon-muses-neurips/citeroots-rhetoric-judge-qwen3-8b).
- `code/eval_test_full.py` and `code/eval_test_full_citeroots.py` — broad-tier and rhetorical/endorsement scoring.
- `code/build_candidate_pool.py` — license-clean candidate-pool builder.

Top-level docs: `DATASHEET.md`, `LICENSE.md`, `MAINTENANCE.md`, `consent_protocol.md`, `RELEASE_INVENTORY.md`, `SHA256SUMS.txt`, and the [Croissant manifest](croissant.json) with full RAI metadata.

## Headline numbers (from the accompanying paper)

| Method | hit@100 (CiteNext) | hit@100 (CiteNew) | hit@100 (CiteNew-Isolated) |
|--------|--------:|---------:|---------:|
| MC-SPECTER2 (multi-centroid SPECTER2, K=16) | 0.534 | 0.424 | 0.366 |
| Single-centroid SPECTER2 | 0.447 | 0.347 | 0.296 |
| BM25 | 0.307 | 0.248 | 0.217 |
| BGE-large (off-the-shelf) | 0.409 | 0.321 | 0.278 |
| E5-large-v2 (off-the-shelf) | 0.401 | 0.310 | 0.266 |
| Popularity baseline | 0.017 | 0.011 | 0.004 |

47.8–50.0% of broad-tier test instances remain unsolved by every evaluated method at K=1000.

## Companion resource: CiteRoots

For the rhetorical and author-endorsed labeling layers, see the companion [`citeroots`](https://huggingface.co/datasets/anon-muses-neurips/citeroots) dataset and the [`citeroots-rhetoric-judge-qwen3-8b`](https://huggingface.co/anon-muses-neurips/citeroots-rhetoric-judge-qwen3-8b) model.

## License

The MUSES identifier files in this dataset are released under **CC-BY-4.0**. See [`LICENSE.md`](LICENSE.md) at the top of this dataset.

S2ORC content is **NOT** redistributed by MUSES; it remains under its original [CC-BY-NC-SA-4.0 license](https://github.com/allenai/s2orc#license-and-attribution).

## Citation

Anonymized for double-blind review. Will be filled in at de-anonymization.

## Maintenance

See [`MAINTENANCE.md`](MAINTENANCE.md) at the top of this dataset.

## Datasheet

A full Datasheet for Datasets (Gebru et al.) is available in [`DATASHEET.md`](DATASHEET.md) at the top of this dataset.
