# VT-SSum Benchmark Evaluation Results

**Date:** 2026-05-07 20:51:21  
**Samples Evaluated:** 5  
**Pipeline:** Meiyie (Steps 7-10: Embedding → Clustering → LLM Summary → Map-Reduce)  

## Aggregate Scores

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| rouge1_f1 | 0.2419 | 0.0968 | 0.2921 |
| rouge2_f1 | 0.0346 | 0.0173 | 0.0714 |
| rougeL_f1 | 0.1197 | 0.0717 | 0.1573 |

## Notes

- **Reference:** VT-SSum extractive ground truth (sentences with label=1)
- **Prediction:** Meiyie abstractive summary (final_summary.md)
- **Task mismatch:** Extractive vs abstractive summarization — ROUGE scores may be lower than extractive baselines by nature.
