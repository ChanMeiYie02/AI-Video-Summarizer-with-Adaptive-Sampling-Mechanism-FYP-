# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** AMD Advancing AI 2026: Lisa Su Full Keynote
**Duration:** 131m 7s (7867.04 seconds)
**Date Executed:** 2026-07-27 15:19:08

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 31468 | 490 | 16 | 1928.86s | 14768 MB | 11396 MB |
| 2 | LOW | 8 | SUCCESS | 31468 | 490 | 16 | 1207.27s | 15443 MB | 12073 MB |
| 3 | LOW | 16 | SUCCESS | 31468 | 490 | 16 | 1075.92s | 17642 MB | 14272 MB |
| 4 | LOW | 32 | SUCCESS | 31468 | 490 | 16 | 1228.01s | 21885 MB | 18510 MB |
| 5 | MEDIUM | 2 | SUCCESS | 31468 | 490 | 76 | 3029.88s | 16845 MB | 13464 MB |
| 6 | MEDIUM | 8 | SUCCESS | 31468 | 490 | 76 | 1481.95s | 19164 MB | 15776 MB |
| 7 | MEDIUM | 16 | SUCCESS | 31468 | 490 | 76 | 1459.52s | 20760 MB | 17369 MB |
| 8 | MEDIUM | 32 | SUCCESS | 31468 | 490 | 76 | 1173.60s | 24259 MB | 20875 MB |
| 9 | HIGH | 2 | SUCCESS | 31468 | 490 | 298 | 3304.92s | 16854 MB | 13470 MB |
| 10 | HIGH | 8 | SUCCESS | 31468 | 490 | 298 | 1923.50s | 22802 MB | 19412 MB |
| 11 | HIGH | 16 | SUCCESS | 31468 | 490 | 298 | 1722.37s | 29259 MB | 25863 MB |
| 12 | HIGH | 32 | SUCCESS | 31468 | 490 | 298 | 1592.56s | 43257 MB | 39855 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=LOW (Batch=16)** completing in **1075.92 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=HIGH (Batch=2)** taking **3304.92 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **43257 MB** (Net pipeline allocation: **39855 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
