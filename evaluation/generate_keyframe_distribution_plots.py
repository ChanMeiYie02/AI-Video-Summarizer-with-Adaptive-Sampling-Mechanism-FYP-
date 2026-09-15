import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Paths
RESULTS_DIR = r"evaluation\results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Find all experiment reports
report_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("experiment_report.md")]

data = []

# Parse the reports
for fname in report_files:
    fpath = os.path.join(RESULTS_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract Title
    title_match = re.search(r"\*\*Video Title/File:\*\*\s*(.+)", content)
    if not title_match:
        continue
    video_title = title_match.group(1).strip()
    # Shorten title for readability on plot
    if "Cyberdeck" in video_title:
        short_title = "Powerful Cyberdeck"
    else:
        short_title = video_title[:25] + "..." if len(video_title) > 25 else video_title
    
    # Parse rows: | Run | Granularity | Batch Size | Status | ... | Keyframes | ...
    # Match rows like: | 1 | LOW | 2 | SUCCESS | 8410 | 1277 | 48 | ...
    pattern = r"\|\s*\d+\s*\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*\w+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+)\s*\|"
    matches = re.findall(pattern, content)
    
    for granularity, bs, keyframes in matches:
        data.append({
            "Video": short_title,
            "Granularity": granularity,
            "Batch Size": int(bs),
            "Keyframes": int(keyframes)
        })

# Create DataFrame
df = pd.DataFrame(data)

if df.empty:
    print("Error: No data found to plot!")
    exit(1)

# Group by Video and Granularity (since keyframes count is constant across Batch Sizes)
grouped = df.groupby(["Video", "Granularity"])["Keyframes"].first().unstack(fill_value=0)

# Sort videos by High granularity count descending
grouped = grouped.sort_values(by="HIGH", ascending=False)

# Ensure columns are in order
modes = ["LOW", "MEDIUM", "HIGH"]
grouped = grouped[modes]

# Plotting Grouped Bar Chart
fig, ax = plt.subplots(figsize=(12, 7))

x = np.arange(len(grouped))
width = 0.25

rects1 = ax.bar(x - width, grouped["LOW"], width, label="LOW Mode", color="#93c5fd")  # Soft blue
rects2 = ax.bar(x, grouped["MEDIUM"], width, label="MEDIUM Mode", color="#3b82f6")  # Blue
rects3 = ax.bar(x + width, grouped["HIGH"], width, label="HIGH Mode", color="#1e3a8a")  # Dark blue

# Add labels, title and custom x-axis tick labels
ax.set_ylabel("Number of Keyframes Extracted", fontsize=12, fontweight="bold", labelpad=10)
ax.set_title("Keyframe Distribution Across Benchmark Videos by Granularity Mode\n(Independent of Inference Batch Size)", fontsize=14, fontweight="bold", pad=20)
ax.set_xticks(x)
ax.set_xticklabels(grouped.index, rotation=35, ha="right", fontsize=9)
ax.legend(fontsize=11, loc="upper right")
ax.grid(True, axis="y", linestyle="--", alpha=0.3)

# Add values on top of bars
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        if height > 0:
            ax.annotate(f"{height}",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.tight_layout()

# Save plot
output_path = os.path.join(RESULTS_DIR, "keyframe_distribution_by_mode.png")
plt.savefig(output_path, dpi=150)
plt.close()

print(f"Successfully generated keyframe distribution plot at: {output_path}")
