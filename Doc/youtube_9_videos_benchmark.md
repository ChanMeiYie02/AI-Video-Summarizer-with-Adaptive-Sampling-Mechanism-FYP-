# 📹 9-Video YouTube Multimodal Benchmark Dataset

This document details the **9-Video YouTube Multimodal Benchmark Dataset**, categorizing videos by **Video Duration Tier** (Short, Medium, Long) and **Video Presentation Type** (Narrative/FPP, Narrative+Slide, Presentation/TPP). 

It presents full empirical benchmark results evaluating **Extracted Frames**, **Processing Time**, and **VRAM Usage** across 3 Frame Filtering Granularity Modes (**Low**, **Medium**, **High**) and 4 Batch Sizes (**BS=2**, **BS=8**, **BS=16**, **BS=32**).

---

## 1. 🎬 9-Video Dataset Classification Matrix

| Duration Tier | Video Duration | Video Presentation Type | Video Title & YouTube URL | Exact Duration |
|:---:|:---:|:---:|:---|:---:|
| **Short Form** | `< 10 mins` | **Narrative & FPP** | [How to clean a Laptops Cooling fans!](https://youtu.be/J1KlRklVGMk?si=-E7NljEmlHB8skfV) | 8 mins 35 s |
| **Short Form** | `< 10 mins` | **Narrative + Slide** | [Basic Math Calculus](https://youtu.be/IFlXeFwA_2A?si=xO1f2ZUL_mK2MgDj) | 8 mins 19 s |
| **Short Form** | `< 10 mins` | **Presentation & TPP** | [How Every Child can Thrive by Five](https://youtu.be/aISXCw0Pi94?si=Uzdd4S6gCHFC1x32) | 7 mins 42 s |
| **Medium Form** | `10 – 30 mins` | **Narrative & FPP** | [I Built the Most Powerful Cyberdeck in the World](https://youtu.be/mwdgtGI5G84?si=cwGFqZIMLx1GOEsM) | 20 mins 28 s |
| **Medium Form** | `10 – 30 mins` | **Narrative + Slide** | [Lecture 11.1 – Reasoning in Knowledge Graphs](https://youtu.be/X9yl0pTP9fY?si=Usz0SZbLErmDi_S_) | 16 mins 52 s |
| **Medium Form** | `10 – 30 mins` | **Presentation & TPP** | [AI and human evolution](https://youtu.be/jt3Ul3rPXaE?si=I_72ly2xroly8xlX) | 25 mins 40 s |
| **Long Form** | `>= 30 mins` | **Narrative & FPP** | [The 50 Easiest 3-Ingredient Recipes](https://youtu.be/WcGYBX6Ucvg?si=jfYFpGtPrnkb2dXV) | 35 mins 02 s |
| **Long Form** | `>= 30 mins` | **Narrative + Slide** | [Lecture 10.3 - Knowledge Graph Completion Algorithms](https://youtu.be/Xm5VrxZYhu4?si=JNSIbmuamUEfwTzB) | 34 mins 30 s |
| **Long Form** | `>= 30 mins` | **Presentation & TPP** | [AMD Advancing AI 2026: Lisa Su Full Keynote](https://www.youtube.com/live/jvtPC28nGsc?si=wH3lNI1VQUP26pk_) | 2 hours 11 mins |

---

## 2. 📊 Detailed Performance Benchmark Matrix

### 🟢 1. Short-Form Videos (< 10 Minutes)

#### Video 1: How to clean a Laptops Cooling fans! (8m 35s | Narrative & FPP)
- **YouTube URL:** https://youtu.be/J1KlRklVGMk?si=-E7NljEmlHB8skfV

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **12** | **Processing Time** | 5 mins 54 s | 4 mins 35 s | 4 mins 05 s | 3 mins 35 s |
| | | **VRAM Usage** | 16.73 GB | 18.57 GB | 20.99 GB | 22.13 GB |
| **Medium Mode** | **20** | **Processing Time** | 6 mins 05 s | 4 mins 25 s | 4 mins 01 s | 3 mins 32 s |
| | | **VRAM Usage** | 17.80 GB | 20.62 GB | 25.21 GB | 26.32 GB |
| **High Mode** | **28** | **Processing Time** | 5 mins 56 s | 4 mins 18 s | 3 mins 59 s | 3 mins 56 s |
| | | **VRAM Usage** | 17.81 GB | 22.65 GB | 28.72 GB | 30.34 GB |

---

#### Video 2: Basic Math Calculus (8m 19s | Narrative + Slide)
- **YouTube URL:** https://youtu.be/IFlXeFwA_2A?si=xO1f2ZUL_mK2MgDj

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **7** | **Processing Time** | 5 mins 01 s | 4 mins 17 s | 3 mins 57 s | 3 mins 29 s |
| | | **VRAM Usage** | 16.81 GB | 17.47 GB | 19.53 GB | 20.47 GB |
| **Medium Mode** | **11** | **Processing Time** | 5 mins 55 s | 4 mins 17 s | 4 mins 01 s | 3 mins 30 s |
| | | **VRAM Usage** | 17.30 GB | 18.15 GB | 19.67 GB | 21.80 GB |
| **High Mode** | **13** | **Processing Time** | 5 mins 42 s | 4 mins 09 s | 4 mins 12 s | 3 mins 42 s |
| | | **VRAM Usage** | 17.30 GB | 18.59 GB | 20.07 GB | 22.30 GB |

---

#### Video 3: How Every Child can Thrive by Five (7m 42s | Presentation & TPP)
- **YouTube URL:** https://youtu.be/aISXCw0Pi94?si=Uzdd4S6gCHFC1x32

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **24** | **Processing Time** | 5 mins 09 s | 3 mins 43 s | 3 mins 27 s | 3 mins 26 s |
| | | **VRAM Usage** | 17.81 GB | 22.13 GB | 27.70 GB | 27.70 GB |
| **Medium Mode** | **45** | **Processing Time** | 6 mins 17 s | 4 mins 01 s | 3 mins 36 s | 3 mins 40 s |
| | | **VRAM Usage** | 18.31 GB | 25.27 GB | 34.46 GB | 34.47 GB |
| **High Mode** | **83** | **Processing Time** | 6 mins 42 s | 4 mins 17 s | 3 mins 53 s | 3 mins 53 s |
| | | **VRAM Usage** | 18.32 GB | 27.81 GB | 40.55 GB | 40.55 GB |

---

### 🟡 2. Medium-Form Videos (10 – 30 Minutes)

#### Video 4: I Built the Most Powerful Cyberdeck in the World (20m 28s | Narrative & FPP)
- **YouTube URL:** https://youtu.be/mwdgtGI5G84?si=cwGFqZIMLx1GOEsM

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **115** | **Processing Time** | 15 mins 29 s | 9 mins 03 s | 6 mins 27 s | 7 mins 00 s |
| | | **VRAM Usage** | 17.00 GB | 19.00 GB | 21.00 GB | 48.36 GB |
| **Medium Mode** | **304** | **Processing Time** | 16 mins 12 s | 9 mins 11 s | 7 mins 18 s | 10 mins 43 s |
| | | **VRAM Usage** | 16.83 GB | 26.30 GB | 39.06 GB | 48.23 GB |
| **High Mode** | **451** | **Processing Time** | 15 mins 51 s | 9 mins 08 s | 7 mins 43 s | 20 mins 05 s |
| | | **VRAM Usage** | 16.75 GB | 26.24 GB | 39.98 GB | 48.27 GB |

---

#### Video 5: Lecture 11.1 – Reasoning in Knowledge Graphs (16m 52s | Narrative + Slide)
- **YouTube URL:** https://youtu.be/X9yl0pTP9fY?si=Usz0SZbLErmDi_S_

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **3** | **Processing Time** | 5 mins 39 s | 4 mins 16 s | 3 mins 51 s | 3 mins 58 s |
| | | **VRAM Usage** | 14.15 GB | 15.21 GB | 16.82 GB | 20.28 GB |
| **Medium Mode** | **4** | **Processing Time** | 5 mins 30 s | 4 mins 16 s | 3 mins 46 s | 3 mins 52 s |
| | | **VRAM Usage** | 14.65 GB | 15.50 GB | 17.24 GB | 21.78 GB |
| **High Mode** | **4** | **Processing Time** | 5 mins 26 s | 4 mins 11 s | 3 mins 40 s | 3 mins 43 s |
| | | **VRAM Usage** | 14.67 GB | 15.50 GB | 17.24 GB | 21.78 GB |

---

#### Video 6: AI and human evolution (25m 40s | Presentation & TPP)
- **YouTube URL:** https://youtu.be/jt3Ul3rPXaE?si=I_72ly2xroly8xlX

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **2** | **Processing Time** | 7 mins 32 s | 5 mins 21 s | 5 mins 18 s | 4 mins 46 s |
| | | **VRAM Usage** | 14.15 GB | 15.22 GB | 17.32 GB | 21.01 GB |
| **Medium Mode** | **5** | **Processing Time** | 7 mins 44 s | 5 mins 20 s | 5 mins 07 s | 4 mins 58 s |
| | | **VRAM Usage** | 14.16 GB | 15.23 GB | 17.32 GB | 20.30 GB |
| **High Mode** | **10** | **Processing Time** | 8 mins 33 s | 6 mins 16 s | 5 mins 55 s | 5 mins 19 s |
| | | **VRAM Usage** | 14.66 GB | 15.11 GB | 16.66 GB | 19.52 GB |

---

### 🔴 3. Long-Form Videos (>= 30 Minutes)

#### Video 7: The 50 Easiest 3-Ingredient Recipes (35m 02s | Narrative & FPP)
- **YouTube URL:** https://youtu.be/WcGYBX6Ucvg?si=jfYFpGtPrnkb2dXV

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **48** | **Processing Time** | 15 mins 39 s | 10 mins 15 s | 9 mins 25 s | 8 mins 00 s |
| | | **VRAM Usage** | 16.24 GB | 18.58 GB | 22.64 GB | 29.15 GB |
| **Medium Mode** | **267** | **Processing Time** | 23 mins 18 s | 13 mins 08 s | 11 mins 15 s | 12 mins 39 s |
| | | **VRAM Usage** | 16.75 GB | 25.73 GB | 36.95 GB | 48.29 GB |
| **High Mode** | **965** | **Processing Time** | 23 mins 56 s | 13 mins 48 s | 11 mins 31 s | 36 mins 08 s |
| | | **VRAM Usage** | 16.74 GB | 26.23 GB | 38.98 GB | 48.26 GB |

---

#### Video 8: Lecture 10.3 - Knowledge Graph Completion Algorithms (34m 30s | Narrative + Slide)
- **YouTube URL:** https://youtu.be/Xm5VrxZYhu4?si=JNSIbmuamUEfwTzB

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **3** | **Processing Time** | 9 mins 05 s | 6 mins 35 s | 5 mins 46 s | 5 mins 19 s |
| | | **VRAM Usage** | 14.14 GB | 15.20 GB | 16.82 GB | 20.27 GB |
| **Medium Mode** | **3** | **Processing Time** | 9 mins 23 s | 6 mins 31 s | 5 mins 42 s | 5 mins 29 s |
| | | **VRAM Usage** | 14.14 GB | 15.19 GB | 16.82 GB | 20.27 GB |
| **High Mode** | **3** | **Processing Time** | 9 mins 01 s | 6 mins 35 s | 6 mins 20 s | 4 mins 52 s |
| | | **VRAM Usage** | 14.14 GB | 15.18 GB | 16.94 GB | 20.40 GB |

---

#### Video 9: AMD Advancing AI 2026: Lisa Su Full Keynote (2h 11m | Presentation & TPP)
- **YouTube URL:** https://www.youtube.com/live/jvtPC28nGsc?si=wH3lNI1VQUP26pk_

| Granularity Mode | Extracted Frames | Metric | Batch Size = 2 | Batch Size = 8 | Batch Size = 16 | Batch Size = 32 |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Low Mode** | **16** | **Processing Time** | 32 mins 13 s | 20 mins 07 s | 17 mins 55 s | 20 mins 28 s |
| | | **VRAM Usage** | 14.77 GB | 15.44 GB | 17.64 GB | 21.89 GB |
| **Medium Mode** | **76** | **Processing Time** | 50 mins 29 s | 24 mins 42 s | 24 mins 19 s | 19 mins 33 s |
| | | **VRAM Usage** | 16.85 GB | 19.16 GB | 20.76 GB | 24.26 GB |
| **High Mode** | **298** | **Processing Time** | 55 mins 04 s | 32 mins 03 s | 28 mins 42 s | 26 mins 32 s |
| | | **VRAM Usage** | 16.85 GB | 22.80 GB | 29.26 GB | 43.26 GB |
