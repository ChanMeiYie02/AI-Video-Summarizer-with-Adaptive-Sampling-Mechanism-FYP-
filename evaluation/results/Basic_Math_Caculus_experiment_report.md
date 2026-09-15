# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** Basic Math Caculus
**Duration:** 8m 19s (499.44 seconds)
**Date Executed:** 2026-07-26 18:25:19

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 1997 | 20 | 7 | 301.10s | 16812 MB | 11960 MB |
| 2 | LOW | 8 | SUCCESS | 1997 | 20 | 7 | 257.28s | 17471 MB | 12613 MB |
| 3 | LOW | 16 | SUCCESS | 1997 | 0 | 7 | 236.98s | 19532 MB | 14669 MB |
| 4 | LOW | 32 | SUCCESS | 1997 | 20 | 7 | 209.25s | 20472 MB | 15609 MB |
| 5 | MEDIUM | 2 | SUCCESS | 1997 | 20 | 11 | 355.37s | 17299 MB | 12438 MB |
| 6 | MEDIUM | 8 | SUCCESS | 1997 | 20 | 11 | 256.78s | 18153 MB | 13295 MB |
| 7 | MEDIUM | 16 | SUCCESS | 1997 | 20 | 11 | 240.87s | 19674 MB | 14821 MB |
| 8 | MEDIUM | 32 | SUCCESS | 1997 | 20 | 11 | 210.34s | 21797 MB | 16943 MB |
| 9 | HIGH | 2 | SUCCESS | 1997 | 20 | 13 | 341.94s | 17295 MB | 12441 MB |
| 10 | HIGH | 8 | SUCCESS | 1997 | 20 | 13 | 249.14s | 18585 MB | 13731 MB |
| 11 | HIGH | 16 | SUCCESS | 1997 | 20 | 13 | 252.30s | 20071 MB | 15310 MB |
| 12 | HIGH | 32 | SUCCESS | 1997 | 0 | 13 | 222.21s | 22300 MB | 17501 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=LOW (Batch=32)** completing in **209.25 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=MEDIUM (Batch=2)** taking **355.37 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **22300 MB** (Net pipeline allocation: **17501 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
