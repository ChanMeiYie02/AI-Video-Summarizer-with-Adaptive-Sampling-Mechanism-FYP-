# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** The 50 Easiest 3-Ingredient Recipes
**Duration:** 35m 2s (2102.52 seconds)
**Date Executed:** 2026-07-27 08:04:22

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 8410 | 1277 | 48 | 939.67s | 16243 MB | 12966 MB |
| 2 | LOW | 8 | SUCCESS | 8410 | 1277 | 48 | 614.95s | 18578 MB | 15296 MB |
| 3 | LOW | 16 | SUCCESS | 8410 | 1277 | 48 | 565.26s | 22639 MB | 19360 MB |
| 4 | LOW | 32 | SUCCESS | 8410 | 1277 | 48 | 480.24s | 29146 MB | 25865 MB |
| 5 | MEDIUM | 2 | SUCCESS | 8410 | 1277 | 267 | 1398.62s | 16745 MB | 13468 MB |
| 6 | MEDIUM | 8 | SUCCESS | 8410 | 1277 | 267 | 788.16s | 25727 MB | 22447 MB |
| 7 | MEDIUM | 16 | SUCCESS | 8410 | 1277 | 267 | 675.08s | 36946 MB | 33667 MB |
| 8 | MEDIUM | 32 | SUCCESS | 8410 | 1277 | 267 | 759.56s | 48285 MB | 45012 MB |
| 9 | HIGH | 2 | SUCCESS | 8410 | 1277 | 965 | 1436.33s | 16744 MB | 13472 MB |
| 10 | HIGH | 8 | SUCCESS | 8410 | 1277 | 965 | 828.60s | 26233 MB | 22962 MB |
| 11 | HIGH | 16 | SUCCESS | 8410 | 1277 | 965 | 691.04s | 38977 MB | 35708 MB |
| 12 | HIGH | 32 | SUCCESS | 8410 | 1277 | 965 | 2168.78s | 48255 MB | 44982 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=LOW (Batch=32)** completing in **480.24 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=HIGH (Batch=32)** taking **2168.78 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **48285 MB** (Net pipeline allocation: **45012 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
