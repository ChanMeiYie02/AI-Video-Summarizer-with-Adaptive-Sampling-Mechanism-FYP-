# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** How to clean a Laptops Cooling fans!
**Duration:** 8m 35s (515.32 seconds)
**Date Executed:** 2026-07-26 17:13:26

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 2061 | 35 | 12 | 354.08s | 16735 MB | 11922 MB |
| 2 | LOW | 8 | SUCCESS | 2061 | 35 | 12 | 275.62s | 18570 MB | 13738 MB |
| 3 | LOW | 16 | SUCCESS | 2061 | 35 | 12 | 245.03s | 20990 MB | 16158 MB |
| 4 | LOW | 32 | SUCCESS | 2061 | 35 | 12 | 215.90s | 22132 MB | 17300 MB |
| 5 | MEDIUM | 2 | SUCCESS | 2061 | 0 | 20 | 365.70s | 17804 MB | 12970 MB |
| 6 | MEDIUM | 8 | SUCCESS | 2061 | 35 | 20 | 265.16s | 20623 MB | 15790 MB |
| 7 | MEDIUM | 16 | SUCCESS | 2061 | 35 | 20 | 240.57s | 25205 MB | 20373 MB |
| 8 | MEDIUM | 32 | SUCCESS | 2061 | 35 | 20 | 212.28s | 26321 MB | 21486 MB |
| 9 | HIGH | 2 | SUCCESS | 2061 | 0 | 28 | 356.83s | 17805 MB | 12972 MB |
| 10 | HIGH | 8 | SUCCESS | 2061 | 35 | 28 | 258.21s | 22648 MB | 17813 MB |
| 11 | HIGH | 16 | SUCCESS | 2061 | 0 | 28 | 239.57s | 28721 MB | 23850 MB |
| 12 | HIGH | 32 | SUCCESS | 2061 | 35 | 28 | 236.77s | 30339 MB | 25488 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=MEDIUM (Batch=32)** completing in **212.28 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=MEDIUM (Batch=2)** taking **365.70 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **30339 MB** (Net pipeline allocation: **25488 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
