import os
import sys

# Configure standard streams to handle encoding errors gracefully (especially on Windows)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(errors='replace')
    except Exception:
        pass

# Ensure project root is in the search path for module resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import cv2
import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from transnetv2_pytorch import TransNetV2

def compute_ssim(img1, img2):
    """
    Computes structural similarity index (SSIM) between two BGR images using OpenCV.
    """
    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Ensure same size
    if gray1.shape != gray2.shape:
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
        
    C1 = 6.5025
    C2 = 58.5225
    
    I1 = gray1.astype(np.float32)
    I2 = gray2.astype(np.float32)
    
    I1_2 = I1 * I1
    I2_2 = I2 * I2
    I1_I2 = I1 * I2
    
    mu1 = cv2.GaussianBlur(I1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(I2, (11, 11), 1.5)
    
    mu1_2 = mu1 * mu1
    mu2_2 = mu2 * mu2
    mu1_mu2 = mu1 * mu2
    
    sigma1_2 = cv2.GaussianBlur(I1_2, (11, 11), 1.5) - mu1_2
    sigma2_2 = cv2.GaussianBlur(I2_2, (11, 11), 1.5) - mu2_2
    sigma12 = cv2.GaussianBlur(I1_I2, (11, 11), 1.5) - mu1_mu2
    
    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_2 + mu2_2 + C1) * (sigma1_2 + sigma2_2 + C2))
    return float(np.mean(ssim_map))

