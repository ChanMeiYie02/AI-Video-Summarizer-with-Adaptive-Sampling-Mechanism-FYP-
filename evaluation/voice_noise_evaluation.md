# Voice Noise Evaluation Plan

We will evaluate the speech transcription capabilities of the **Gemma-4-E2B** multimodal model under various acoustic noise conditions.

---

## Goal Description

We want to assess how well **Gemma-4-E2B** transcribes noisy audio using a dataset of 11,572 samples across 10 noise categories (Babble, Cafeteria, Car, Kitchen, Meeting, Metro, Restaurant, SSN, Station, Traffic) and 4 Signal-to-Noise Ratio (SNR) levels (0, 5, 10, 15 dB).

### Steps:
1. **Deterministic Sampling**: Read `log_trainset_28spk.txt` to identify the noise type and SNR of each file. Sample exactly 100 files for each of the 10 noise categories (total 1,000 files) with a balanced distribution across the SNR levels (0, 5, 10, 15 dB), which means 25 samples per SNR level per category.
2. **Ground Truth Validation**: Check that the corresponding ground truth `.txt` file exists in `trainset_28spk_txt` for each sampled audio file.
3. **Model Inference**: Load `google/gemma-4-E2B-it` natively on GPU and process each audio clip to extract the transcribed text.
4. **Accuracy Evaluation**: Compare Gemma-4's predictions against the ground truth transcriptions using two metrics:
   - **Exact Match (EM)**: Percent of transcriptions that match exactly (after text normalization).
   - **Word Error Rate (WER)**: Standard edit-distance word error rate.
5. **SNR Analysis**: Break down results by SNR level to determine the minimum SNR level where Gemma-4-E2B maintains high accuracy.

---

## Proposed Changes

We will create a new evaluation script:

### [NEW] [run_voice_noise_evaluation.py](file:///c:/Users/admin/Desktop/Meiyie/evaluation/run_voice_noise_evaluation.py)
This Python script will:
- Read `log_trainset_28spk.txt` and filter files.
- Randomly sample 100 files per category (25 per SNR level) using a fixed random seed for reproducibility.
- Load the model natively onto GPU.
- Loop through the selected files, transcribe them, calculate WER and Exact Match, and save incremental results in `evaluation/results/voice_noise_runs/`.
- Print a consolidated markdown report summarizing accuracy metrics for each noise type and SNR level, identifying the model's capabilities and limits.

---

## Verification Plan

### Automated Verification
- We will execute the script using the virtual environment:
  ```powershell
  & vts\Scripts\python.exe evaluation\run_voice_noise_evaluation.py
  ```
- Verify the generated markdown report and the compiled stats JSON file at `evaluation/results/voice_noise_report.md`.
