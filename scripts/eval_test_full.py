#!/usr/bin/env python3
"""eval_test_full.py — score a method's predictions against MUSES broad tiers.

Computes hit@10/50/100/1000 + MRR for one method × one familiarity tier.
Resolves data files via local layout or HuggingFace Hub auto-download.

Usage:
    python eval_test_full.py --predictions my_method.parquet --tier citenew

Predictions parquet schema (must contain at minimum):
    focal_corpusid : int64
    candidate_corpusid : int64
    rank : int  (rank 0 = top-1; lower is better)
or
    focal_corpusid, candidate_corpusid, score (descending)
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

MUSES_REPO = "anon-muses-neurips/muses"

TIER_FILES = {
    "citenext":     "tier_targets/citenext.parquet",
    "citenew":      "tier_targets/citenew.parquet",
    "citenew_iso":  "tier_targets/citenew_iso.parquet",
}
SPLITS_FILE = "instance_splits.parquet"
KS = [10, 50, 100, 1000]


def find_or_download(rel_path):
    """Try local layouts first; fall back to HF Hub download."""
    here = Path(__file__).resolve().parent
    candidates = [here.parent / rel_path, here.parent / "muses" / rel_path,
                  here.parent.parent / rel_path,
                  here.parent.parent / "muses" / rel_path]
    for p in candidates:
        if p.exists():
            return p
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        sys.exit("Missing files locally and `huggingface_hub` not installed. "
                 "Run: pip install huggingface_hub")
    return Path(hf_hub_download(MUSES_REPO, rel_path, repo_type="dataset"))


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
    ap.add_argument("--tier", required=True, choices=list(TIER_FILES.keys()))
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    args = ap.parse_args()

    print(f"[1/4] Loading splits + {args.tier} targets ...")
    splits = pd.read_parquet(find_or_download(SPLITS_FILE))
    targets = pd.read_parquet(find_or_download(TIER_FILES[args.tier]))
    targets["focal_corpusid"] = targets["focal_corpusid"].astype("int64")
    targets["target_corpusid"] = targets["target_corpusid"].astype("int64")

    eval_focals = set(splits[splits["split"] == args.split]["focal_corpusid"].astype("int64"))
    targets = targets[targets["focal_corpusid"].isin(eval_focals)]
    print(f"  {args.tier} {args.split}: {len(eval_focals):,} focals, {len(targets):,} positives")

    print(f"[2/4] Loading predictions ...")
    preds = load_predictions(args.predictions)
    print(f"  {len(preds):,} rows × {preds['focal_corpusid'].nunique():,} focals")

    print(f"[3/4] Scoring ...")
    pos = set(zip(targets["focal_corpusid"], targets["target_corpusid"]))
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

    metrics["n_focals"] = len(eval_focals)
    metrics["n_positives"] = len(pos)

    print(f"[4/4] Results:")
    for k, v in metrics.items():
        print(f"  {k:<14} {v:.4f}" if isinstance(v, float) else f"  {k:<14} {v:,}")
    return metrics


if __name__ == "__main__":
    main()
