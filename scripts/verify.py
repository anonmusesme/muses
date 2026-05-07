#!/usr/bin/env python3
"""verify.py — reproducibility walkthrough for the MUSES + CiteRoots release.

Reproduces every numerical claim in the paper from the released parquets alone.
No external joins, no model inference required.

Auto-detects the file layout. Works in three contexts:
  (a) Local clone of the release/ directory:  python release/scripts/verify.py
  (b) Inside the muses HF dataset clone:      python code/verify.py
  (c) Standalone:                              python verify.py
      (downloads files on demand from huggingface.co/datasets/anon-muses-neurips/{muses,citeroots})
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

MUSES_REPO     = "anon-muses-neurips/muses"
CITEROOTS_REPO = "anon-muses-neurips/citeroots"

# Logical name → (HF repo, path-within-HF-repo, path-within-local-release-tree)
FILES = {
    "instance_splits":   (MUSES_REPO,     "instance_splits.parquet",                          "muses/instance_splits.parquet"),
    "candidate_pool":    (MUSES_REPO,     "candidate_pool.parquet",                           "muses/candidate_pool.parquet"),
    "tier_citenext":     (MUSES_REPO,     "tier_targets/citenext.parquet",                    "muses/tier_targets/citenext.parquet"),
    "tier_citenew":      (MUSES_REPO,     "tier_targets/citenew.parquet",                     "muses/tier_targets/citenew.parquet"),
    "tier_citenew_iso":  (MUSES_REPO,     "tier_targets/citenew_iso.parquet",                 "muses/tier_targets/citenew_iso.parquet"),
    "rhetoric":          (CITEROOTS_REPO, "rhetoric_labels_paper_level.parquet",              "citeroots/rhetoric_labels_paper_level.parquet"),
    "human_gold":        (CITEROOTS_REPO, "human_gold_audit.parquet",                         "citeroots/human_gold_audit.parquet"),
    "endorse":           (CITEROOTS_REPO, "endorsement_pairs.parquet",                        "citeroots/endorsement_pairs.parquet"),
    "paper_time_pos":    (CITEROOTS_REPO, "paper_time_endorsement_positives.parquet",         "citeroots/paper_time_endorsement_positives.parquet"),
    "predictions":       (CITEROOTS_REPO, "predictions/mc_specter2_K16_paper_time.parquet",   "citeroots/predictions/mc_specter2_K16_paper_time.parquet"),
}


def resolve(local_root):
    """Return {logical_name: Path}. Try local layout first, then download from HF."""
    here = Path(__file__).resolve().parent

    # Local layout candidates: --local override, then release/ above scripts/, then HF-flat
    base_candidates = []
    if local_root:
        base_candidates.append(Path(local_root).resolve())
    base_candidates += [here.parent, here.parent.parent]

    paths = {}
    missing = []
    for key, (repo, hf_path, local_path) in FILES.items():
        found = None
        for base in base_candidates:
            for try_path in (base / local_path,                              # release/muses/file
                             base / local_path.split("/", 1)[1]):            # HF-flat: file at repo root
                if try_path.exists():
                    found = try_path
                    break
            if found:
                break
        paths[key] = found
        if not found:
            missing.append(key)

    if missing:
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            print("ERROR: missing files locally and `huggingface_hub` not installed.", file=sys.stderr)
            print("       pip install huggingface_hub  OR  rerun with --local <path-to-release-tree>", file=sys.stderr)
            sys.exit(1)
        print(f"\nDownloading {len(missing)} missing files from HuggingFace Hub...")
        for k in missing:
            repo, hf_path, _ = FILES[k]
            paths[k] = Path(hf_hub_download(repo, hf_path, repo_type="dataset"))
            print(f"  {k:<22} {repo}/{hf_path}")
    return paths


def kappa_binary(y1, y2):
    cm = pd.crosstab(y1, y2)
    n = cm.values.sum()
    p_o = cm.values.diagonal().sum() / n
    rs = cm.values.sum(axis=1)
    cs = cm.values.sum(axis=0)
    p_e = sum((rs[i] * cs[i]) / (n * n) for i in range(min(len(rs), len(cs))))
    return (p_o - p_e) / (1 - p_e)


def check(name, claim, actual, tol=0.001):
    if isinstance(claim, (int, float)) and isinstance(actual, (int, float)):
        ok = abs(claim - actual) < tol if isinstance(claim, float) else (claim == actual)
    else:
        ok = (claim == actual)
    flag = "[OK]   " if ok else "[FAIL] "
    print(f"  {flag} {name}: paper={claim}, computed={actual}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default=None,
                    help="Path to a local release tree containing muses/ and citeroots/. "
                         "Auto-detects if omitted; downloads missing files from HF Hub as a fallback.")
    args = ap.parse_args()

    paths = resolve(args.local)

    splits     = pd.read_parquet(paths["instance_splits"])
    pool       = pd.read_parquet(paths["candidate_pool"])
    rh         = pd.read_parquet(paths["rhetoric"])
    gold       = pd.read_parquet(paths["human_gold"])
    endorse    = pd.read_parquet(paths["endorse"])
    paper_pos  = pd.read_parquet(paths["paper_time_pos"])
    preds      = pd.read_parquet(paths["predictions"])

    print("\n" + "=" * 70)
    print("MUSES + CiteRoots — paper-claim reproducibility walkthrough")
    print("=" * 70)

    print("\n--- Section 1: Counts ---")
    check("Pool size",       2_330_779, len(pool))
    check("Total instances", 1_038_780, len(splits))
    check("Train",           687_624,   (splits["split"] == "train").sum())
    check("Val",             182_543,   (splits["split"] == "val").sum())
    check("Test",            168_613,   (splits["split"] == "test").sum())

    test_focals = set(splits[splits["split"] == "test"]["focal_corpusid"])
    for tier_key, tier_label, n_expected in [
        ("tier_citenext",     "citenext",     168_613),
        ("tier_citenew",      "citenew",      167_568),
        ("tier_citenew_iso",  "citenew_iso",  166_180),
    ]:
        df_t = pd.read_parquet(paths[tier_key], columns=["focal_corpusid"])
        n = df_t[df_t["focal_corpusid"].isin(test_focals)]["focal_corpusid"].nunique()
        check(f"Test tier {tier_label}", n_expected, n)

    df_next = pd.read_parquet(paths["tier_citenext"])
    df_new  = pd.read_parquet(paths["tier_citenew"])
    df_iso  = pd.read_parquet(paths["tier_citenew_iso"])
    ks_next = set(zip(df_next.focal_corpusid, df_next.target_corpusid))
    ks_new  = set(zip(df_new.focal_corpusid,  df_new.target_corpusid))
    ks_iso  = set(zip(df_iso.focal_corpusid,  df_iso.target_corpusid))
    check("CiteNew ⊆ CiteNext",    True, ks_new.issubset(ks_next))
    check("CiteNew-Iso ⊆ CiteNew", True, ks_iso.issubset(ks_new))

    print("\n--- Section 2: CiteRoots-Rhetoric ---")
    check("Rhetoric pair count",   397_718, len(rh))
    check("Rhetoric ROOT count",   13_466,  (rh.root_label == 1).sum())
    check("Rhetoric ROOT rate",    0.0339,  (rh.root_label == 1).mean(), tol=0.0001)

    rh_root = rh[rh.root_label == 1].rename(columns={"candidate_corpusid": "target_corpusid"})
    for tier_key, tier_label, n_expected in [("tier_citenew", "citenew", 5_702),
                                              ("tier_citenew_iso", "citenew_iso", 4_483)]:
        df_t = pd.read_parquet(paths[tier_key])
        df_t = df_t[df_t["focal_corpusid"].isin(test_focals)]
        joined = rh_root.merge(df_t, on=["focal_corpusid", "target_corpusid"], how="inner")
        check(f"Test instances w/ ROOT in {tier_label}", n_expected, joined["focal_corpusid"].nunique())

    print("\n--- Section 3: κ values ---")
    ROOTS = {"TF", "ME", "GM"}
    gold["hr"] = gold["human_label"].apply(lambda x: "ROOT" if x in ROOTS else "WEED")
    gold["lr"] = gold["llm_subtype"].apply(lambda x: "ROOT" if x in ROOTS else "WEED")
    check("κ LLM vs human gold (n=1,202, binary)", 0.896, round(kappa_binary(gold["hr"], gold["lr"]), 3))
    check("κ LLM vs human gold (six-way)",         0.713, round(kappa_binary(gold["human_label"], gold["llm_subtype"]), 3), tol=0.005)

    print("\n--- Section 4: Endorsement funnel ---")
    check("Release-ready endorsement pairs", 1_136, len(endorse))
    check("Unique focals (release-ready)",   628,   endorse["focal_corpusid"].nunique())

    focals_pred = set(preds["focal_corpusid"].astype(int))
    paper_pos["focal_int"] = paper_pos["focal_corpusid"].astype(int)
    in_pred = paper_pos[paper_pos["focal_int"].isin(focals_pred)]
    check("Paper-time prediction focals",         134, preds["focal_corpusid"].nunique())
    check("402 retrieval-evaluable",              402, len(in_pred))
    check("145 Habitual (in_reading_shadow=1)",   145, (in_pred["is_in_reading_shadow"] == 1).sum())
    check("257 CiteNew (in_reading_shadow=0)",    257, (in_pred["is_in_reading_shadow"] == 0).sum())

    print("\n--- Section 5: MC-SPECTER2 endorsement endpoint h@100 ---")
    preds_top100 = preds[preds["rank"] < 100]
    preds_pairs = set(zip(preds_top100["focal_corpusid"].astype(int),
                          preds_top100["candidate_corpusid"].astype(int)))

    def hit_at_100(positives_df):
        pos = set(zip(positives_df["focal_corpusid"].astype(int),
                      positives_df["candidate_corpusid"].astype(int)))
        return len(pos & preds_pairs) / len(pos) if pos else 0

    in_pred_cn  = paper_pos[paper_pos["focal_int"].isin(focals_pred) & (paper_pos["is_in_reading_shadow"] == 0)]
    in_pred_hab = paper_pos[paper_pos["focal_int"].isin(focals_pred) & (paper_pos["is_in_reading_shadow"] == 1)]
    check("h@100 on n=257 CiteNew sub-cohort",  0.171, round(hit_at_100(in_pred_cn),  3), tol=0.005)
    check("h@100 on n=145 Habitual sub-cohort", 0.393, round(hit_at_100(in_pred_hab), 3), tol=0.005)

    print("\n" + "=" * 70)
    print("Verification complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
