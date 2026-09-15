"""
Step 2: Run Meiyie Summarization Pipeline on VT-SSum Converted Data
====================================================================
Runs Steps 7-10 of the Meiyie pipeline (embedding → clustering → 
cluster summarization → map-reduce final summary) on VT-SSum converted data.

This does NOT modify any existing pipeline code. It imports the existing
modules and runs them with redirected I/O paths.

Prerequisites:
    1. Run convert_vtssum.py first
    2. TurboQuant / llama-server must be running on localhost:8080

Usage:
    python run_pipeline_on_vtssum.py                   # Process ALL converted samples
    python run_pipeline_on_vtssum.py --limit 5         # Process first 5 samples
    python run_pipeline_on_vtssum.py --single <id>     # Process one specific sample
"""

import json
import os
import sys
import time
import shutil
import argparse
from typing import Any
import numpy as np

# ─── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

EVAL_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "evaluation", "vtssum_outputs")
PIPELINE_OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

# Add src to path so we can import pipeline modules
sys.path.insert(0, SRC_DIR)


def run_pipeline_steps_7_to_10(sample_id: str, sample_dir: str) -> dict[str, Any]:
    """
    Runs Steps 7-10 of the Meiyie pipeline on a single VT-SSum sample.
    
    Strategy: Copy the converted transcript.json and timeline into the
    standard outputs/ directory, run the pipeline steps, then move
    the results back into the sample's evaluation directory.
    """
    transcript_path = os.path.join(sample_dir, "transcript.json")
    timeline_path = os.path.join(sample_dir, "interleaved_timeline.txt")
    
    if not os.path.exists(transcript_path) or not os.path.exists(timeline_path):
        return {"status": "error", "message": "Missing converted files"}
    
    # ── Prepare the standard outputs/ directory ─────────────────────────────
    os.makedirs(PIPELINE_OUTPUTS_DIR, exist_ok=True)
    
    # Copy converted files to where the pipeline expects them
    std_transcript = os.path.join(PIPELINE_OUTPUTS_DIR, "transcript.json")
    std_timeline = os.path.join(PIPELINE_OUTPUTS_DIR, "interleaved_timeline.txt")
    
    shutil.copy2(transcript_path, std_transcript)
    shutil.copy2(timeline_path, std_timeline)
    
    run_times = {}
    errors = []
    
    # ── Step 7: Embed and Search ────────────────────────────────────────────
    try:
        print(f"\n  [Step 7] Embedding transcript chunks...")
        start = time.time()
        from utils.embed_and_search import embed_and_search
        embed_and_search()
        run_times["step_7_embed"] = round(time.time() - start, 2)
    except Exception as e:
        errors.append(f"Step 7 failed: {e}")
        print(f"  ❌ Step 7 error: {e}")
        return {"status": "error", "message": str(e), "step": 7}
    
    # ── Step 8: Cluster Subtopics ───────────────────────────────────────────
    try:
        print(f"  [Step 8] Clustering subtopics...")
        start = time.time()
        from utils.cluster_subtopics import cluster_subtopics
        cluster_subtopics()
        run_times["step_8_cluster"] = round(time.time() - start, 2)
    except Exception as e:
        errors.append(f"Step 8 failed: {e}")
        print(f"  ❌ Step 8 error: {e}")
        return {"status": "error", "message": str(e), "step": 8}
    
    # ── Step 9: Summarize Clusters ──────────────────────────────────────────
    try:
        print(f"  [Step 9] Summarizing clusters via TurboQuant...")
        start = time.time()
        from utils.summarize_clusters import summarize_clusters
        summarize_clusters()
        run_times["step_9_summarize_clusters"] = round(time.time() - start, 2)
    except Exception as e:
        errors.append(f"Step 9 failed: {e}")
        print(f"  ❌ Step 9 error: {e}")
        return {"status": "error", "message": str(e), "step": 9}
    
    # ── Step 10: Final Map-Reduce Summary ───────────────────────────────────
    try:
        print(f"  [Step 10] Generating final map-reduce summary...")
        start = time.time()
        from summarization.summarize import summarize_video
        summarize_video(
            input_path=std_timeline,
            output_path=os.path.join(PIPELINE_OUTPUTS_DIR, "final_summary.md")
        )
        run_times["step_10_final_summary"] = round(time.time() - start, 2)
    except Exception as e:
        errors.append(f"Step 10 failed: {e}")
        print(f"  ❌ Step 10 error: {e}")
        return {"status": "error", "message": str(e), "step": 10}
    
    # ── Collect results back into sample directory ──────────────────────────
    result_files = [
        "embeddings.npy",
        "clustered_subtopics.json",
        "final_topic_summaries.json",
        "chapter_summaries.txt",
        "final_summary.md"
    ]
    
    for fname in result_files:
        src = os.path.join(PIPELINE_OUTPUTS_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(sample_dir, fname))
    
    # Save timing info
    run_times["total"] = round(sum(run_times.values()), 2)
    with open(os.path.join(sample_dir, "pipeline_times.json"), 'w') as f:
        json.dump(run_times, f, indent=4)
    
    return {"status": "success", "times": run_times, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description="Run Meiyie pipeline on VT-SSum converted data")
    parser.add_argument("--limit", type=int, default=0, help="Process only N samples (0 = all)")
    parser.add_argument("--single", type=str, default=None, help="Process a single sample by ID")
    args = parser.parse_args()
    
    print("=" * 60)
    print("VT-SSum Evaluation — Pipeline Runner (Steps 7-10)")
    print("=" * 60)
    
    if not os.path.exists(EVAL_OUTPUT_DIR):
        print(f"❌ ERROR: Run convert_vtssum.py first!")
        print(f"   Expected: {EVAL_OUTPUT_DIR}")
        return
    
    # Change to project root (pipeline modules expect this)
    os.chdir(PROJECT_ROOT)
    
    # Determine which samples to process
    if args.single:
        sample_dirs = [args.single]
    else:
        sample_dirs = sorted([
            d for d in os.listdir(EVAL_OUTPUT_DIR) 
            if os.path.isdir(os.path.join(EVAL_OUTPUT_DIR, d)) and not d.startswith("_")
        ])
    
    if args.limit > 0:
        sample_dirs = sample_dirs[:args.limit]
    
    print(f"Samples to process: {len(sample_dirs)}")
    print(f"⚠️  Ensure TurboQuant server is running on localhost:8080!")
    print("-" * 60)
    
    total_start = time.time()
    results: dict = {"success": 0, "error": 0, "details": [], "total_time_seconds": 0.0}
    
    for i, sample_id in enumerate(sample_dirs):
        sample_path = os.path.join(EVAL_OUTPUT_DIR, sample_id)
        
        if not os.path.isdir(sample_path):
            print(f"  ⏭️  Skipping {sample_id} (not a directory)")
            continue
        
        # Check if already processed
        if os.path.exists(os.path.join(sample_path, "final_summary.md")):
            print(f"  [{i+1}/{len(sample_dirs)}] ⏭️  {sample_id} — already processed, skipping")
            results["success"] += 1
            continue
        
        # Load metadata for display
        meta_path = os.path.join(sample_path, "metadata.json")
        title = sample_id
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            title = meta.get("title", sample_id)[:60]
        
        print(f"\n  [{i+1}/{len(sample_dirs)}] 🔄 Processing: {title}")
        
        result = run_pipeline_steps_7_to_10(sample_id, sample_path)
        
        if result["status"] == "success":
            results["success"] += 1
            print(f"  ✅ Done in {result['times']['total']}s")
        else:
            results["error"] += 1
            print(f"  ❌ Failed at step {result.get('step', '?')}: {result['message']}")
        
        results["details"].append({
            "sample_id": sample_id,
            "title": title,
            **result
        })
    
    total_elapsed = time.time() - total_start
    
    print("\n" + "=" * 60)
    print(f"PIPELINE RUN COMPLETE")
    print(f"  ✅ Success: {results['success']}")
    print(f"  ❌ Errors:  {results['error']}")
    print(f"  ⏱️  Total:  {total_elapsed:.2f}s")
    print("=" * 60)
    
    # Save run log
    log_path = os.path.join(EVAL_OUTPUT_DIR, "_pipeline_run_log.json")
    results["total_time_seconds"] = round(total_elapsed, 2)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    print(f"📄 Run log saved to: {log_path}")


if __name__ == "__main__":
    main()
