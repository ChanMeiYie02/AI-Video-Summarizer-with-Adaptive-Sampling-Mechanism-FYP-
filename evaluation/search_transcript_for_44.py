import os
import json

EXP_DIR = r"evaluation\results\experiments\Long_Form_Video\The_50_Easiest_3-Ingredient_Recipes_high_batch_2"
TRANSCRIPT_PATH = os.path.join(EXP_DIR, "The_50_Easiest_3-Ingredient_Recipes_high_batch_2_transcript.json")

with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
    transcript = json.load(f)

for idx, chunk in enumerate(transcript):
    text = chunk["text"]
    if "44" in text or "forty-four" in text.lower():
        print(f"Chunk #{idx} ({idx*29}s): {text}")
