# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** Lecture 10.3 - Knowledge Graph Completion Algorithms
**Duration:** 34m 30s (2070.45 seconds)
**Date Executed:** 2026-07-27 09:26:00

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 8282 | 8 | 3 | 545.72s | 14138 MB | 10895 MB |
| 2 | LOW | 8 | SUCCESS | 8282 | 8 | 3 | 395.70s | 15198 MB | 11951 MB |
| 3 | LOW | 16 | SUCCESS | 8282 | 8 | 3 | 346.97s | 16818 MB | 13570 MB |
| 4 | LOW | 32 | SUCCESS | 8282 | 8 | 3 | 319.78s | 20274 MB | 17024 MB |
| 5 | MEDIUM | 2 | SUCCESS | 8282 | 8 | 3 | 563.47s | 14137 MB | 10888 MB |
| 6 | MEDIUM | 8 | SUCCESS | 8282 | 8 | 3 | 391.10s | 15192 MB | 11946 MB |
| 7 | MEDIUM | 16 | SUCCESS | 8282 | 8 | 3 | 342.49s | 16815 MB | 13566 MB |
| 8 | MEDIUM | 32 | SUCCESS | 8282 | 8 | 3 | 329.85s | 20273 MB | 17025 MB |
| 9 | HIGH | 2 | SUCCESS | 8282 | 8 | 3 | 541.66s | 14136 MB | 10901 MB |
| 10 | HIGH | 8 | SUCCESS | 8282 | 8 | 3 | 395.78s | 15182 MB | 11949 MB |
| 11 | HIGH | 16 | SUCCESS | 8282 | 8 | 3 | 380.84s | 16942 MB | 13576 MB |
| 12 | HIGH | 32 | SUCCESS | 8282 | 8 | 3 | 292.70s | 20399 MB | 17027 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=HIGH (Batch=32)** completing in **292.70 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=MEDIUM (Batch=2)** taking **563.47 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **20399 MB** (Net pipeline allocation: **17027 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
