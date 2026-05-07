---
license: cc-by-4.0
language:
  - en
size_categories:
  - 10K<n<100K
task_categories:
  - text-classification
  - text-retrieval
tags:
  - citation-intent
  - rhetorical-roles
  - author-endorsement
  - inspiration
  - scientific-literature
  - benchmark
pretty_name: CiteRoots — Two-Layer Inspiration Measurement Framework
---

# CiteRoots — Two-Layer Inspiration Measurement Framework

**CiteRoots** is a two-layer measurement framework that complements the [MUSES](https://huggingface.co/datasets/anon-muses-neurips/muses) prospective retrieval benchmark by tightening "any future citation" toward citations that play generative roles in local text and citations the citing-paper authors themselves identify as intellectual roots.

CiteRoots is independently usable: any benchmark or analysis that operates over S2ORC paper-pair edges can join with these labels to add a rhetorical or author-endorsement axis.

## The two layers

### CiteRoots-Rhetoric (passage-level → paper-level aggregated)

Local rhetorical role of a citation context, classified into one of six categories grouped into a generative ROOT union (TF / ME / GM) and a non-generative WEED union (CC / TR / BC). Aggregated to paper-level binary labels under a precision-first rule (positive iff at least one linked context is judged ROOT).

- **Validation**: LLM teacher (`gpt-5.4-mini`) reaches Cohen's κ = **0.896** vs. ~1,200 human-gold contexts (binary ROOT/non-ROOT).
- **Open companion**: a distilled Qwen3-8B + LoRA student reaches κ = **0.771** vs. teacher; released as the [`citeroots-rhetoric-judge-qwen3-8b`](https://huggingface.co/anon-muses-neurips/citeroots-rhetoric-judge-qwen3-8b) model.

### CiteRoots-Endorsement (paper-level)

Author-attested generative-inspiration pairs collected through an author-response adjudication workbench. **1,518 author-attested pairs from 753 focal papers**, of which 435 are context-linked back to explicit focal-paper bibliography evidence and 402 are evaluable as retrieval targets within the released MUSES pool.

- **Empirical separability**: the same `gpt-5.4-mini` family reaches κ = 0.896 on rhetorical-role classification but only κ = **0.037** on author-endorsement on the same audit pairs — paper-level intellectual debt is not recoverable from local citation rhetoric alone.

## Files

| File | Rows | Size | Purpose |
|------|-----:|-----:|---------|
| `rhetoric_labels_paper_level.parquet` | 397,718 | 4.9 MB | Paper-level ROOT/non-ROOT labels for benchmark-aligned focal→cited edges. Cols: `focal_corpusid, candidate_corpusid, n_mentions, n_root_mentions, max_root_prob, root_label`. |
| `human_gold_audit.parquet` | 1,202 | 63 KB | Canonical human-gold audit set with both LLM teacher (`llm_label`, `llm_subtype`) and human (`human_label`) annotations. Reproduces κ=0.896. |
| `endorsement_pairs.parquet` | 1,136 | 100 KB | Release-ready author-attested pairs with novelty-axis flags (`is_in_reading_shadow`, `is_citenew_endorsement`, `is_retrieval_evaluable`, `is_context_linked`, etc.). |
| `paper_time_endorsement_positives.parquet` | 1,049 | 53 KB | Paper-time positives cohort that supports the headline 402 / 145 / 257 / 0.171 / 0.393 numbers. See `endorsement_subsets.json`. |
| `predictions/mc_specter2_K16_paper_time.parquet` | 134,000 | 1.8 MB | Paper-time MC-SPECTER2 (K=16) predictions over the 134-focal cohort. Lets reviewers reproduce h@100 = 0.171 / 0.393 without re-running inference. |
| `endorsement_subsets.json` | manifest | 2.8 KB | Defines the 1,518 / 1,136 / 435 / 402 / 145 / 257 / 34 funnel and the paper-time vs canonical-release distinction. |
| `cohort_characterization.parquet` | 35 | 3 KB | Aggregate cohort statistics (field/year/journal distribution for the 753 focal papers). No PII. |
| `taxonomy_v7_0.yml` | — | 33 KB | Six-category v7.0 CiteRoots taxonomy (TF/ME/GM/CC/TR/BC + ROOT/WEED grouping). |
| `prompt_v6_literature.txt` | — | 6 KB | Verbatim canonical teacher prompt (`gpt-5.4-mini` + v6_literature). |

## Important: this dataset does NOT include raw author narratives or S2ORC text

CiteRoots redistributes only the structured outcomes of the rhetorical and endorsement workflows. Free-text author rationales, raw author responses, citation-context windows, and S2ORC text are **not** redistributed. Raw S2ORC content must be obtained from the upstream [S2ORC release](https://github.com/allenai/s2orc) under its CC-BY-NC-SA-4.0 license. Author-response data is governed by the consent boundary documented in `consent_protocol.md` (in the [MUSES dataset repo](https://huggingface.co/datasets/anon-muses-neurips/muses)).

## Quick start

```python
import pandas as pd
from huggingface_hub import hf_hub_download

# Rhetorical layer (paper-level)
rhetoric = pd.read_parquet(hf_hub_download(
    "anon-muses-neurips/citeroots", "rhetoric_labels_paper_level.parquet", repo_type="dataset"))

# Author-endorsed layer (release-ready cohort)
endorsement = pd.read_parquet(hf_hub_download(
    "anon-muses-neurips/citeroots", "endorsement_pairs.parquet", repo_type="dataset"))

# Human gold audit (n=1,202; reproduces κ=0.896)
gold = pd.read_parquet(hf_hub_download(
    "anon-muses-neurips/citeroots", "human_gold_audit.parquet", repo_type="dataset"))
```

To reproduce all 22 paper-claim numerical checks at once, run
[`code/verify.py`](https://huggingface.co/datasets/anon-muses-neurips/muses/blob/main/code/verify.py)
in the companion MUSES dataset repo. To run the open distilled judge on your own citation contexts, see the
[`citeroots-rhetoric-judge-qwen3-8b`](https://huggingface.co/anon-muses-neurips/citeroots-rhetoric-judge-qwen3-8b)
model card.

## Companion resource: MUSES

For the prospective retrieval benchmark, see the companion [`muses`](https://huggingface.co/datasets/anon-muses-neurips/muses) dataset.

## License

CiteRoots is released under **CC-BY-4.0**. See `LICENSE.md` in the [MUSES dataset repo](https://huggingface.co/datasets/anon-muses-neurips/muses).

The companion distilled judge weights are subject to the Qwen3 base license terms; our LoRA adapters and inference scripts are Apache 2.0.

## Citation

Anonymized for double-blind review. Will be filled in at de-anonymization.

## Datasheet

A full Datasheet for Datasets is available in `DATASHEET.md` in the [MUSES dataset repo](https://huggingface.co/datasets/anon-muses-neurips/muses).

## Consent boundary

The CiteRoots-Endorsement layer was collected under explicit author consent. See `consent_protocol.md` in the [MUSES dataset repo](https://huggingface.co/datasets/anon-muses-neurips/muses) for the full protocol and what is and is not redistributed.
