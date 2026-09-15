# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** I Built the Most Powerful Cyberdeck in the World
**Duration:** 20m 28s (1228.13 seconds)
**Date Executed:** 2026-07-27 02:47:43

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 4912 | 541 | 115 | 929.57s | 17000 MB | 12000 MB |
| 2 | LOW | 8 | SUCCESS | 4912 | 541 | 115 | 543.77s | 19000 MB | 14000 MB |
| 3 | LOW | 16 | SUCCESS | 4912 | 541 | 115 | 417.27s | 21000 MB | 16000 MB |
| 4 | LOW | 32 | SUCCESS | 4912 | 541 | 115 | 420.47s | 48365 MB | 44925 MB |
| 5 | MEDIUM | 2 | SUCCESS | 4912 | 541 | 304 | 972.30s | 16834 MB | 13675 MB |
| 6 | MEDIUM | 8 | SUCCESS | 4912 | 541 | 304 | 551.68s | 26300 MB | 22991 MB |
| 7 | MEDIUM | 16 | SUCCESS | 4912 | 541 | 304 | 438.38s | 39068 MB | 35719 MB |
| 8 | MEDIUM | 32 | SUCCESS | 4912 | 541 | 304 | 643.85s | 48235 MB | 44880 MB |
| 9 | HIGH | 2 | SUCCESS | 4912 | 541 | 451 | 951.26s | 16748 MB | 13472 MB |
| 10 | HIGH | 8 | SUCCESS | 4912 | 541 | 451 | 548.40s | 26238 MB | 22962 MB |
| 11 | HIGH | 16 | SUCCESS | 4912 | 541 | 451 | 463.89s | 38982 MB | 35708 MB |
| 12 | HIGH | 32 | SUCCESS | 4912 | 541 | 451 | 1205.69s | 48265 MB | 44980 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=LOW (Batch=16)** completing in **417.27 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=HIGH (Batch=32)** taking **1205.69 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **48365 MB** (Net pipeline allocation: **44925 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