def compute_frame_differences(video_path='data/raw_videos/input.mp4', frames_dir='data/frames/', threshold=0.3, show_plot=False, fps=4.0, similarity_threshold=0.40): #0.3 or 0.9 if remove flat = flat - np.mean(flat)
    """
    Keyframe extraction strategy:
    1. Detect scene segments using TransNetV2.
    2. Extract the middle frame from each scene segment as candidates.
    3. Extract 64x64 grayscale raw pixel embeddings for these middle frames.
    4. Run Agglomerative Clustering dynamically based on cosine distance (threshold = 0.20, i.e. 80% similarity).
    5. Select the frame closest to the cluster mean for each cluster as a final keyframe.
    6. Generate PCA 2D projection clustering graph and save to outputs/clustering_graph.png.
    """
    print("🎬 Loading TransNetV2 model to detect scenes...")
    model = TransNetV2()
    
    print(f"📹 Processing video: {video_path}")
    # Run TransNetV2 scene detection
    outputs = model.predict_video(video_path)
    single_pred = outputs[1]
    single_pred = single_pred.detach().cpu().numpy()
    scenes = model.predictions_to_scenes(single_pred, threshold=threshold)
    num_scenes = len(scenes)
    print(f"🎯 Detected {num_scenes} scenes.")
    
    # Load all 4 FPS frames
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    frame_files = [f for f in os.listdir(frames_dir) if f.lower().endswith(valid_extensions)]
    frame_files = sorted(
        frame_files,
        key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else x
    )
    num_frames = len(frame_files)
    
    if num_frames == 0:
        print("Error: No frame files found. Please run frame extraction first.")
        return []
        
    print(f"📸 Total 4 FPS frames found: {num_frames}")
    
    # 1. Map scenes to middle frames on the 4 FPS timeline
    print("🎯 Extracting middle frames of each scene segment...")
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    if video_fps <= 0:
        video_fps = 30.0  # fallback
        
    candidate_indices = []
    for s_idx, scene in enumerate(scenes):
        start_frame, end_frame = scene
        start_sec = start_frame / video_fps
        end_sec = end_frame / video_fps
        middle_sec = (start_sec + end_sec) / 2.0
        
        timeline_idx = int(round(middle_sec * fps)) + 1
        # Clamp to valid frame indices range
        timeline_idx = max(1, min(timeline_idx, num_frames))
        candidate_indices.append(timeline_idx - 1)
        
    # Remove duplicates from candidates while keeping order
    unique_candidates = []
    for c in candidate_indices:
        if c not in unique_candidates:
            unique_candidates.append(c)
    candidate_indices = unique_candidates
    num_candidates = len(candidate_indices)
    print(f"📸 Selected {num_candidates} unique middle frames as candidates.")
    
    if num_candidates == 0:
        print("Error: No candidates extracted from scenes.")
        return []
        
    # Compute consecutive SSIM differences just to log change scores for final metrics
    diff_scores = [0.0] * num_frames
    prev_img = cv2.imread(os.path.join(frames_dir, frame_files[0]))
    for i in range(1, num_frames):
        curr_img = cv2.imread(os.path.join(frames_dir, frame_files[i]))
        if prev_img is not None and curr_img is not None:
            ssim_val = compute_ssim(prev_img, curr_img)
            diff_scores[i] = float(1.0 - ssim_val)
        else:
            diff_scores[i] = 0.0
        prev_img = curr_img

    # 2. Extract 64x64 raw pixel embeddings for candidate middle frames
    candidate_embeddings_list = []
    for idx in candidate_indices:
        path = os.path.join(frames_dir, frame_files[idx])
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            resized = cv2.resize(img, (64, 64))
            flat = resized.flatten().astype(np.float32) / 255.0
            
            # Check for solid-color/zero-variance frames to prevent division by zero in Cosine Clustering
            variance = np.var(flat)
            if variance < 1e-9:
                flat = np.random.normal(0.0, 1e-6, size=flat.shape).astype(np.float32)
            else:
                # Mean-centering to eliminate background bias (converts Cosine Similarity to Pearson Correlation)
                flat = flat - np.mean(flat)
                
            candidate_embeddings_list.append(flat)
        else:
            # Fallback to tiny noise vector instead of absolute zero vector to prevent Cosine clustering failure
            fallback = np.random.normal(0.0, 1e-6, size=4096).astype(np.float32)
            candidate_embeddings_list.append(fallback)
            
    candidate_embeddings = np.array(candidate_embeddings_list)

    # 3. Agglomerative Clustering
    selected_indices_set = set()
    labels: np.ndarray = np.array([])
    
    if num_candidates == 1:
        selected_indices_set.add(candidate_indices[0])
        num_clusters = 1
        labels = np.array([0])
    else:
        from sklearn.cluster import AgglomerativeClustering
        # Threshold: 0.10 means 90% cosine similarity
        distance_threshold = 1.0 - similarity_threshold
        print(f"🤖 Clustering candidate middle frames using Cosine Agglomerative Clustering (similarity threshold={similarity_threshold:.2%})...")
        
        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric='cosine',
            linkage='average',
            distance_threshold=distance_threshold
        )
        labels = clustering.fit_predict(candidate_embeddings)  # type: ignore
        num_clusters = len(np.unique(labels))
        print(f"🎯 Segmented into {num_clusters} visual clusters dynamically.")

        # 4. Select representative frame closest to average center for each cluster
        for k in range(num_clusters):
            cluster_cand_indices = [i for i, label in enumerate(labels) if label == k]
            if not cluster_cand_indices:
                continue
            
            # Average embedding of cluster
            cluster_mean = np.mean(candidate_embeddings[cluster_cand_indices], axis=0)
            
            distances = []
            for i in cluster_cand_indices:
                dist = np.linalg.norm(candidate_embeddings[i] - cluster_mean)
                distances.append((dist, candidate_indices[i]))
                
            best_candidate_idx = sorted(distances, key=lambda x: x[0])[0][1]
            selected_indices_set.add(best_candidate_idx)

    # 5. Generate PCA projection plot for clustering graph
    if num_candidates >= 2:
        try:
            print("📊 Generating PCA projection plot for clustering graph...")
            from sklearn.decomposition import PCA
            
            n_comp = min(2, num_candidates)
            pca = PCA(n_components=n_comp, random_state=42)
            coords = pca.fit_transform(candidate_embeddings)  # type: ignore
            
            plt.figure(figsize=(10, 7))
            if coords.shape[1] == 2:
                x = coords[:, 0]
                y = coords[:, 1]
            else:
                x = coords[:, 0]
                y = np.zeros_like(x)
                
            unique_labels = np.unique(labels)
            colors = plt.cm.get_cmap('tab20', max(1, len(unique_labels)))
            
            # Track labeled items to prevent duplicate legend entries
            plotted_labels = set()
            
            for i, label in enumerate(labels):
                is_rep = candidate_indices[i] in selected_indices_set
                color = colors(np.where(unique_labels == label)[0][0] if len(unique_labels) > 0 else 0)
                
                if is_rep:
                    label_str = f"Cluster {label} Center"
                    if label_str not in plotted_labels:
                        plt.scatter(x[i], y[i], color=color, s=220, marker='*', edgecolor='black', zorder=5, label=label_str)
                        plotted_labels.add(label_str)
                    else:
                        plt.scatter(x[i], y[i], color=color, s=220, marker='*', edgecolor='black', zorder=5)
                    # Label with frame number
                    plt.annotate(f"Frame {candidate_indices[i] + 1}", (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, fontweight='bold')
                else:
                    label_str = f"Cluster {label}"
                    if label_str not in plotted_labels:
                        plt.scatter(x[i], y[i], color=color, s=70, alpha=0.5, zorder=3, label=label_str)
                        plotted_labels.add(label_str)
                    else:
                        plt.scatter(x[i], y[i], color=color, s=70, alpha=0.5, zorder=3)
                        
            plt.title(f"Visual Cluster Map (Agglomerative Cosine Clustering, {num_clusters} Groups)", fontsize=12, fontweight='bold', pad=15)
            plt.xlabel("PCA Component 1", fontsize=10)
            plt.ylabel("PCA Component 2", fontsize=10)
            plt.grid(True, linestyle='--', alpha=0.3)
            
            if len(unique_labels) <= 15:
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
                
            plt.tight_layout()
            graph_path = 'outputs/clustering_graph.png'
            os.makedirs(os.path.dirname(graph_path), exist_ok=True)
            plt.savefig(graph_path, dpi=150)
            plt.close()
            print(f"📈 Clustering graph saved to {graph_path}")
        except Exception as plot_err:
            print(f"Warning: Failed to generate clustering graph: {plot_err}")

    # 6. Construct final metrics output
    difference_metrics = []
    keyframes_rgb = []
    
    for idx, filename in enumerate(frame_files):
        is_selected = idx in selected_indices_set
        
        # Parse timeline index and calculate timestamp
        try:
            timeline_idx = int(''.join(filter(str.isdigit, filename)))
        except ValueError:
            timeline_idx = idx + 1
        timestamp_sec = (timeline_idx - 1) / fps
        
        difference_metrics.append({
            'frame_index': idx,
            'filename': filename,
            'is_clear_keyframe': is_selected,
            'change_score': diff_scores[idx],
            'timestamp_sec': timestamp_sec
        })
        
        if is_selected:
            path = os.path.join(frames_dir, filename)
            img = cv2.imread(path)
            if img is not None:
                frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                keyframes_rgb.append(frame_rgb)

    output_file = 'outputs/frame_comparison_final.json'
    with open(output_file, 'w') as f:
        json.dump(difference_metrics, f, indent=4)
        
    print(f"✅ Final analysis saved to {output_file}")
    total_clear = sum(1 for m in difference_metrics if m['is_clear_keyframe'])
    print(f"📊 Summary: Saved {len(difference_metrics)} frames, flagged {total_clear} clear keyframes to {frames_dir}.")
    
    # Direct display (showing only the flagged clear keyframes if show_plot is True and we're not in headless mode)
    if show_plot and keyframes_rgb:
        try:
            print("📊 Generating dynamic display...")
            cols = 5
            rows = math.ceil(len(keyframes_rgb) / cols)
            
            plt.figure(figsize=(20, 4 * rows))
            for plot_idx, frame_rgb in enumerate(keyframes_rgb):
                plt.subplot(rows, cols, plot_idx + 1)
                plt.imshow(frame_rgb)
                plt.axis('off')
                plt.title(f"Keyframe {plot_idx + 1}", fontsize=10)
                
            plt.tight_layout()
            plt.show()
        except Exception as plot_err:
            print(f"Warning: Could not display plots: {plot_err}")
        
    return difference_metrics


if __name__ == "__main__":
    results = compute_frame_differences(show_plot=True)

