"""
Step 1: VT-SSum → Meiyie Format Converter
==========================================
Converts VT-SSum benchmark JSON files into Meiyie-compatible format:
  - transcript.json      (for Steps 7-8: embedding + clustering)
  - interleaved_timeline.txt  (for Step 10: Map-Reduce summary)
  - ground_truth_summary.txt  (extractive reference for evaluation)
  - metadata.json        (video title, url, stats)

Usage:
    python convert_vtssum.py                           # Convert ALL test files
    python convert_vtssum.py --limit 10                # Convert first 10 files only
    python convert_vtssum.py --single <filename>.json  # Convert one specific file
"""

import json
import os
import argparse
import glob
import time
from typing import Any, Optional

# ─── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

VTSSUM_INPUT_DIR = os.path.join(PROJECT_ROOT, "data", "VT-SSum", "test")
if not os.path.exists(VTSSUM_INPUT_DIR):
    VTSSUM_INPUT_DIR = os.path.join(PROJECT_ROOT, "data", "VT-SSum-test")
EVAL_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "evaluation", "vtssum_outputs")

# How many seconds to assign per segment (for fake timestamps)
SEGMENT_DURATION = 29.0


def convert_single_sample(input_path: str, output_dir: str) -> Optional[dict[str, Any]]:
    """
    Converts a single VT-SSum JSON file into Meiyie-compatible format.
    
    Returns a dict with conversion stats, or None on failure.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    video_id = data.get("id", os.path.splitext(os.path.basename(input_path))[0])
    sample_output_dir = os.path.join(output_dir, video_id)
    os.makedirs(sample_output_dir, exist_ok=True)
    
    # ── 1. Build transcript.json from segmentation ──────────────────────────
    transcript = []
    timeline_lines = []
    fake_time = 0.0
    total_sentences = 0
    
    segmentation = data.get("segmentation", [])
    
    for seg_idx, segment_sentences in enumerate(segmentation):
        combined_text = " ".join(segment_sentences)
        start = fake_time
        end = fake_time + SEGMENT_DURATION
        
        transcript.append({
            "text": combined_text,
            "start": round(start, 1),
            "end": round(end, 1)
        })
        
        timeline_lines.append(f"[{start:.1f}s - {end:.1f}s]")
        timeline_lines.append(combined_text)
        timeline_lines.append("")
        
        fake_time = end
        total_sentences += len(segment_sentences)
    
    # ── 2. Extract ground truth summary (sentences with label=1) ────────────
    gt_summary_sentences = []
    summarization = data.get("summarization", {})
    total_clips_with_summary = 0
    
    for clip_key in sorted(summarization.keys()):
        clip_data = summarization[clip_key]
        if clip_data.get("is_summarization_sample", False):
            total_clips_with_summary += 1
            for item in clip_data.get("summarization_data", []):
                if item.get("label", 0) == 1:
                    gt_summary_sentences.append(item["sent"])
    
    # Skip samples with no ground truth summary
    if not gt_summary_sentences:
        return None
    
    ground_truth_summary = " ".join(gt_summary_sentences)
    
    # ── 3. Save metadata ───────────────────────────────────────────────────
    metadata = {
        "id": video_id,
        "title": data.get("title", "Unknown"),
        "url": data.get("url", ""),
        "info": data.get("info", {}),
        "num_segments": len(segmentation),
        "num_sentences": total_sentences,
        "num_clips_with_summary": total_clips_with_summary,
        "num_gt_summary_sentences": len(gt_summary_sentences),
        "ground_truth_summary_length_chars": len(ground_truth_summary)
    }
    
    # ── 4. Write all output files ──────────────────────────────────────────
    with open(os.path.join(sample_output_dir, "transcript.json"), 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=4, ensure_ascii=False)
    
    with open(os.path.join(sample_output_dir, "interleaved_timeline.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(timeline_lines))
    
    with open(os.path.join(sample_output_dir, "ground_truth_summary.txt"), 'w', encoding='utf-8') as f:
        f.write(ground_truth_summary)
    
    with open(os.path.join(sample_output_dir, "metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Convert VT-SSum test data to Meiyie format")
    parser.add_argument("--limit", type=int, default=0, help="Limit to N files (0 = all)")
    parser.add_argument("--single", type=str, default=None, help="Convert a single specific JSON file")
    args = parser.parse_args()
    
    print("=" * 60)
    print("VT-SSum → Meiyie Format Converter")
    print("=" * 60)
    print(f"Input dir:  {VTSSUM_INPUT_DIR}")
    print(f"Output dir: {EVAL_OUTPUT_DIR}")
    
    if not os.path.exists(VTSSUM_INPUT_DIR):
        print(f"\n❌ ERROR: VT-SSum test data not found at: {VTSSUM_INPUT_DIR}")
        return
    
    # Determine which files to process
    if args.single:
        single_path = os.path.join(VTSSUM_INPUT_DIR, args.single)
        if not os.path.exists(single_path):
            print(f"\n❌ ERROR: File not found: {single_path}")
            return
        json_files = [single_path]
    else:
        json_files = sorted(glob.glob(os.path.join(VTSSUM_INPUT_DIR, "*.json")))
    
    if args.limit > 0:
        json_files = json_files[:args.limit]
    
    print(f"Files to convert: {len(json_files)}")
    print("-" * 60)
    
    os.makedirs(EVAL_OUTPUT_DIR, exist_ok=True)
    
    start_time = time.time()
    success_count = 0
    skip_count = 0
    
    for i, fpath in enumerate(json_files):
        fname = os.path.basename(fpath)
        result = convert_single_sample(fpath, EVAL_OUTPUT_DIR)
        
        if result is None:
            skip_count += 1
            if (i + 1) % 100 == 0 or len(json_files) <= 20:
                print(f"  [{i+1}/{len(json_files)}] ⏭️  {fname} — skipped (no ground truth summary)")
        else:
            success_count += 1
            if (i + 1) % 100 == 0 or len(json_files) <= 20:
                print(f"  [{i+1}/{len(json_files)}] ✅ {result['title'][:50]}... "
                      f"({result['num_segments']} segs, {result['num_gt_summary_sentences']} GT sents)")
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"CONVERSION COMPLETE")
    print(f"  ✅ Converted: {success_count}")
    print(f"  ⏭️  Skipped (no GT): {skip_count}")
    print(f"  ⏱️  Time: {elapsed:.2f}s")
    print(f"  📁 Output: {EVAL_OUTPUT_DIR}")
    print("=" * 60)
    
    # Save a manifest of all converted samples
    manifest = {
        "total_files_processed": len(json_files),
        "successful_conversions": success_count,
        "skipped_no_ground_truth": skip_count,
        "conversion_time_seconds": round(elapsed, 2),
        "converted_ids": sorted(os.listdir(EVAL_OUTPUT_DIR))
    }
    with open(os.path.join(EVAL_OUTPUT_DIR, "_manifest.json"), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4)


if __name__ == "__main__":
    main()
