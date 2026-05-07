# License Summary

This release contains four classes of artifact, each governed by its own license. Read carefully — the license terms differ across artifact classes.

## At a glance

| Artifact class | License | Notes |
|----------------|---------|-------|
| Derived labels (MUSES + CiteRoots parquets, JSONs, manifests) | **CC-BY-4.0** | Attribution required; permits commercial use |
| Code (eval scripts, inference references, build scripts) | **Apache 2.0** | Standard open-source license |
| Distilled judge weights (Qwen3-8B + LoRA adapters) | Subject to **Qwen3 base license terms** | LoRA adapters and inference scripts: Apache 2.0 |
| S2ORC content | NOT redistributed | Remains under its CC-BY-NC-SA-4.0 license; obtain from upstream |

## Derived labels — CC-BY-4.0

All `*.parquet`, `*.json`, `*.tsv`, and label-manifest files in the release are licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC-BY-4.0).

This applies specifically to:
- `instance_splits.parquet`
- `tier_targets/*.parquet`
- `candidate_pool.parquet`
- `candidate_pool_derived.parquet`
- `rhetoric_labels_paper_level.parquet`
- `human_gold_audit.parquet`
- `endorsement_pairs.parquet`
- `endorsement_subsets.json`
- `cohort_characterization.parquet`
- `taxonomy_v7_0.yml`
- `prompt_v6_literature.txt`

You are free to: **share** (copy and redistribute the material in any medium or format) and **adapt** (remix, transform, and build upon the material) for any purpose, even commercially.

You must: give appropriate **attribution**, provide a link to the license, and indicate if changes were made.

## Code — Apache 2.0

All `*.py`, `*.sh`, and other source-code files in the release are licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

This applies specifically to:
- `eval_test_full.py`
- `eval_test_full_citeroots.py`
- `mc_specter2_inference.py`
- `judge_inference.py`
- `build_candidate_pool.py`
- All other scripts in the code repository

The Apache 2.0 license includes a patent-grant clause and a notice-preservation clause. Read the license text for full terms.

## Distilled judge weights — Qwen3 base license + Apache 2.0 for our adapters

The released distilled rhetorical judge consists of two layers:

1. **Base weights**: the underlying Qwen3-8B model is *not* redistributed by us; users who load the released LoRA adapters will fetch the Qwen3-8B base separately from its canonical source under the Qwen3 license terms. Refer to the Qwen3 license at the time of download for current terms.
2. **LoRA adapters + tokenizer config + inference script**: our additions are licensed under Apache 2.0. The adapters were trained on teacher-labeled citation contexts that we ourselves produced; the resulting weights are our derivative work.

This split-license posture means: anyone who can use Qwen3-8B can use our distilled judge.

## S2ORC content — NOT redistributed

We do **not** redistribute any S2ORC-owned content. The 2,330,779-paper candidate pool is referenced by `corpusid` only; users who want text, abstracts, citation contexts, titles, years, venues, or author lists must obtain them from the upstream S2ORC release at [https://github.com/allenai/s2orc](https://github.com/allenai/s2orc) under the Allen Institute's CC-BY-NC-SA-4.0 license terms.

This split is deliberate and reflects best practice for S2ORC-derivative releases. The MUSES release does not modify, mirror, or otherwise redistribute S2ORC's licensed content.

## Author-response narratives — NOT redistributed

We do **not** redistribute the raw free-text responses authors provided to the workbench. We redistribute only the structured pair-level outcomes after human review, as documented in `consent_protocol.md`. This is a consent boundary, not a license boundary.

## Attribution

When using MUSES or CiteRoots artifacts, please cite the accompanying paper. The citation entry will be filled in at de-anonymization. A `CITATION.cff` file will be added to the code repository.

## Trademark

"MUSES" and "CiteRoots" are used here as the names of the released benchmark and labeling resource respectively; no trademark is claimed.

## Disclaimer

The released artifacts are provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from, out of, or in connection with the artifacts or the use or other dealings in them.
