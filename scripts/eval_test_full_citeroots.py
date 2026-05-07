#!/usr/bin/env python3
"""eval_test_full_citeroots.py — score predictions against the rhetorical CiteRoots slice.

Computes hit@10/50/100/1000 + MRR for one method on one rhetorical slice
(citeroots_new = CiteNew ∩ rhetorical-ROOT, or citeroots_iso = CiteNew-Isolated ∩ rhetorical-ROOT).

Resolves data files via local layout or HuggingFace Hub auto-download from
anon-muses-neurips/muses + anon-muses-neurips/citeroots.

Usage:
    python eval_test_full_citeroots.py --predictions my_method.parquet --slice citeroots_new
    python eval_test_full_citeroots.py --predictions my_method.parquet --slice citeroots_iso
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

MUSES_REPO     = "anon-muses-neurips/muses"
CITEROOTS_REPO = "anon-muses-neurips/citeroots"

SLICE_TIER = {
    "citeroots_new": ("citenew",      "tier_targets/citenew.parquet"),
    "citeroots_iso": ("citenew_iso",  "tier_targets/citenew_iso.parquet"),
}
SPLITS_FILE   = "instance_splits.parquet"
RHETORIC_FILE = "rhetoric_labels_paper_level.parquet"
KS = [10, 50, 100, 1000]


def find_or_download(repo, rel_path):
    here = Path(__file__).resolve().parent
    suffix = rel_path.split("/", 1)[1] if "/" in rel_path else rel_path
    repo_dir = repo.split("/")[-1]
    candidates = [
        here.parent / repo_dir / rel_path,
        here.parent / rel_path,
        here.parent / suffix,
        here.parent.parent / repo_dir / rel_path,
        here.parent.parent / rel_path,
    ]
    for p in candidates:
        if p.exists():
            return p
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        sys.exit("Missing files locally; pip install huggingface_hub")
    return Path(hf_hub_download(repo, rel_path, repo_type="dataset"))


def load_predictions(path):
    df = pd.read_parquet(path)
    df["focal_corpusid"] = df["focal_corpusid"].astype("int64")
    df["candidate_corpusid"] = df["candidate_corpusid"].astype("int64")
    if "rank" not in df.columns:
        if "score" not in df.columns:
            sys.exit("predictions parquet needs `rank` or `score` column")
        df = df.sort_values(["focal_corpusid", "score"], ascending=[True, False])
        df["rank"] = df.groupby("focal_corpusid").cumcount()
    return df[["focal_corpusid", "candidate_corpusid", "rank"]]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--slice", required=True, choices=list(SLICE_TIER.keys()))
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    args = ap.parse_args()

    tier_label, tier_path = SLICE_TIER[args.slice]

    print(f"[1/5] Loading splits + tier targets ({tier_label}) ...")
    splits = pd.read_parquet(find_or_download(MUSES_REPO, SPLITS_FILE))
    targets = pd.read_parquet(find_or_download(MUSES_REPO, tier_path))
    targets = targets.rename(columns={"target_corpusid": "candidate_corpusid"})
    targets["focal_corpusid"]     = targets["focal_corpusid"].astype("int64")
    targets["candidate_corpusid"] = targets["candidate_corpusid"].astype("int64")

    print(f"[2/5] Loading rhetoric labels ...")
    rh = pd.read_parquet(find_or_download(CITEROOTS_REPO, RHETORIC_FILE))
    rh["focal_corpusid"]     = rh["focal_corpusid"].astype("int64")
    rh["candidate_corpusid"] = rh["candidate_corpusid"].astype("int64")
    rh_root = rh[rh["root_label"] == 1][["focal_corpusid", "candidate_corpusid"]]

    print(f"[3/5] Building rhetorical slice ...")
    eval_focals = set(splits[splits["split"] == args.split]["focal_corpusid"].astype("int64"))
    targets = targets[targets["focal_corpusid"].isin(eval_focals)]
    sliced = targets.merge(rh_root, on=["focal_corpusid", "candidate_corpusid"], how="inner")
    n_pos = len(sliced)
    n_focals = sliced["focal_corpusid"].nunique()
    print(f"  {args.slice} ({tier_label}): {n_pos:,} positive pairs across {n_focals:,} focal papers")

    print(f"[4/5] Loading predictions ...")
    preds = load_predictions(args.predictions)
    print(f"  {len(preds):,} prediction rows × {preds['focal_corpusid'].nunique():,} focals")

    print(f"[5/5] Scoring ...")
    pos = set(zip(sliced["focal_corpusid"], sliced["candidate_corpusid"]))
    p = preds.copy()
    p["is_hit"] = pd.Series(list(zip(p["focal_corpusid"], p["candidate_corpusid"]))).isin(pos).values

    metrics = {}
    for k in KS:
        topk = p[p["rank"] < k]
        hit_pairs = set(zip(topk[topk["is_hit"]]["focal_corpusid"],
                            topk[topk["is_hit"]]["candidate_corpusid"]))
        metrics[f"hit@{k}"] = len(hit_pairs) / len(pos) if pos else 0.0

    p_hit = p[p["is_hit"]]
    if len(p_hit) > 0:
        first_hit = p_hit.groupby(["focal_corpusid", "candidate_corpusid"])["rank"].min().reset_index()
        all_pos = pd.DataFrame(list(pos), columns=["focal_corpusid", "candidate_corpusid"])
        merged = all_pos.merge(first_hit, on=["focal_corpusid", "candidate_corpusid"], how="left")
        merged["rr"] = (1.0 / (merged["rank"] + 1)).fillna(0.0)
        metrics["mrr"] = merged["rr"].mean()
    else:
        metrics["mrr"] = 0.0

    metrics["n_focals"] = n_focals
    metrics["n_positives"] = n_pos

    print(f"\nResults:")
    for k, v in metrics.items():
        print(f"  {k:<14} {v:.4f}" if isinstance(v, float) else f"  {k:<14} {v:,}")
    return metrics


if __name__ == "__main__":
    main()
