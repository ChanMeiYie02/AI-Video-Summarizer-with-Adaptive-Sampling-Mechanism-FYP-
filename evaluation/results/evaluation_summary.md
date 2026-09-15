# VT-SSum Benchmark Evaluation Results

**Date:** 2026-05-13 20:44:02  
**Samples Evaluated:** 50  
**Pipeline:** Meiyie (Steps 7-10: Embedding → Clustering → LLM Summary → Map-Reduce)  

## Aggregate Scores

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| rouge1_f1 | 0.3311 | 0.0966 | 0.4971 |
| rouge2_f1 | 0.0706 | 0.0048 | 0.2000 |
| rougeL_f1 | 0.1438 | 0.0676 | 0.3306 |
| bertscore_f1 | 0.8215 | 0.7768 | 0.8840 |

## Notes

- **Reference:** VT-SSum extractive ground truth (sentences with label=1)
- **Prediction:** Meiyie abstractive summary (final_summary.md)
- **Task mismatch:** Extractive vs abstractive summarization — ROUGE scores may be lower than extractive baselines by nature.
