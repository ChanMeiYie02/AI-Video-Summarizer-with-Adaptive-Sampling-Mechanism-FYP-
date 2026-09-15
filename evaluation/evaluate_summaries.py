"""
Step 3: Evaluate Meiyie Summaries Against VT-SSum Ground Truth
===============================================================
Computes ROUGE-1, ROUGE-2, ROUGE-L, and BERTScore (optional) between
the Meiyie-generated summaries and the VT-SSum extractive ground truth.

Produces:
  - Per-sample scores (saved per sample directory)
  - Aggregate results table (printed + saved as CSV and JSON)

Prerequisites:
    1. Run convert_vtssum.py first
    2. Run run_pipeline_on_vtssum.py first
    3. pip install rouge-score  (required)
    4. pip install bert-score   (optional, for BERTScore)

Usage:
    python evaluate_summaries.py                       # Evaluate ALL processed samples
    python evaluate_summaries.py --limit 10            # Evaluate first 10
    python evaluate_summaries.py --single <id>         # Evaluate one sample
    python evaluate_summaries.py --skip-bertscore      # Skip BERTScore (faster)
"""

import json
import os
import sys
import argparse
import time
import csv

# ─── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

EVAL_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "evaluation", "vtssum_outputs")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "evaluation", "results")


def compute_rouge_scores(prediction, reference):
    """
    Compute ROUGE-1, ROUGE-2, ROUGE-L F1 scores.
    """
    from rouge_score import rouge_scorer
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, prediction)
    
    return {
        "rouge1_f1": round(scores['rouge1'].fmeasure, 4),
        "rouge1_precision": round(scores['rouge1'].precision, 4),
        "rouge1_recall": round(scores['rouge1'].recall, 4),
        "rouge2_f1": round(scores['rouge2'].fmeasure, 4),
        "rouge2_precision": round(scores['rouge2'].precision, 4),
        "rouge2_recall": round(scores['rouge2'].recall, 4),
        "rougeL_f1": round(scores['rougeL'].fmeasure, 4),
        "rougeL_precision": round(scores['rougeL'].precision, 4),
        "rougeL_recall": round(scores['rougeL'].recall, 4),
    }


def compute_bertscore(prediction, reference):
    """
    Compute BERTScore (Precision, Recall, F1).
    """
    try:
        from bert_score import score as bert_score_fn
        
        P, R, F1 = bert_score_fn(
            [prediction], [reference], 
            lang="en", 
            verbose=False,
            device="cuda"
        )
        return {
            "bertscore_precision": round(P.item(), 4),  # type: ignore[union-attr]
            "bertscore_recall": round(R.item(), 4),  # type: ignore[union-attr]
            "bertscore_f1": round(F1.item(), 4),  # type: ignore[union-attr]
        }
    except ImportError:
        return {"bertscore_error": "bert-score not installed (pip install bert-score)"}
    except Exception as e:
        return {"bertscore_error": str(e)}


def evaluate_single_sample(sample_dir, skip_bertscore=False):
    """
    Evaluate a single sample's generated summary against ground truth.
    """
    gt_path = os.path.join(sample_dir, "ground_truth_summary.txt")
    
    # Try final_summary.md first, then chapter_summaries.txt as fallback
    gen_path = os.path.join(sample_dir, "final_summary.md")
    if not os.path.exists(gen_path):
        return None
    
    if not os.path.exists(gt_path):
        return None
    
    with open(gt_path, 'r', encoding='utf-8') as f:
        reference = f.read().strip()
    
    with open(gen_path, 'r', encoding='utf-8') as f:
        prediction = f.read().strip()
    
    # Remove markdown header if present
    if prediction.startswith("# Final Multimodal Video Summary"):
        prediction = prediction.replace("# Final Multimodal Video Summary", "").strip()
    
    if not prediction or not reference:
        return None
    
    # Compute scores
    scores = compute_rouge_scores(prediction, reference)
    
    if not skip_bertscore:
        bert_scores = compute_bertscore(prediction, reference)
        scores.update(bert_scores)
    
    # Add metadata
    scores["prediction_length"] = len(prediction)
    scores["reference_length"] = len(reference)
    scores["compression_ratio"] = round(len(prediction) / max(len(reference), 1), 2)
    
    # Save per-sample scores
    with open(os.path.join(sample_dir, "eval_scores.json"), 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=4)
    
    return scores


