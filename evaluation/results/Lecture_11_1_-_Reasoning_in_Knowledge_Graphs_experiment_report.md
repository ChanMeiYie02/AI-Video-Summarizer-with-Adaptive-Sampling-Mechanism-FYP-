# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** Lecture 11.1 - Reasoning in Knowledge Graphs
**Duration:** 16m 52s (1012.11 seconds)
**Date Executed:** 2026-07-27 03:40:53

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 4048 | 8 | 3 | 339.53s | 14157 MB | 10905 MB |
| 2 | LOW | 8 | SUCCESS | 4048 | 8 | 3 | 256.93s | 15210 MB | 11951 MB |
| 3 | LOW | 16 | SUCCESS | 4048 | 8 | 3 | 231.39s | 16828 MB | 13559 MB |
| 4 | LOW | 32 | SUCCESS | 4048 | 8 | 3 | 238.73s | 20283 MB | 17018 MB |
| 5 | MEDIUM | 2 | SUCCESS | 4048 | 8 | 4 | 330.30s | 14654 MB | 11395 MB |
| 6 | MEDIUM | 8 | SUCCESS | 4048 | 8 | 4 | 256.59s | 15496 MB | 12230 MB |
| 7 | MEDIUM | 16 | SUCCESS | 4048 | 8 | 4 | 226.82s | 17244 MB | 13965 MB |
| 8 | MEDIUM | 32 | SUCCESS | 4048 | 8 | 4 | 232.15s | 21778 MB | 18501 MB |
| 9 | HIGH | 2 | SUCCESS | 4048 | 8 | 4 | 326.13s | 14665 MB | 11387 MB |
| 10 | HIGH | 8 | SUCCESS | 4048 | 8 | 4 | 251.82s | 15499 MB | 12222 MB |
| 11 | HIGH | 16 | SUCCESS | 4048 | 8 | 4 | 220.58s | 17241 MB | 13963 MB |
| 12 | HIGH | 32 | SUCCESS | 4048 | 8 | 4 | 229.35s | 21775 MB | 18498 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=HIGH (Batch=16)** completing in **220.58 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=LOW (Batch=2)** taking **339.53 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **21778 MB** (Net pipeline allocation: **18501 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
