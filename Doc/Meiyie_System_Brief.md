# Meiyie Multimodal Video Summarizer: System Architecture & Technical Specifications

This document describes the design, pipeline, and AI implementation of the **Meiyie Multimodal Video Summarizer** system.

---

## 1. System Overview
The Meiyie Video Summarizer is an advanced, end-to-end multimodal pipeline designed to process video recordings (local files or YouTube URLs), extract and filter visual/auditory information, align them chronologically, cluster them into semantic subtopics (chapters), and generate a cohesive narrative video summary.

---

## 2. Ingestion & Preprocessing Layer
1. **Video Ingestion**: Handles raw MP4 inputs or YouTube URLs. YouTube links are resolved and downloaded locally using `yt-dlp` to prevent streaming bandwidth issues.
2. **Parallel Demuxing (FFmpeg)**: 
   - **Audio Extraction**: Extracts raw audio stream, converting it to a 16kHz mono `.wav` file (`output.wav`).
   - **Frame Extraction**: Extracts video frames at a frequency of 4 frames per second (4 FPS) to capture dynamic scene changes without visual redundancy.
3. **Audio Chunking**: Slices the main audio stream into 29-second WAV segments (`chunk_XXX.wav`). This is a physical constraint of the **Gemma-4-E2B** multimodal model, which natively supports a maximum of 30 seconds of audio per prompt.

---

## 3. Vision Filtering Layer
To prevent VRAM explosion and accelerate processing, the pipeline employs a hierarchical vision filter:
1. **Scene Boundary Detection (TransNetV2)**: Uses the TransNetV2 neural network to segment the video into individual logical scenes.
2. **Cosine Similarity Filter**: Computes visual differences between successive frames inside each scene. Redundant, static, and blurry frames are discarded.
3. **Clear Keyframe Selection**: Retains only the most visually distinct and clear keyframes (usually capped at the top 3 per 29-second segment based on change scores).

---

## 4. Multimodal Core: Gemma-4-E2B-it
1. **Interleaved Execution**: Maps chronological keyframes and the matching 29-second audio chunk into a unified chat template.
2. **Prompt Template**:
   - If a segment contains both keyframes and audio: *"Analyze this chronological sequence of [N] video frames and the accompanying 29 seconds of audio. Provide a consolidated summary synthesizing exactly what physically happens on screen alongside what is being discussed verbally."*
   - If a segment has no keyframes (audio-only): *"Transcribe the following speech segment in its original language."*
3. **GPU Inference**: The model is loaded in `bfloat16`/`float16` on the local GPU (NVIDIA RTX 6000 Ada) using Hugging Face's `transformers` library, producing high-quality transcriptions and visual analyses.

---

## 5. Orchestration, RAG, and Clustering Layer
Once Gemma-4-E2B generates descriptions for all segments, the text timeline is passed to the downstream text processor:
1. **Text Vectorization**: Embeds the timeline segments using a local SentenceTransformers model (`all-MiniLM-L6-v2`) via Hugging Face.
2. **Semantic Chunking**: Group contiguous timeline descriptions into chapters. A semantic text splitter splits the text when the similarity between adjacent blocks drops below a threshold.
3. **LangChain Map-Reduce Chain**:
   - **Map Phase**: Summarizes individual semantic chapters.
   - **Reduce Phase**: Synthesizes the chapter summaries into a final coherent narrative summary of the entire video.

---

## 6. Local Model Server Backend (WSL)
- To keep the vectorization and pipeline orchestration clean from text-generation resource usage, the Map-Reduce summarization runs via an API endpoint connection to a local **llama-server**.
- The `llama-server` runs inside **Windows Subsystem for Linux (WSL)**, hosting a quantized version of the **Gemma-4-E2B-it** model (GGUF format, `Q4_K_M`). 
- The Python script connects to this backend server at `http://localhost:8080/v1` using LangChain's `ChatOpenAI` wrapper.

---

## 7. Frontend User Interface
- Built using **Streamlit**.
- Provides a dashboard displaying the uploaded video, interactive chapter-by-chapter summaries, timeline graphs, and execution performance metrics (processing speed, GPU VRAM usage).
