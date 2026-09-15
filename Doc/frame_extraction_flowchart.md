# Frame Extraction to Final Keyframe Pipeline

This flowchart documents the technical pipeline that processes the raw video input, extracts frames, detects scenes, clusters visual segments, and selects the final keyframes displayed on the dashboard.

```mermaid
graph TD
    %% Define styles
    classDef process fill:#d2e3fc,stroke:#174ea6,stroke-width:2px;
    classDef input fill:#f1f3f4,stroke:#5f6368,stroke-width:2px;
    classDef model fill:#e6f4ea,stroke:#137333,stroke-width:2px;
    classDef output fill:#feefd5,stroke:#b06000,stroke-width:2px;

    %% Elements
    Video["📹 Raw Video Input<br>(e.g. 41 mins @ 24 FPS = 59,219 frames)"]:::input
    
    %% Path A: FFmpeg
    FFmpeg["⚙️ FFmpeg Extraction<br>(Extract at constant 4 FPS)"]:::process
    FramesDir["📂 data/frames/<br>(9,880 JPEG files)"]:::input
    
    %% Path B: Scene Detection
    TransNet["🧠 TransNetV2 Model<br>(Processes 59,219 frames frame-by-frame)"]:::model
    Scenes["🎯 Detected Scenes<br>(Start & End frames on native 24 FPS timeline)"]:::output

    %% Syncing
    MiddleSec["Calculate Middle Timestamp (s)<br>middle_sec = (start + end) / (2.0 * native_fps)"]:::process
    Map4FPS["Map to 4 FPS Frame Index<br>index = int(round(middle_sec * 4.0)) + 1"]:::process
    Candidates["📸 Candidate Middle Frames<br>(1 representative per scene segment)"]:::process

    %% Embeddings
    Resize["Resize & Grayscale<br>(Convert to 64x64 pixels)"]:::process
    MeanCenter["Mean-Centering<br>flat_vector = flat - np.mean(flat)<br>(Converts Cosine Similarity to Pearson Correlation)"]:::process
    Embeddings["🧬 Grayscale Raw Pixel Embeddings<br>(4,096-dimensional vectors)"]:::output

    %% Clustering
    Cluster["🤖 Agglomerative Clustering<br>(Cosine metric, average linkage,<br>distance threshold based on similarity)"]:::model
    Groups["📦 Visual Clusters<br>(Groups visually redundant scenes together)"]:::process

    %% Selection
    ClusterMean["Compute Cluster Mean<br>(Average vector of each cluster)"]:::process
    MinDist["Min-Distance Selection<br>(Select frame closest to average center)"]:::process
    FinalKeyframes["🖼️ Final Selected Keyframes<br>(is_clear_keyframe = True)"]:::output

    %% Connections
    Video --> FFmpeg
    Video --> TransNet
    
    FFmpeg --> FramesDir
    TransNet --> Scenes
    
    Scenes --> MiddleSec
    MiddleSec --> Map4FPS
    FramesDir --> Map4FPS
    Map4FPS --> Candidates
    
    Candidates --> Resize
    Resize --> MeanCenter
    MeanCenter --> Embeddings
    
    Embeddings --> Cluster
    Cluster --> Groups
    
    Groups --> ClusterMean
    ClusterMean --> MinDist
    MinDist --> FinalKeyframes
```

---

### Step-by-Step Walkthrough

1. **Dual-Path Initialization**:
   - **Path A (Frame Extraction)**: FFmpeg extracts static images at a low frequency of **4 FPS** (`GLOBAL_FPS = 4.0`) to save disk space and computing power.
   - **Path B (Scene Detection)**: The raw video is fed frame-by-frame to **TransNetV2** at its **native rate** (24 FPS) to pinpoint exact scene change boundaries.
2. **Temporal Alignment**:
   - The mid-point of each detected scene (in seconds) is calculated.
   - This timestamp is converted to the nearest 4 FPS frame number to yield a list of **unique candidate frames**.
3. **Preprocessing & Embedding**:
   - Candidates are downscaled to `64x64` pixels and grayscaled.
   - **Mean-centering** is applied to cancel out solid background similarities (e.g. slides with the same layout), ensuring focus on the actual content differences (essentially converting cosine similarity to a Pearson correlation coefficient).
4. **Agglomerative Clustering**:
   - The embeddings are grouped together hierarchical-style based on Cosine Distance. Similar scenes (e.g., slides showing the same slide deck background) are clustered together.
5. **Representative Center Selection**:
   - For each cluster, the algorithm selects the frame that is mathematically closest to the cluster's average center. This acts as the final representative keyframe.
