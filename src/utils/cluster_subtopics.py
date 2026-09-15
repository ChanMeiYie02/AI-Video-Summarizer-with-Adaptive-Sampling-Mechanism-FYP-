import json
import os
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRANSCRIPT_PATH = os.path.join(BASE_DIR, "outputs", "transcript.json")
EMBEDDINGS_SAVE_PATH = os.path.join(BASE_DIR, "outputs", "embeddings.npy")
CLUSTERED_OUTPUT_PATH = os.path.join(BASE_DIR, "outputs", "clustered_subtopics.json")
CLUSTER_GRAPH_PATH = os.path.join(BASE_DIR, "outputs", "subtopic_clusters_graph.png")


def find_optimal_clusters_agglomerative(embeddings, k_min=2, k_max=10, initial_threshold=0.95):
    """
    Use Agglomerative Clustering with a dynamic distance threshold to group transcript segments.
    Adjusts the threshold if the cluster count falls outside [k_min, k_max].
    """
    n_samples = len(embeddings)
    if n_samples <= 2:
        return np.array(range(n_samples)), min(2, n_samples), initial_threshold

    # L2-normalize embeddings for cosine-like distance with Ward linkage
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_emb = embeddings / norms

    threshold = initial_threshold
    best_labels = None
    best_n_clusters = 0

    print(f"\n   Running Agglomerative Clustering (n_samples={n_samples})...")
    
    # Iterate to find a threshold that yields between k_min and k_max clusters
    for attempt in range(12):
        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric='euclidean',
            linkage='ward',
            distance_threshold=threshold
        )
        labels = clustering.fit_predict(norm_emb)
        n_clusters = len(set(labels))
        print(f"   Attempt {attempt+1}: threshold={threshold:.4f} -> n_clusters={n_clusters}")

        if k_min <= n_clusters <= k_max:
            return labels, n_clusters, threshold
        
        # Keep track of the closest valid configuration
        if best_labels is None or abs(n_clusters - (k_min + k_max)/2) < abs(best_n_clusters - (k_min + k_max)/2):
            best_labels = labels
            best_n_clusters = n_clusters

        if n_clusters < k_min:
            # Too few clusters: split by reducing the distance threshold
            threshold *= 0.85
        elif n_clusters > k_max:
            # Too many clusters: merge by increasing the distance threshold
            threshold *= 1.15

    # Fallback to the best labels found if bounds weren't perfectly met
    print(f"   ⚠️ Could not perfectly fit bounds with threshold search. Using best fit: {best_n_clusters} clusters.")
    return best_labels, best_n_clusters, threshold


def generate_cluster_scatter(embeddings, cluster_labels, num_clusters):
    """Generate a PCA 2D scatter plot of the clusters."""
    try:
        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(embeddings)

        # Color palette matching the app's blue theme
        colors = plt.cm.Set2(np.linspace(0, 1, max(num_clusters, 3)))

        fig, ax = plt.subplots(figsize=(7, 5))
        for cluster_id in range(num_clusters):
            mask = cluster_labels == cluster_id
            ax.scatter(
                coords[mask, 0], coords[mask, 1],
                c=[colors[cluster_id]],
                label=f'Subtopic {cluster_id} ({mask.sum()} segments)',
                s=60, alpha=0.75, edgecolors='white', linewidth=0.5
            )

        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=11)
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=11)
        ax.set_title('Subtopic Clustering (PCA Projection)', fontsize=13, fontweight='bold')
        ax.legend(fontsize=9, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.2)
        fig.tight_layout()
        fig.savefig(CLUSTER_GRAPH_PATH, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"   📊 Cluster scatter plot saved to {CLUSTER_GRAPH_PATH}")
    except Exception as e:
        print(f"   Warning: Could not generate cluster scatter plot: {e}")


def cluster_subtopics():
    print("1. Loading pre-computed Embeddings and Text Data...")
    if not os.path.exists(TRANSCRIPT_PATH) or not os.path.exists(EMBEDDINGS_SAVE_PATH):
        print("Error: Run 01_embed_and_search.py first to generate embeddings.")
        return

    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    embeddings = np.load(EMBEDDINGS_SAVE_PATH)
    print(f"Loaded {len(data)} text chunks and {embeddings.shape} embeddings.")

    # 2. Dynamically determine optimal number of subtopics using Agglomerative Clustering
    cluster_labels, num_clusters, final_threshold = find_optimal_clusters_agglomerative(embeddings, k_min=2, k_max=10)
    print(f"\n2. Applying Agglomerative Clustering with K={num_clusters} subtopics (threshold={final_threshold:.4f})...")
    
    # Generate cluster visualization
    generate_cluster_scatter(embeddings, cluster_labels, num_clusters)
    
    # 3. Group contexts by their cluster (Subtopic)
    subtopics = {i: [] for i in range(num_clusters)}
    
    for i, label in enumerate(cluster_labels):
        # Adding the original text to its assigned subtopic bucket
        subtopics[int(label)].append(data[i]['text'])
        
    # Formatting it nicely into a JSON structure
    clustered_data = []
    for cluster_id, texts in subtopics.items():
        clustered_data.append({
            "subtopic_id": cluster_id,
            "chunk_count": len(texts),
            "combined_context": "\n\n".join(texts)
        })
        
    print(f"\n3. Clustering complete. Found {len(subtopics)} distinct subtopics.")
    for c in clustered_data:
        print(f"- Subtopic {c['subtopic_id']}: Contains {c['chunk_count']} chunks.")

    # 4. Save the clustered subtopics for summarization
    print(f"\nSaving clustered subtopics to {CLUSTERED_OUTPUT_PATH}...")
    with open(CLUSTERED_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(clustered_data, f, indent=4)
    print("Done!")

if __name__ == "__main__":
    cluster_subtopics()
