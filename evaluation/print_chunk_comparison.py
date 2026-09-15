import os
import json

EXP_DIR = r"evaluation\results\experiments\Long_Form_Video"
batch2_path = os.path.join(EXP_DIR, "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_2", "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_2_transcript.json")
batch32_path = os.path.join(EXP_DIR, "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_32", "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_32_transcript.json")

with open(batch2_path, 'r', encoding='utf-8') as f:
    b2 = json.load(f)
with open(batch32_path, 'r', encoding='utf-8') as f:
    b32 = json.load(f)

print("Batch 2 Chunk 10:")
print(b2[10]["text"])
print("\nBatch 32 Chunk 10:")
print(b32[10]["text"])
