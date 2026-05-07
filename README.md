# MUSES + CiteRoots — Code Repository

Code for the NeurIPS 2026 Evaluations & Datasets submission. The dataset parquets live at:

- **MUSES dataset**: https://huggingface.co/datasets/anon-muses-neurips/muses
- **CiteRoots dataset**: https://huggingface.co/datasets/anon-muses-neurips/citeroots
- **Distilled judge model**: https://huggingface.co/anon-muses-neurips/citeroots-rhetoric-judge-qwen3-8b

## Quick start — reproduce all 22 paper claims

```bash
pip install pandas pyarrow huggingface_hub
python scripts/verify.py
```

The script auto-downloads the required parquets from the HuggingFace datasets above and runs every numerical check from the paper (counts, kappas, hit@K). No model inference required; ~30 seconds.

## Score your own method

```bash
# Score against a broad familiarity tier (citenext / citenew / citenew_iso)
python scripts/eval_test_full.py --predictions my_method.parquet --tier citenew

# Score against a rhetorical CiteRoots slice
python scripts/eval_test_full_citeroots.py --predictions my_method.parquet --slice citeroots_new
```

Predictions parquet schema: `focal_corpusid (int64), candidate_corpusid (int64), rank (int)`.

## What's in this repo

- `scripts/` — eval + inference + verify scripts (Apache 2.0)
- `cards/` — HuggingFace dataset cards (reference; live on HF)
- `croissant/` — Croissant 1.0 manifests with full RAI metadata
- `DATASHEET.md` — Gebru-style 7-section datasheet
- `LICENSE.md`, `MAINTENANCE.md`, `consent_protocol.md`, `RELEASE_INVENTORY.md`, `SHA256SUMS.txt`

## Anonymization

Submitted under double-blind review for NeurIPS 2026 Evaluations & Datasets track. URLs and identifiers use the placeholder organization `anon-muses-neurips`. Real org and citation will be filled in at de-anonymization.

## License

- Code: Apache 2.0
- Dataset labels (separate HF entities): CC-BY-4.0
- Distilled judge LoRA adapters: Apache 2.0; Qwen3-8B base: subject to upstream license
