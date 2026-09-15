# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** AI and human evolution
**Duration:** 25m 40s (1540.04 seconds)
**Date Executed:** 2026-07-27 04:53:57

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 6160 | 57 | 2 | 452.50s | 14156 MB | 10879 MB |
| 2 | LOW | 8 | SUCCESS | 6160 | 57 | 2 | 321.65s | 15226 MB | 11947 MB |
| 3 | LOW | 16 | SUCCESS | 6160 | 57 | 2 | 318.82s | 17320 MB | 14043 MB |
| 4 | LOW | 32 | SUCCESS | 6160 | 57 | 2 | 286.87s | 21014 MB | 17737 MB |
| 5 | MEDIUM | 2 | SUCCESS | 6160 | 57 | 5 | 464.28s | 14167 MB | 10887 MB |
| 6 | MEDIUM | 8 | SUCCESS | 6160 | 57 | 5 | 320.79s | 15227 MB | 11950 MB |
| 7 | MEDIUM | 16 | SUCCESS | 6160 | 57 | 5 | 307.27s | 17318 MB | 14039 MB |
| 8 | MEDIUM | 32 | SUCCESS | 6160 | 57 | 5 | 298.81s | 20304 MB | 17026 MB |
| 9 | HIGH | 2 | SUCCESS | 6160 | 57 | 10 | 513.25s | 14656 MB | 11377 MB |
| 10 | HIGH | 8 | SUCCESS | 6160 | 57 | 10 | 376.35s | 15112 MB | 11834 MB |
| 11 | HIGH | 16 | SUCCESS | 6160 | 57 | 10 | 355.94s | 16662 MB | 13383 MB |
| 12 | HIGH | 32 | SUCCESS | 6160 | 57 | 10 | 319.94s | 19522 MB | 16245 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=LOW (Batch=32)** completing in **286.87 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=HIGH (Batch=2)** taking **513.25 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **21014 MB** (Net pipeline allocation: **17737 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
