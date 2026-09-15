import os
import json

EXP_DIR = r"evaluation\results\experiments\Long_Form_Video"
batch2_path = os.path.join(EXP_DIR, "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_2", "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_2_transcript.json")
batch32_path = os.path.join(EXP_DIR, "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_32", "AMD_Advancing_AI_2026__Lisa_Su_Full_Keynote_high_batch_32_transcript.json")

with open(batch2_path, 'r', encoding='utf-8') as f:
    b2 = json.load(f)
with open(batch32_path, 'r', encoding='utf-8') as f:
    b32 = json.load(f)

print("Comparing generated transcripts for Chunk #10 and Chunk #20:")
for chunk_id in [10, 20]:
    txt_b2 = b2[chunk_id]["text"]
    txt_b32 = b32[chunk_id]["text"]
    
    print(f"\n======================================")
    print(f"Chunk #{chunk_id}")
    print(f"======================================")
    print(f"Batch Size 2  : {txt_b2[:120]}...")
    print(f"Batch Size 32 : {txt_b32[:120]}...")
    if len(txt_b2) != len(txt_b32):
        print(f"WARNING: Length mismatch! Batch 2 length: {len(txt_b2)}, Batch 32 length: {len(txt_b32)}")
