import os
import sys
import json
import random
import time
import string
import re
import shutil
import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM
from tqdm import tqdm

# Configure paths
DATASET_DIR = r"C:\Users\admin\Downloads\Voice_Noise_Test_Set"
LOG_FILE = os.path.join(DATASET_DIR, "log_trainset_28spk.txt")
WAV_DIR = os.path.join(DATASET_DIR, "noisy_trainset_28spk_wav")
TXT_DIR = os.path.join(DATASET_DIR, "trainset_28spk_txt")

# Set target directory inside experiments folder
RESULTS_DIR = r"evaluation\results\experiments\Noise_Voice_Evaluation"
RESULTS_JSON = os.path.join(RESULTS_DIR, "voice_noise_results.json")
REPORT_MD = os.path.join(RESULTS_DIR, "voice_noise_report.md")

# Ensure output directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)


def calculate_wer(reference, hypothesis):
    """Calculates Word Error Rate using standard dynamic programming edit distance."""
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    
    d = [[0 for _ in range(len(hyp_words) + 1)] for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j
        
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion = d[i][j-1] + 1
                deletion = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
                
    if len(ref_words) == 0:
        return 1.0 if len(hyp_words) > 0 else 0.0
    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


def normalize_text(text):
    """Normalizes text by converting to lowercase, removing punctuation, and collapsing spacing."""
    if not text:
        return ""
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_dataset_log():
    """Parses log_trainset_28spk.txt and validates file existence."""
    print(f"Parsing log file: {LOG_FILE}...")
    if not os.path.exists(LOG_FILE):
        raise FileNotFoundError(f"Log file not found at: {LOG_FILE}")
        
    entries = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                filename = parts[0]
                category = parts[1]
                try:
                    snr = int(parts[2])
                except ValueError:
                    snr = parts[2]
                
                wav_path = os.path.join(WAV_DIR, f"{filename}.wav")
                txt_path = os.path.join(TXT_DIR, f"{filename}.txt")
                
                # Verify that both audio and ground truth files exist in source
                if os.path.exists(wav_path) and os.path.exists(txt_path):
                    entries.append({
                        "filename": filename,
                        "category": category,
                        "snr": snr,
                        "src_wav_path": wav_path,
                        "src_txt_path": txt_path
                    })
    print(f"Successfully loaded and verified {len(entries)} entries with files in source.")
    return entries


def sample_dataset(entries):
    """
    Samples 100 entries per category (10 categories, total 1000 entries)
    balanced evenly across SNR levels (25 samples per SNR: 0, 5, 10, 15 dB).
    Uses a fixed random seed for reproducibility.
    """
    random.seed(42)
    categories = sorted(list(set(e["category"] for e in entries)))
    snrs = [0, 5, 10, 15]
    
    sampled_entries = []
    
    print("\n--- Starting Balanced Sampling ---")
    for category in categories:
        cat_entries = [e for e in entries if e["category"] == category]
        print(f"Category: {category.upper()} (Total available: {len(cat_entries)})")
        
        cat_sampled = []
        for snr in snrs:
            snr_entries = [e for e in cat_entries if e["snr"] == snr]
            
            # Target 25 samples per SNR
            needed = 25
            if len(snr_entries) >= needed:
                sampled = random.sample(snr_entries, needed)
            else:
                print(f"  [WARNING] Only {len(snr_entries)} available for SNR {snr}dB. Taking all.")
                sampled = snr_entries
            cat_sampled.extend(sampled)
            
        # Ensure we have exactly 100 samples per category (if possible)
        if len(cat_sampled) < 100:
            remaining_needed = 100 - len(cat_sampled)
            remaining_entries = [e for e in cat_entries if e not in cat_sampled]
            if len(remaining_entries) >= remaining_needed:
                additional_samples = random.sample(remaining_entries, remaining_needed)
                cat_sampled.extend(additional_samples)
            else:
                cat_sampled.extend(remaining_entries)
                
        print(f"  -> Sampled {len(cat_sampled)} entries for {category}.")
        sampled_entries.extend(cat_sampled)
        
    print(f"Total sampled entries: {len(sampled_entries)}")
    return sampled_entries


def load_gemma4_model():
    """Loads Google Gemma-4-E2B-it unquantized on GPU (BF16 or FP16)."""
    model_id = "google/gemma-4-E2B-it"
    print(f"\nLoading model {model_id} on GPU...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device != "cuda":
        print("[WARNING] CUDA is not available. Execution will run slowly on CPU!")
        
    processor = AutoProcessor.from_pretrained(model_id)
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    
    model = AutoModelForMultimodalLM.from_pretrained(
        model_id,
        device_map=device,
        torch_dtype=dtype,
    )
    return processor, model, device


def load_checkpoint():
    """Loads intermediate run results from checkpoint file to support resuming."""
    if os.path.exists(RESULTS_JSON):
        try:
            with open(RESULTS_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading checkpoint file: {e}. Starting fresh.")
    return []


def save_checkpoint(results):
    """Saves run results to checkpoint file."""
    with open(RESULTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)


def copy_files_to_category_folders(sampled_entries):
    """Copies sampled WAV and TXT files to category-specific folders inside RESULTS_DIR."""
    print(f"\n--- Organizing Audio and Text Files into Category Folders ---")
    organized_entries = []
    
    for entry in sampled_entries:
        category = entry["category"]
        filename = entry["filename"]
        
        # Create category folder
        category_dir = os.path.join(RESULTS_DIR, category)
        os.makedirs(category_dir, exist_ok=True)
        
        dest_wav_path = os.path.join(category_dir, f"{filename}.wav")
        dest_txt_path = os.path.join(category_dir, f"{filename}.txt")
        
        # Copy WAV if it doesn't exist
        if not os.path.exists(dest_wav_path):
            shutil.copy(entry["src_wav_path"], dest_wav_path)
            
        # Copy TXT if it doesn't exist
        if not os.path.exists(dest_txt_path):
            shutil.copy(entry["src_txt_path"], dest_txt_path)
            
        organized_entries.append({
            "filename": filename,
            "category": category,
            "snr": entry["snr"],
            "wav_path": dest_wav_path,
            "txt_path": dest_txt_path
        })
        
    print(f"Dataset organization complete. All files available under: {RESULTS_DIR}")
    return organized_entries


def run_evaluation():
    # 1. Parse dataset log and validate files
    all_entries = load_dataset_log()
    
    # 2. Sample 1000 entries (100 per category, balanced SNRs)
    sampled_entries = sample_dataset(all_entries)
    
    # 3. Copy files to self-contained category folders first
    organized_entries = copy_files_to_category_folders(sampled_entries)
    
    # 4. Load checkpoint to support resuming
    results = load_checkpoint()
    processed_filenames = set(res["filename"] for res in results)
    print(f"\nResuming evaluation: {len(processed_filenames)} / {len(organized_entries)} already processed.")
    
    # Filter out entries already processed
    entries_to_process = [e for e in organized_entries if e["filename"] not in processed_filenames]
    
    if entries_to_process:
        # 5. Load Gemma-4 model
        processor, model, device = load_gemma4_model()
        
        print("\n--- Running Voice-to-Text Transcriptions ---")
        for entry in tqdm(entries_to_process, desc="Processing Audio"):
            filename = entry["filename"]
            wav_path = entry["wav_path"]
            txt_path = entry["txt_path"]
            category = entry["category"]
            snr = entry["snr"]
            
            # Read ground truth transcription
            with open(txt_path, 'r', encoding='utf-8') as f:
                gt_text = f.read().strip()
                
            # Perform speech inference using Gemma-4-E2B-it
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "audio", "audio": wav_path},
                        {
                            "type": "text",
                            "text": (
                                "Transcribe the following speech segment in its original language. "
                                "Follow these specific instructions for formatting the answer:\n"
                                "* Only output the transcription, with no newlines.\n"
                                "* When transcribing numbers, write the digits."
                            )
                        }
                    ]
                }
            ]
            
            prediction = ""
            try:
                inputs = processor.apply_chat_template(
                    messages,
                    tokenize=True,
                    return_dict=True,
                    return_tensors="pt",
                    add_generation_prompt=True
                ).to(device)
                
                input_len = inputs["input_ids"].shape[-1]
                
                with torch.inference_mode():
                    outputs = model.generate(**inputs, max_new_tokens=256)
                    
                generated_tokens = outputs[0][input_len:]
                prediction = processor.decode(generated_tokens, skip_special_tokens=True).strip()
            except Exception as e:
                print(f"\n[ERROR] Failed to transcribe {filename}: {e}")
                prediction = "[FAILED]"
                
            # Normalize text for comparisons
            norm_gt = normalize_text(gt_text)
            norm_pred = normalize_text(prediction)
            
            # Calculate metrics
            wer = calculate_wer(norm_gt, norm_pred)
            exact_match = 1 if norm_gt == norm_pred else 0
            
            results.append({
                "filename": filename,
                "category": category,
                "snr": snr,
                "ground_truth": gt_text,
                "prediction": prediction,
                "norm_gt": norm_gt,
                "norm_pred": norm_pred,
                "wer": wer,
                "exact_match": exact_match
            })
            
            # Save checkpoint incrementally
            save_checkpoint(results)
    
    # 6. Perform Post-Evaluation Analysis and Report Generation
    generate_report(results)


