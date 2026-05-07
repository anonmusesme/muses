"""Build the stripped, license-clean candidate-pool artifacts for release.

Reads the internal full candidate-pool parquet (which contains S2ORC-owned text
and metadata) and emits two stripped artifacts that can be released under
CC-BY-4.0:

    1. candidate_pool.parquet          — corpusid only (~30 MB)
    2. candidate_pool_derived.parquet  — corpusid + our derived flags
                                         (time_safe, text_ready, primary_field_kd)
                                         (~50 MB)

The stripped artifacts contain NO S2ORC-owned columns: no title, no abstract,
no year, no venue, no authors, no s2_field_of_study. Users join with S2ORC by
corpusid under the S2ORC license.

Usage:
    python build_candidate_pool.py \
        --source /data/.../benchmark_release_2026-03-10/candidate_papers_global.parquet \
        --output-pool release/muses/candidate_pool.parquet \
        --output-derived release/muses/candidate_pool_derived.parquet

License: Apache 2.0.
"""

import argparse
from pathlib import Path

import pandas as pd


# The exact set of S2ORC-owned columns we MUST NOT redistribute.
S2ORC_OWNED_COLUMNS = {
    "title", "abstract", "venue", "year", "authors", "author_names",
    "s2_field_of_study", "external_ids", "doi", "arxiv_id", "pubmed_id",
    "open_access_pdf", "tldr", "embedding", "citation_count",
    "reference_count", "influential_citation_count", "is_open_access",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True,
                        help="Internal full candidate-pool parquet (NOT for release).")
    parser.add_argument("--output-pool", required=True,
                        help="Output: corpusid-only stripped parquet.")
    parser.add_argument("--output-derived", required=True,
                        help="Output: corpusid + our derived flags parquet.")
    args = parser.parse_args()

    print(f"Reading source from {args.source} ...")
    df = pd.read_parquet(args.source)
    print(f"  {len(df):,} rows; columns: {list(df.columns)}")

    # Sanity check: the source MUST have a corpusid column.
    if "corpusid" not in df.columns:
        raise SystemExit("Source parquet must have a `corpusid` column.")

    # Sanity check: warn if we see any S2ORC-owned columns; we will strip them.
    leaked = [c for c in df.columns if c in S2ORC_OWNED_COLUMNS]
    if leaked:
        print(f"  Stripping S2ORC-owned columns: {leaked}")

    # Output 1: corpusid-only.
    pool = df[["corpusid"]].drop_duplicates().sort_values("corpusid").reset_index(drop=True)
    out_pool = Path(args.output_pool)
    out_pool.parent.mkdir(parents=True, exist_ok=True)
    pool.to_parquet(out_pool, index=False)
    print(f"Wrote {len(pool):,} corpusids to {out_pool} "
          f"({out_pool.stat().st_size / 1e6:.1f} MB)")

    # Output 2: corpusid + our derived flags.
    derived_columns = ["corpusid"]
    for col in ["time_safe", "text_ready", "primary_field_kd"]:
        if col in df.columns:
            derived_columns.append(col)
        else:
            print(f"  WARNING: derived column `{col}` missing from source; "
                  f"will need to be computed upstream before release.")
    derived = df[derived_columns].drop_duplicates(subset=["corpusid"]).sort_values("corpusid").reset_index(drop=True)
    out_derived = Path(args.output_derived)
    out_derived.parent.mkdir(parents=True, exist_ok=True)
    derived.to_parquet(out_derived, index=False)
    print(f"Wrote {len(derived):,} rows × {len(derived_columns)} cols to {out_derived} "
          f"({out_derived.stat().st_size / 1e6:.1f} MB)")

    # Final license-boundary assertion.
    leaked_in_output = [c for c in derived.columns if c in S2ORC_OWNED_COLUMNS]
    if leaked_in_output:
        raise SystemExit(
            f"BLOCKED: output {out_derived} contains S2ORC-owned columns: "
            f"{leaked_in_output}. Refusing to write a license-violating release "
            f"artifact."
        )
    print("License-boundary assertion: OK (no S2ORC-owned columns in either output).")


if __name__ == "__main__":
    main()
