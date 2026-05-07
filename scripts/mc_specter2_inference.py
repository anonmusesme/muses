"""Reference inference script for MC-SPECTER2, the headline retriever.

Builds K=16 history-trajectory centroids per author and ranks the candidate pool
by max-similarity to the centroids. No fine-tuning, no reranker, no LLM call.

This is the lean baseline that wins the broad-tier MUSES leaderboard:
hit@100 = 0.534 / 0.424 / 0.366 on CiteNext / CiteNew / CiteNew-Isolated.

Usage:
    python mc_specter2_inference.py \
        --instances muses/instance_splits.parquet \
        --candidate-pool muses/candidate_pool.parquet \
        --history-text-dir /path/to/s2orc/joined-history/ \
        --candidate-text-dir /path/to/s2orc/joined-candidates/ \
        --output predictions.parquet \
        --K 16 \
        --top-k 1000

Inputs:
    - instance_splits.parquet from the MUSES release
    - candidate_pool.parquet from the MUSES release
    - text-joined parquets from the user's S2ORC join (NOT included in this release)
        - history-text-dir: per-author papers with concatenated title + abstract,
          one parquet per author keyed by (authorid, paper_corpusid, text)
        - candidate-text-dir: candidate-pool papers with concatenated title +
          abstract, single parquet keyed by (corpusid, text)

Output parquet schema:
    authorid, focal_corpusid, candidate_corpusid, score, rank

License: Apache 2.0.

Notes:
    - SPECTER2 weights are loaded from `allenai/specter2_base` (Apache 2.0).
    - This script is a single-file reference. The full benchmark code repository
      contains a sharded multi-host implementation that is faster but identical
      in behaviour.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.cluster import KMeans
from transformers import AutoModel, AutoTokenizer


def encode(texts, tokenizer, model, device, max_length=512, batch_size=32):
    """Encode a list of texts with SPECTER2-base; return L2-normalized embeddings."""
    all_emb = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        enc = tokenizer(batch, padding=True, truncation=True,
                        max_length=max_length, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model(**enc)
        cls = out.last_hidden_state[:, 0]  # SPECTER2 uses CLS pooling
        cls = torch.nn.functional.normalize(cls, p=2, dim=-1)
        all_emb.append(cls.cpu().numpy())
    return np.vstack(all_emb)


def author_centroids(history_emb, K):
    """K-means centroids over an author's history embeddings, K=16 by default."""
    n = history_emb.shape[0]
    if n == 0:
        return np.zeros((1, history_emb.shape[1]), dtype=np.float32)
    if n <= K:
        return history_emb
    km = KMeans(n_clusters=K, n_init=4, random_state=0).fit(history_emb)
    centroids = km.cluster_centers_
    centroids = centroids / np.linalg.norm(centroids, axis=1, keepdims=True).clip(min=1e-9)
    return centroids.astype(np.float32)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", required=True)
    parser.add_argument("--candidate-pool", required=True)
    parser.add_argument("--history-text-dir", required=True,
                        help="Directory with per-author history-text parquets (joined from S2ORC under user license).")
    parser.add_argument("--candidate-text-dir", required=True,
                        help="Directory with candidate-pool text parquet (joined from S2ORC under user license).")
    parser.add_argument("--output", required=True)
    parser.add_argument("--K", type=int, default=16)
    parser.add_argument("--top-k", type=int, default=1000)
    parser.add_argument("--encoder", default="allenai/specter2_base")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    print(f"Loading encoder {args.encoder} ...")
    tokenizer = AutoTokenizer.from_pretrained(args.encoder)
    model = AutoModel.from_pretrained(args.encoder).to(args.device).eval()

    print("Loading candidate pool and encoding ...")
    cand_pool = pd.read_parquet(args.candidate_pool)
    cand_text = pd.concat([pd.read_parquet(p) for p in Path(args.candidate_text_dir).glob("*.parquet")])
    cand_text = cand_text.merge(cand_pool, on="corpusid", how="inner")
    cand_emb = encode(cand_text["text"].tolist(), tokenizer, model, args.device)
    cand_corpusids = cand_text["corpusid"].to_numpy()

    print("Loading instances ...")
    instances = pd.read_parquet(args.instances)
    test_instances = instances[instances["split"] == "test"]
    print(f"  {len(test_instances)} test instances")

    predictions = []
    for authorid, group in test_instances.groupby("authorid"):
        history_path = Path(args.history_text_dir) / f"author_{authorid}.parquet"
        if not history_path.exists():
            continue
        history = pd.read_parquet(history_path)
        history_emb = encode(history["text"].tolist(), tokenizer, model, args.device)
        centroids = author_centroids(history_emb, args.K)
        # Max similarity to any centroid; (n_cand x K) -> max axis=1
        sims = cand_emb @ centroids.T
        scores = sims.max(axis=1)
        top_idx = np.argpartition(-scores, args.top_k)[: args.top_k]
        top_idx = top_idx[np.argsort(-scores[top_idx])]
        for focal_corpusid in group["focal_corpusid"].unique():
            for rank, idx in enumerate(top_idx):
                predictions.append({
                    "authorid": authorid,
                    "focal_corpusid": int(focal_corpusid),
                    "candidate_corpusid": int(cand_corpusids[idx]),
                    "score": float(scores[idx]),
                    "rank": rank,
                })

    out_df = pd.DataFrame(predictions)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(out_path, index=False)
    print(f"Wrote {len(out_df)} predictions to {out_path}")


if __name__ == "__main__":
    main()
