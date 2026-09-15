import os
import re

EXP_DIR = r"evaluation\results"
files = [f for f in os.listdir(EXP_DIR) if f.endswith("experiment_report.md")]

for fname in files:
    fpath = os.path.join(EXP_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"\n======================================")
    print(f"File: {fname}")
    print(f"======================================")
    
    # Parse rows: | Run | Granularity | Batch Size | Status | Frames Extracted | TransNetV2 Scenes | Keyframes | Processing Time (s) | ...
    # Match lines like: | 1 | LOW | 2 | SUCCESS | ... | 939.67s | ...
    pattern = r"\|\s*\d+\s*\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*\w+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*([\d\.]+)s"
    matches = re.findall(pattern, content)
    
    # Group times by batch size
    bs_groups = {}
    for granularity, bs, duration_s in matches:
        bs = int(bs)
        dur = float(duration_s)
        if bs not in bs_groups:
            bs_groups[bs] = []
        bs_groups[bs].append((granularity, dur))
        
    for bs, items in sorted(bs_groups.items()):
        avg_s = sum(d for g, d in items) / len(items)
        avg_m = avg_s / 60.0
        print(f"  Batch Size {bs}: count={len(items)}, average={avg_m:.2f} minutes ({avg_s:.2f} seconds)")
        for g, d in items:
            print(f"    - {g}: {d/60.0:.2f}m ({d:.2f}s)")