def main():
    parser = argparse.ArgumentParser(description="Evaluate Meiyie summaries vs VT-SSum ground truth")
    parser.add_argument("--limit", type=int, default=0, help="Evaluate only N samples (0 = all)")
    parser.add_argument("--single", type=str, default=None, help="Evaluate a single sample by ID")
    parser.add_argument("--skip-bertscore", action="store_true", help="Skip BERTScore computation")
    args = parser.parse_args()
    
    print("=" * 60)
    print("VT-SSum Evaluation — Summary Quality Metrics")
    print("=" * 60)
    
    if not os.path.exists(EVAL_OUTPUT_DIR):
        print(f"❌ ERROR: No evaluation outputs found at: {EVAL_OUTPUT_DIR}")
        print(f"   Run convert_vtssum.py and run_pipeline_on_vtssum.py first!")
        return
    
    # Check dependencies
    try:
        from rouge_score import rouge_scorer
        print("✅ rouge-score installed")
    except ImportError:
        print("❌ rouge-score not found. Install: pip install rouge-score")
        return
    
    if not args.skip_bertscore:
        try:
            import bert_score
            print("✅ bert-score installed")
        except ImportError:
            print("⚠️  bert-score not found. Install: pip install bert-score")
            print("   Continuing without BERTScore (use --skip-bertscore to suppress this)")
            args.skip_bertscore = True
    else:
        print("⏭️  Skipping BERTScore (--skip-bertscore flag)")
    
    # Determine which samples to evaluate
    if args.single:
        sample_dirs = [args.single]
    else:
        sample_dirs = sorted([
            d for d in os.listdir(EVAL_OUTPUT_DIR)
            if os.path.isdir(os.path.join(EVAL_OUTPUT_DIR, d)) and not d.startswith("_")
        ])
    
    if args.limit > 0:
        sample_dirs = sample_dirs[:args.limit]
    
    print(f"\nSamples to evaluate: {len(sample_dirs)}")
    print("-" * 60)
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    start_time = time.time()
    all_scores = []
    evaluated = 0
    skipped = 0
    
    for i, sample_id in enumerate(sample_dirs):
        sample_path = os.path.join(EVAL_OUTPUT_DIR, sample_id)
        
        if not os.path.isdir(sample_path):
            continue
        
        scores = evaluate_single_sample(sample_path, skip_bertscore=args.skip_bertscore)
        
        if scores is None:
            skipped += 1
            continue
        
        evaluated += 1
        scores["sample_id"] = sample_id
        
        # Load title from metadata
        meta_path = os.path.join(sample_path, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            scores["title"] = meta.get("title", "")
        
        all_scores.append(scores)
        
        if (i + 1) % 50 == 0 or len(sample_dirs) <= 20:
            print(f"  [{i+1}/{len(sample_dirs)}] {sample_id}: "
                  f"R1={scores['rouge1_f1']:.3f} R2={scores['rouge2_f1']:.3f} "
                  f"RL={scores['rougeL_f1']:.3f}" +
                  (f" BS={scores.get('bertscore_f1', 'N/A')}" if not args.skip_bertscore else ""))
    
    elapsed = time.time() - start_time
    
    if not all_scores:
        print("\n❌ No samples were successfully evaluated.")
        print("   Ensure you've run run_pipeline_on_vtssum.py first.")
        return
    
    # ── Compute Aggregate Statistics ────────────────────────────────────────
    metric_keys = ["rouge1_f1", "rouge2_f1", "rougeL_f1", 
                   "rouge1_precision", "rouge1_recall",
                   "rouge2_precision", "rouge2_recall",
                   "rougeL_precision", "rougeL_recall"]
    
    if not args.skip_bertscore and "bertscore_f1" in all_scores[0]:
        metric_keys += ["bertscore_precision", "bertscore_recall", "bertscore_f1"]
    
    aggregates = {}
    for key in metric_keys:
        values = [s[key] for s in all_scores if key in s]
        if values:
            aggregates[key] = {
                "mean": round(sum(values) / len(values), 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
                "count": len(values)
            }
    
    # ── Print Results ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"EVALUATION RESULTS — {evaluated} samples evaluated")
    print("=" * 60)
    
    print(f"\n{'Metric':<25} {'Mean':>8} {'Min':>8} {'Max':>8}")
    print("-" * 55)
    for key in ["rouge1_f1", "rouge2_f1", "rougeL_f1", "bertscore_f1"]:
        if key in aggregates:
            agg = aggregates[key]
            print(f"  {key:<23} {agg['mean']:>8.4f} {agg['min']:>8.4f} {agg['max']:>8.4f}")
    
    print(f"\n  Evaluated: {evaluated} | Skipped: {skipped} | Time: {elapsed:.2f}s")
    
    # ── Save Results ────────────────────────────────────────────────────────
    # 1. Full JSON report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "samples_evaluated": evaluated,
        "samples_skipped": skipped,
        "evaluation_time_seconds": round(elapsed, 2),
        "aggregate_metrics": aggregates,
        "per_sample_scores": all_scores
    }
    json_path = os.path.join(RESULTS_DIR, "evaluation_report.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
    print(f"\n📊 Full report: {json_path}")
    
    # 2. CSV for easy spreadsheet import
    csv_path = os.path.join(RESULTS_DIR, "evaluation_scores.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["sample_id", "title"] + metric_keys + 
                                ["prediction_length", "reference_length", "compression_ratio"])
        writer.writeheader()
        for s in all_scores:
            writer.writerow({k: s.get(k, "") for k in writer.fieldnames})
    print(f"📄 CSV scores: {csv_path}")
    
    # 3. Summary markdown
    md_path = os.path.join(RESULTS_DIR, "evaluation_summary.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# VT-SSum Benchmark Evaluation Results\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Samples Evaluated:** {evaluated}  \n")
        f.write(f"**Pipeline:** Meiyie (Steps 7-10: Embedding → Clustering → LLM Summary → Map-Reduce)  \n\n")
        f.write("## Aggregate Scores\n\n")
        f.write(f"| Metric | Mean | Min | Max |\n")
        f.write(f"|--------|------|-----|-----|\n")
        for key in ["rouge1_f1", "rouge2_f1", "rougeL_f1", "bertscore_f1"]:
            if key in aggregates:
                agg = aggregates[key]
                f.write(f"| {key} | {agg['mean']:.4f} | {agg['min']:.4f} | {agg['max']:.4f} |\n")
        f.write(f"\n## Notes\n\n")
        f.write(f"- **Reference:** VT-SSum extractive ground truth (sentences with label=1)\n")
        f.write(f"- **Prediction:** Meiyie abstractive summary (final_summary.md)\n")
        f.write(f"- **Task mismatch:** Extractive vs abstractive summarization — "
                f"ROUGE scores may be lower than extractive baselines by nature.\n")
    print(f"📝 Summary report: {md_path}")
    
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
