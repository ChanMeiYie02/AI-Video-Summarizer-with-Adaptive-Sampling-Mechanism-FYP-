# Evaluation Report: Multimodal Pipeline Performance Matrix

**Video Title/File:** How Every Child can Thrive by Five
**Duration:** 7m 42s (462.38 seconds)
**Date Executed:** 2026-07-26 19:56:12

## Experiment Configuration Matrix
This table details the processing metrics under 12 combinations of batch sizes and frame filtering granularities.

| Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | Peak VRAM (MB) | Net VRAM (MB) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | LOW | 2 | SUCCESS | 1849 | 0 | 24 | 309.65s | 17815 MB | 12968 MB |
| 2 | LOW | 8 | SUCCESS | 1849 | 0 | 24 | 223.10s | 22131 MB | 17291 MB |
| 3 | LOW | 16 | SUCCESS | 1849 | 0 | 24 | 207.02s | 27705 MB | 22863 MB |
| 4 | LOW | 32 | SUCCESS | 1849 | 0 | 24 | 206.68s | 27706 MB | 22864 MB |
| 5 | MEDIUM | 2 | SUCCESS | 1849 | 0 | 45 | 377.10s | 18313 MB | 13473 MB |
| 6 | MEDIUM | 8 | SUCCESS | 1849 | 0 | 45 | 241.84s | 25274 MB | 20434 MB |
| 7 | MEDIUM | 16 | SUCCESS | 1849 | 0 | 45 | 216.53s | 34464 MB | 29623 MB |
| 8 | MEDIUM | 32 | SUCCESS | 1849 | 0 | 45 | 220.45s | 34468 MB | 29627 MB |
| 9 | HIGH | 2 | SUCCESS | 1849 | 0 | 83 | 402.83s | 18322 MB | 13477 MB |
| 10 | HIGH | 8 | SUCCESS | 1849 | 0 | 83 | 256.99s | 27811 MB | 22967 MB |
| 11 | HIGH | 16 | SUCCESS | 1849 | 0 | 83 | 233.65s | 40555 MB | 35710 MB |
| 12 | HIGH | 32 | SUCCESS | 1849 | 0 | 83 | 233.37s | 40556 MB | 35712 MB |

## 🔍 Key Performance Insights
- **Maximum Speedup:** The fastest run was **Granularity=LOW (Batch=32)** completing in **206.68 seconds**.
- **Maximum Latency:** The slowest run was **Granularity=HIGH (Batch=2)** taking **402.83 seconds**.
- **VRAM Footprint Peak:** The highest memory usage was recorded at **40556 MB** (Net pipeline allocation: **35712 MB**).

## 📂 Preserved Outputs Location
All outputs, final summaries, timelines, and visualization charts are archived in the experiments output directory:
- [Experiments Directory](file:///C:/Users/admin/Desktop/Meiyie/evaluation/results/experiments)
