"""Reference inference script for the CiteRoots-Rhetoric distilled judge.

Loads the Qwen3-8B base + LoRA adapters and produces ROOT / NON_ROOT predictions
plus calibrated probabilities for a list of citation contexts.

Usage:
    python judge_inference.py \
        --adapter-path anon-muses-neurips/citeroots-rhetoric-judge-qwen3-8b \
        --input contexts.jsonl \
        --output predictions.parquet

Input JSONL schema (one record per line):
    {
        "context_id": "...",
        "focal_corpusid": 12345,
        "candidate_corpusid": 67890,
        "context_text": "We extend the approach of [REF_TARGET] to ...",
        "target_marker": "[REF_TARGET]"
    }

Output parquet schema:
    context_id, focal_corpusid, candidate_corpusid,
    label (ROOT|NON_ROOT|UNSURE), root_probability (float), key_phrase (str|null)

License: Apache 2.0 for this script. Distilled adapter weights are released under
Apache 2.0; the Qwen3-8B base is subject to its upstream license terms.
"""

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer


PROMPT_TEMPLATE = """You are an impartial citation classifier for the CiteRoots v7.0 benchmark.

Classify the function of the citation marked {target_marker} in the following context into one of six categories:

ROOT categories:
  - THEORETICAL_FOUNDATION (TF): the cited work supplies a conceptual framework, theory, or formal model that the citing paper operationalizes as-is.
  - METHOD_EXTENSION (ME): the citing paper non-trivially modifies, extends, or generalizes the cited method.
  - GENERATIVE_MOTIVATION (GM): the cited work sparks or motivates the research direction by exposing a gap, limitation, anomaly, or finding that causally explains why the current paper exists.

NON-ROOT categories:
  - CONTRAST_COMPARISON (CC): rhetorical contrast or performance benchmarking with explicit contrastive phrasing.
  - TOOL_RESOURCE (TR): instrumental use as software, dataset, library, benchmark, or recipe.
  - BACKGROUND_CONTEXT (BC): residual non-generative mention.

Decide using only the provided context. Do not use prior knowledge about the cited paper.

Context:
{context_text}

Return JSON: {{"reasoning": "...", "label": "ROOT|NON_ROOT|UNSURE", "subtype": "TF|ME|GM|CC|TR|BC", "confidence": "high|medium|low", "key_phrase": "..."}}
"""


def build_input(record: dict) -> str:
    return PROMPT_TEMPLATE.format(
        target_marker=record["target_marker"],
        context_text=record["context_text"],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-path", required=True,
                        help="HF model id or local path to the LoRA adapters.")
    parser.add_argument("--base-model", default="Qwen/Qwen3-8B",
                        help="Base model id (default: Qwen/Qwen3-8B).")
    parser.add_argument("--input", required=True, help="Input JSONL file.")
    parser.add_argument("--output", required=True, help="Output parquet file.")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    print(f"Loading base model {args.base_model} ...")
    base_model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=2,
        torch_dtype=torch.float16,
        device_map=args.device,
    )
    print(f"Loading LoRA adapters from {args.adapter_path} ...")
    model = PeftModel.from_pretrained(base_model, args.adapter_path)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(args.adapter_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    records = []
    with open(args.input) as f:
        for line in f:
            records.append(json.loads(line))
    print(f"Loaded {len(records)} contexts.")

    predictions = []
    for i in range(0, len(records), args.batch_size):
        batch = records[i : i + args.batch_size]
        texts = [build_input(r) for r in batch]
        enc = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=args.max_length,
            return_tensors="pt",
        ).to(args.device)
        with torch.no_grad():
            logits = model(**enc).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()
        for r, p in zip(batch, probs):
            root_prob = float(p[1])
            label = "ROOT" if root_prob >= 0.5 else "NON_ROOT"
            predictions.append({
                "context_id": r.get("context_id"),
                "focal_corpusid": r.get("focal_corpusid"),
                "candidate_corpusid": r.get("candidate_corpusid"),
                "label": label,
                "root_probability": root_prob,
                "key_phrase": None,  # the binary student does not extract key phrases
            })

    out_df = pd.DataFrame(predictions)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(out_path, index=False)
    print(f"Wrote {len(out_df)} predictions to {out_path}")


if __name__ == "__main__":
    main()