def generate_report(results):
    print("\n--- Generating Evaluation Report ---")
    
    # Filter out failures if any
    valid_results = [r for r in results if r["prediction"] != "[FAILED]"]
    total_valid = len(valid_results)
    
    if total_valid == 0:
        print("No valid evaluation results found to generate report.")
        return
        
    avg_wer_overall = sum(r["wer"] for r in valid_results) / total_valid
    avg_em_overall = sum(r["exact_match"] for r in valid_results) / total_valid * 100
    
    # 1. Group by category
    categories = sorted(list(set(r["category"] for r in valid_results)))
    category_stats = {}
    for cat in categories:
        cat_res = [r for r in valid_results if r["category"] == cat]
        cat_count = len(cat_res)
        avg_wer = sum(r["wer"] for r in cat_res) / cat_count if cat_count > 0 else 0
        avg_em = sum(r["exact_match"] for r in cat_res) / cat_count * 100 if cat_count > 0 else 0
        category_stats[cat] = {"wer": avg_wer, "em": avg_em, "count": cat_count}
        
    # 2. Group by SNR level
    snrs = sorted(list(set(r["snr"] for r in valid_results)))
    snr_stats = {}
    for snr in snrs:
        snr_res = [r for r in valid_results if r["snr"] == snr]
        snr_count = len(snr_res)
        avg_wer = sum(r["wer"] for r in snr_res) / snr_count if snr_count > 0 else 0
        avg_em = sum(r["exact_match"] for r in snr_res) / snr_count * 100 if snr_count > 0 else 0
        snr_stats[snr] = {"wer": avg_wer, "em": avg_em, "count": snr_count}

    # 3. Category X SNR matrix
    matrix_stats = {}
    for cat in categories:
        matrix_stats[cat] = {}
        for snr in snrs:
            cell_res = [r for r in valid_results if r["category"] == cat and r["snr"] == snr]
            cell_count = len(cell_res)
            avg_wer = sum(r["wer"] for r in cell_res) / cell_count if cell_count > 0 else 0
            avg_em = sum(r["exact_match"] for r in cell_res) / cell_count * 100 if cell_count > 0 else 0
            matrix_stats[cat][snr] = {"wer": avg_wer, "em": avg_em, "count": cell_count}
            
    # Determine the model's limits
    # We define "acceptable capability threshold" as having an average WER below 0.15 (15% WER)
    capable_snrs = []
    for snr in snrs:
        if snr_stats[snr]["wer"] <= 0.15:
            capable_snrs.append(snr)
            
    if capable_snrs:
        capability_statement = f"Gemma-4-E2B is capable of accepting noise levels at **{min(capable_snrs)} dB and above** (maintaining an average WER below 15%)."
    else:
        # Find the best performing SNR
        best_snr = min(snrs, key=lambda s: snr_stats[s]["wer"])
        capability_statement = (
            f"Under the tested conditions, Gemma-4-E2B did not achieve a WER below 15% at any SNR level. "
            f"Its best performance was at **{best_snr} dB** with a WER of **{snr_stats[best_snr]['wer'] * 100:.2f}%**."
        )

    # Print sample errors for the report
    errors = [r for r in valid_results if r["exact_match"] == 0]
    sample_errors = random.sample(errors, min(len(errors), 10)) if errors else []

    # Write Markdown Report
    with open(REPORT_MD, 'w', encoding='utf-8') as f:
        f.write("# Gemma-4-E2B Speech Transcription Noise Robustness Report\n\n")
        f.write(f"**Date Executed:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Samples Evaluated:** {total_valid} / 1000\n\n")
        
        f.write("## Executive Summary\n")
        f.write(f"This report evaluates the noise-tolerance capabilities of **Gemma-4-E2B** using short voice segments mixed with 10 noise types at 4 SNR levels (0dB, 5dB, 10dB, 15dB).\n\n")
        f.write(f"- **Overall Word Error Rate (WER):** {avg_wer_overall * 100:.2f}%\n")
        f.write(f"- **Overall Exact Match (EM) Accuracy:** {avg_em_overall:.2f}%\n\n")
        f.write(f"### Model Capability Statement\n")
        f.write(f"> {capability_statement}\n\n")
        
        # SNR stats table
        f.write("## Performance by Signal-to-Noise Ratio (SNR)\n")
        f.write("Lower SNR indicates higher levels of background noise.\n\n")
        f.write("| SNR Level | Sample Count | Word Error Rate (WER) | Exact Match (EM) Accuracy |\n")
        f.write("| :---: | :---: | :---: | :---: |\n")
        for snr in snrs:
            f.write(f"| {snr} dB | {snr_stats[snr]['count']} | {snr_stats[snr]['wer'] * 100:.2f}% | {snr_stats[snr]['em']:.2f}% |\n")
        f.write("\n")
        
        # Category stats table
        f.write("## Performance by Noise Category\n\n")
        f.write("| Noise Category | Sample Count | Word Error Rate (WER) | Exact Match (EM) Accuracy |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for cat in categories:
            f.write(f"| {cat.capitalize()} | {category_stats[cat]['count']} | {category_stats[cat]['wer'] * 100:.2f}% | {category_stats[cat]['em']:.2f}% |\n")
        f.write("\n")
        
        # Matrix table
        f.write("## Performance Matrix (WER / EM Accuracy)\n\n")
        f.write("| Noise Category | 15 dB | 10 dB | 5 dB | 0 dB |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for cat in categories:
            row_parts = []
            for snr in [15, 10, 5, 0]:
                cell = matrix_stats[cat].get(snr, {"wer": 1.0, "em": 0.0})
                row_parts.append(f"{cell['wer'] * 100:.1f}% / {cell['em']:.1f}%")
            f.write(f"| {cat.capitalize()} | " + " | ".join(row_parts) + " |\n")
        f.write("\n")
        
        # Sample errors section
        f.write("## Sample Discrepancies / Errors\n")
        f.write("Here are some examples where Gemma-4's prediction diverged from the ground truth:\n\n")
        f.write("| File | Category | SNR | Ground Truth | Gemma-4 Prediction | WER |\n")
        f.write("| :--- | :--- | :---: | :--- | :--- | :---: |\n")
        for err in sample_errors:
            f.write(f"| {err['filename']} | {err['category']} | {err['snr']} dB | \"{err['ground_truth']}\" | \"{err['prediction']}\" | {err['wer'] * 100:.1f}% |\n")
            
    print(f"Consolidated performance report written to: {REPORT_MD}")


if __name__ == "__main__":
    run_evaluation()
