import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Configure paths
RESULTS_DIR = r"evaluation\results\experiments\Noise_Voice_Evaluation"
RESULTS_JSON = os.path.join(RESULTS_DIR, "voice_noise_results.json")
OUTPUT_DIR = RESULTS_DIR

# Load results
with open(RESULTS_JSON, 'r', encoding='utf-8') as f:
    results = json.load(f)

# Group data
categories = sorted(list(set(r["category"] for r in results)))
snrs = sorted(list(set(r["snr"] for r in results))) # [0, 5, 10, 15]

# Generate Heatmap Matrix data
heatmap_data = np.zeros((len(categories), len(snrs)))
for i, cat in enumerate(categories):
    for j, snr in enumerate(snrs):
        subset = [r["wer"] for r in results if r["category"] == cat and r["snr"] == snr]
        heatmap_data[i, j] = np.mean(subset) if subset else 0.0

# Define high-contrast professional color palette
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# ----------------------------------------------------
# 1. Plot Line chart: WER vs SNR for each category
# ----------------------------------------------------
plt.figure(figsize=(11, 7), dpi=300)
for idx, cat in enumerate(categories):
    wer_values = []
    for snr in snrs:
        subset = [r["wer"] for r in results if r["category"] == cat and r["snr"] == snr]
        wer_values.append(np.mean(subset) if subset else 0.0)
    plt.plot(snrs, wer_values, marker='o', linewidth=2, color=colors[idx % len(colors)], label=cat.capitalize())

plt.title("Gemma-4-E2B: Word Error Rate (WER) vs SNR by Noise Type", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Signal-to-Noise Ratio (SNR) in dB", fontsize=12, labelpad=10)
plt.ylabel("Word Error Rate (WER)", fontsize=12, labelpad=10)
plt.xticks(snrs, [f"{s} dB" for s in snrs])
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True, facecolor='white', edgecolor='#e2e2e2')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "voice_noise_wer_by_snr.png"), bbox_inches='tight')
plt.close()

# ----------------------------------------------------
# 2. Plot Heatmap of WER (using pure Matplotlib)
# ----------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
im = ax.imshow(heatmap_data, cmap="YlOrRd", aspect='auto')

# Show all ticks and label them with the respective lists
ax.set_xticks(np.arange(len(snrs)))
ax.set_yticks(np.arange(len(categories)))
ax.set_xticklabels([f"{s} dB" for s in snrs], fontsize=10)
ax.set_yticklabels([c.capitalize() for c in categories], fontsize=10)

# Rotate the tick labels and set their alignment
plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

# Create colorbar
cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.ax.set_ylabel("Word Error Rate (WER)", rotation=-90, va="bottom", fontsize=11, labelpad=15)
cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

# Loop over data dimensions and create text annotations
for i in range(len(categories)):
    for j in range(len(snrs)):
        val = heatmap_data[i, j]
        text_color = "white" if val > 0.45 else "black"
        ax.text(j, i, f"{val:.1%}", ha="center", va="center", color=text_color, fontweight='bold', fontsize=9)

ax.set_title("Gemma-4-E2B: Speech Transcription WER Heatmap", fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Signal-to-Noise Ratio (SNR)", fontsize=11, labelpad=10)
ax.set_ylabel("Noise Category", fontsize=11, labelpad=10)
fig.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "voice_noise_matrix_heatmap.png"), bbox_inches='tight')
plt.close()

print(f"Successfully generated visual plots in: {OUTPUT_DIR}")
