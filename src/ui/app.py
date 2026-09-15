import os
import json
import re
import subprocess
import sys
from html import escape

# Configure system paths for robust imports
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import time

def get_wordcloud_and_graph_data(transcripts, summaries):
    # Stop words to filter out
    stop_words = {"the", "and", "a", "of", "to", "in", "is", "that", "it", "for", "on", "with", "as", 
    "at", "by", "an", "be", "this", "are", "from", "you", "your", "how", "make", "video", "powerpoint", 
     "can", "with", "about", "more", "into", "we", "i", "our", "us", "then", "there",
     "then", "but", "not", "what", "which", "or", "if", "so", "up", "out", "now", "just", "like", "will", "go", 
     "get", "here", "their", "them", "which", "was", "were", "been", "could", "have", "used", "also", "use", 
     "just", "some", "any", "very", "many", "much", "few", "all", "one", "two", "three", "four", "five", "six", 
     "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", 
     "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred",
     "thousand", "million", "billion", "trillion", "one", "needs", "should", "would", "could", "may", "might", "must",
     "shall", "should", "would", "could", "may", "might", "must", "shall", "should", "would", "could", "may", "might",
     "must", "shall", "should", "would", "could", "may", "might", "must", "shall", "should", "would", "could", "may", 
     "might", "must", "shall", "should", "would", "could", "may", "might", "must", "shall"}
    
    # 1. Calculate word frequencies for Word Cloud
    word_freq = {}
    for t in transcripts:
        words = re.findall(r'\b[a-zA-Z]{4,15}\b', t.get("text", "").lower())
        for w in words:
            if w not in stop_words:
                word_freq[w] = word_freq.get(w, 0) + 1
                
    # Sort and take top 40 words
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:45]
    wordcloud_data = [{"text": w.capitalize(), "size": count} for w, count in top_words]
    
    # 2. Build Knowledge Graph Nodes and Links
    nodes = [{"id": "video_root", "label": "📹 Video Summary", "group": 0, "value": 30, "title": "Main Video Root Node"}]
    links = []
    
    # Track added keywords to prevent duplicate nodes
    added_keywords = set()
    
    for s in summaries:
        subtopic_id = s.get("subtopic_id")
        title = s.get("title", f"Topic {subtopic_id}").replace("TITLE:", "").strip()
        desc = s.get("description", "").replace("DESCRIPTION:", "").strip()
        summary = s.get("summary", "").replace("SUMMARY:", "").strip()
        
        # Subtopic Node
        subtopic_node_id = f"subtopic_{subtopic_id}"
        nodes.append({
            "id": subtopic_node_id,
            "label": title,
            "group": 1,
            "value": 20,
            "title": f"<b>{title}</b><br>{desc[:100]}..."
        })
        
        # Link from root to subtopic
        links.append({"from": "video_root", "to": subtopic_node_id, "arrows": "to"})
        
        # Extract keywords for this subtopic
        kw_candidates = re.findall(r'\b[a-zA-Z]{5,15}\b', (title + " " + summary).lower())
        kw_freq = {}
        for w in kw_candidates:
            if w not in stop_words:
                kw_freq[w] = kw_freq.get(w, 0) + 1
        top_kws = sorted(kw_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for kw, _ in top_kws:
            kw_cap = kw.capitalize()
            kw_node_id = f"kw_{kw}"
            
            # Add keyword node if not exists
            if kw_node_id not in added_keywords:
                nodes.append({
                    "id": kw_node_id,
                    "label": kw_cap,
                    "group": 2,
                    "value": 10,
                    "title": f"Key phrase in {title}"
                })
                added_keywords.add(kw_node_id)
                
            # Link from subtopic to keyword
            links.append({"from": subtopic_node_id, "to": kw_node_id})
            
    return {"wordcloud": wordcloud_data, "graph": {"nodes": nodes, "links": links}}

st.set_page_config(page_title="Video Summarization Dashboard", layout="wide")

# -- CSS Styling for aesthetics --
st.markdown("""
<style>
:root {
    --bg-main: var(--background-color, #ffffff);
    --bg-card: #ffffff;
    --blue-100: #e1f5fe;
    --blue-200: #b3e5fc;
    --blue-500: var(--primary-color, #2c99ff);
    --blue-600: #0288d1;
    --blue-700: #01579b;
    --text-main: var(--text-color, #31333f);
    --text-soft: #5e6977;
    --border-soft: #b3e5fc;
    --shadow-soft: 0 10px 28px rgba(0, 0, 0, 0.05);
}

/* ===== TIMELINE STEPPER ===== */
.timeline-stepper {
    margin: 15px 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.timeline-item {
    display: flex;
    align-items: flex-start;
    position: relative;
    padding-left: 28px;
    padding-bottom: 20px;
    border-left: 2px solid var(--border-soft);
}
.timeline-item:last-child {
    border-left: none;
    padding-bottom: 5px;
}
.timeline-item.active {
    border-left: 2px dashed var(--blue-500);
}
.timeline-item::before {
    content: '';
    position: absolute;
    left: -7px;
    top: 4px;
    width: 12px;
    height: 12px;
    background-color: var(--border-soft);
    border: 2px solid var(--blue-200);
    border-radius: 50%;
    transition: all 0.3s ease;
}
.timeline-item.active::before {
    background-color: var(--blue-500);
    border: 2px solid var(--blue-100);
    box-shadow: 0 0 10px rgba(47, 123, 229, 0.6);
    animation: pulse 1.5s infinite;
}
.timeline-item.success::before {
    content: '✓';
    color: white;
    font-size: 10px;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    left: -9px;
    top: 2px;
    width: 16px;
    height: 16px;
    background-color: #2e7d32;
    border: none;
}
.timeline-content {
    font-size: 0.95em;
    color: var(--text-soft);
    margin-top: -2px;
}
.timeline-item.active .timeline-content {
    color: var(--blue-700);
    font-weight: 600;
}
.timeline-item.success .timeline-content {
    color: var(--text-main);
}
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(47, 123, 229, 0.4); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(47, 123, 229, 0); }
    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(47, 123, 229, 0); }
}

/* ===== GLOBAL ===== */
html, body, .stApp {
    background: var(--bg-main) !important;
    color: var(--text-main) !important;
    overflow-x: hidden !important;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 1.8rem;
}

h1, h2, h3, h4 {
    color: var(--text-main);
    letter-spacing: 0.1px;
}

/* ===== CARD CONTAINER ===== */
div[data-testid="stHorizontalBlock"] > div {
    background: var(--secondary-background-color, #f0f6ff);
    border: 1px solid var(--border-soft);
    border-radius: 14px;
    padding: 0.85rem 1rem;
    box-shadow: var(--shadow-soft);
}

/* ===== EQUAL-HEIGHT COLUMN ROWS ===== */
div[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}
div[data-testid="stHorizontalBlock"] > div {
    display: flex;
    flex-direction: column;
}
/* Make Streamlit inner blocks fill the card */
div[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlock"] {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
}
/* Streamlit height-constrained container (search panel) should fill space */
div[data-testid="stVerticalBlockBorderWrapper"][style*="height"] {
    flex: 1 1 auto;
}

/* ===== SCROLL CONTAINER ===== */
.scroll-container {
    min-height: 180px;
    max-height: 500px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 10px;
    border: 1px solid var(--border-soft);
    border-radius: 10px;
    background-color: var(--bg-card);
    flex: 1 1 auto;      /* grow to fill remaining card space */
}

/* Scrollbar styling */
.scroll-container::-webkit-scrollbar {
    width: 8px;
}
.scroll-container::-webkit-scrollbar-thumb {
    background: var(--blue-600);
    border-radius: 10px;
}

/* ===== TOPIC CARD (USED EVERYWHERE) ===== */
.topic-card {
    background: var(--bg-card) !important;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 16px;
    border: 1px solid var(--border-soft);
    border-left: 5px solid var(--blue-500);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
    color: var(--text-main);

    word-wrap: break-word;      /* ✅ prevent overflow */
    overflow-wrap: break-word;
}

/* Better spacing */
.topic-card h4 {
    margin-bottom: 6px;
    color: var(--text-main) !important;
}
.topic-card p {
    margin: 4px 0;
    color: var(--text-soft) !important;
}
.topic-card i {
    color: var(--text-soft);
}

/* ===== CLICKABLE CARD EFFECT ===== */
.card-wrapper {
    position: relative;
}

.clickable-card {
    cursor: pointer;
    transition: all 0.2s ease;
}

.clickable-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 26px rgba(47, 123, 229, 0.18);
    border-left: 5px solid var(--blue-600);
}

/* ===== INPUT FIELDS ===== */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border: 1px solid var(--blue-200) !important;
    border-radius: 10px !important;
    background: var(--bg-card) !important;
    color: var(--text-main) !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: var(--blue-500) !important;
    box-shadow: 0 0 0 3px rgba(47, 123, 229, 0.14) !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: var(--text-main) !important;
}

/* ===== VIDEO ===== */
video {
    width: 100% !important;
    height: auto !important;
    max-height: 420px;
    object-fit: contain;
    margin: 0 auto;
    display: block;
    border-radius: 10px;
    border: 1px solid var(--border-soft);
    background: #000;
}

/* ===== VIDEO SECTION WRAPPER ===== */
.video-section {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    padding: 8px 0;
}

/* ===== ALERT ===== */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid var(--blue-200) !important;
}

/* ===== DIVIDER ===== */
.stDivider {
    border-top: 1px solid var(--border-soft) !important;
}

/* ===== PROFESSIONAL BUTTONS DESIGN (GLASSMORPHISM WITH ANCHORS) ===== */

/* 1. Primary Action Buttons (Load Data / Process, Export Downloads) - Glassmorphism */
div.element-container:has(div.primary-btn-anchor) + div.element-container button,
div.element-container:has(div.download-btn-anchor) + div.element-container button {
    text-align: center !important;
    white-space: normal !important; /* Allow wrapping */
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    line-height: 1.3 !important;
    background: linear-gradient(135deg, var(--blue-500) 0%, var(--blue-600) 100%) !important;
    color: #ffffff !important;
    border: 1px solid var(--blue-700) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    padding: 10px 20px !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.2px !important;
    box-shadow: inset 0 1px 1px 0 rgba(255, 255, 255, 0.2), 0 8px 24px 0 rgba(0, 0, 0, 0.05) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-bottom: 0px !important;
    border-left: 1px solid rgba(255, 255, 255, 0.25) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 44px !important;
    cursor: pointer !important;
    width: 100% !important;
}

/* Ensure inner text elements wrap cleanly */
div.element-container:has(div.primary-btn-anchor) + div.element-container button *,
div.element-container:has(div.download-btn-anchor) + div.element-container button * {
    white-space: normal !important;
    word-break: break-word !important;
    text-align: center !important;
    color: #ffffff !important;
}

div.element-container:has(div.primary-btn-anchor) + div.element-container button:hover,
div.element-container:has(div.download-btn-anchor) + div.element-container button:hover {
    background: linear-gradient(135deg, var(--blue-600) 0%, var(--blue-700) 100%) !important;
    border-color: var(--blue-700) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: inset 0 1px 1px 0 rgba(255, 255, 255, 0.4), 0 12px 32px 0 rgba(0, 0, 0, 0.1) !important;
}

div.element-container:has(div.primary-btn-anchor) + div.element-container button:active,
div.element-container:has(div.download-btn-anchor) + div.element-container button:active {
    transform: translateY(0px) !important;
    background: var(--blue-700) !important;
}

/* 2. Utility / Secondary Buttons - Light Blue */
div.element-container:has(div.utility-btn-anchor) + div.element-container button,
div.element-container:has(div.jump-btn-anchor) + div.element-container button {
    text-align: center !important;
    white-space: nowrap !important;
    background: rgba(44, 153, 255, 0.1) !important;
    color: var(--blue-700) !important;
    border: 1px solid var(--blue-200) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    padding: 6px 14px !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 4px 12px 0 rgba(0, 0, 0, 0.05) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-bottom: 0px !important;
    border-left: 1px solid var(--blue-200) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 34px !important;
    cursor: pointer !important;
    width: 100% !important;
}

div.element-container:has(div.utility-btn-anchor) + div.element-container button:hover,
div.element-container:has(div.jump-btn-anchor) + div.element-container button:hover {
    background: rgba(44, 153, 255, 0.2) !important;
    border-color: var(--blue-500) !important;
    color: var(--blue-700) !important;
    transform: translateY(-1px) !important;
    box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.2), 0 6px 16px 0 rgba(0, 0, 0, 0.1) !important;
}

div.element-container:has(div.utility-btn-anchor) + div.element-container button:active,
div.element-container:has(div.jump-btn-anchor) + div.element-container button:active {
    transform: translateY(0px) !important;
    background: rgba(44, 153, 255, 0.3) !important;
}

/* 3. Search Topic Card Clickable Buttons (Topic Card Style) */
div.element-container:has(div.search-card-anchor) + div.element-container button {
    text-align: left !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-soft) !important;
    border-left: 5px solid #2f7be5 !important;
    padding: 18px !important;
    border-radius: 12px !important;
    margin-bottom: 16px !important;
    color: var(--text-main) !important;
    font-weight: normal !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    display: block !important;
    width: 100% !important;
}

div.element-container:has(div.search-card-anchor) + div.element-container button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 26px rgba(0, 0, 0, 0.1) !important;
    border-left-color: #2f7be5 !important;
    background: var(--bg-card) !important;
    opacity: 0.9 !important;
    color: var(--text-main) !important;
}

</style>
""", unsafe_allow_html=True)

# Define directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Initialize Session States
if 'session_initialized' not in st.session_state:
    st.session_state.session_initialized = True
    st.cache_data.clear()
    st.cache_resource.clear()
    
    # Ensure required directories exist without purging them
    for folder in [os.path.join(BASE_DIR, "data", "frames"), os.path.join(BASE_DIR, "data", "audio"), os.path.join(BASE_DIR, "outputs")]:
        os.makedirs(folder, exist_ok=True)

if 'video_path' not in st.session_state:
    # WSL Linux path to your Windows Desktop file
    st.session_state.video_path = "/mnt/c/Users/admin_mtds/OneDrive/Desktop/Meiyie/data/raw_videos/How to Make a Video in PowerPoint - ppt to video.mp4"

# Auto-convert paths for compatibility between WSL and Windows
if st.session_state.video_path:
    if os.name == 'nt' and st.session_state.video_path.startswith("/mnt/c/"):
        st.session_state.video_path = "C:/" + st.session_state.video_path[7:]
    elif os.name != 'nt' and (st.session_state.video_path.lower().startswith("c:/") or st.session_state.video_path.lower().startswith("c:\\")):
        st.session_state.video_path = "/mnt/c/" + st.session_state.video_path[3:].replace("\\", "/")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'start_time' not in st.session_state:
    st.session_state.start_time = 0

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'search_query_input' not in st.session_state:
    st.session_state.search_query_input = ""

def clear_video_cache():
    st.session_state.start_time = 0
    st.session_state.search_results = []
    st.session_state.search_query_input = ""
    st.session_state.data_loaded = False
    st.cache_data.clear()
    
    # Purge outputs and media directories on disk to force processing again
    import shutil
    for folder in [os.path.join(BASE_DIR, "data", "frames"), os.path.join(BASE_DIR, "data", "audio"), os.path.join(BASE_DIR, "outputs")]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except Exception:
                pass
        os.makedirs(folder, exist_ok=True)

# --- Caching expensive operations ---
@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_data
def load_data(_cache_buster):
    transcript_path = os.path.join(OUTPUTS_DIR, "transcript.json")
    embeddings_path = os.path.join(OUTPUTS_DIR, "embeddings.npy")
    summaries_path = os.path.join(OUTPUTS_DIR, "final_topic_summaries.json")
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcripts = json.load(f)
    with open(summaries_path, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    embeddings = np.load(embeddings_path)
    
    # Assign subtopic_ids to transcripts since they're missing
    transcripts = assign_subtopics_to_transcripts(transcripts, summaries)
    
    return transcripts, embeddings, summaries


@st.cache_data
def load_overall_summary(_cache_buster):
    summary_path = os.path.join(OUTPUTS_DIR, "final_summary.md")
    if not os.path.exists(summary_path):
        return "Overall summary file not found. Run the pipeline to generate `outputs/final_summary.md`."
    with open(summary_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_video_metadata(video_path, transcripts, summaries):
    """
    Extract video metadata for display: name, duration, segment count,
    subtopic count, and pipeline processing time.
    """
    metadata = {}

    # Video name
    if is_youtube_url(video_path):
        metadata["name"] = video_path
        metadata["source"] = "YouTube"
    else:
        metadata["name"] = os.path.splitext(os.path.basename(video_path))[0]
        metadata["source"] = "Local File"

    # Duration from transcript timeline
    if transcripts:
        last = max(transcripts, key=lambda t: t.get("end", t.get("end_sec", 0)))
        total_sec = last.get("end", last.get("end_sec", 0))
        mins = int(total_sec // 60)
        secs = int(total_sec % 60)
        metadata["duration"] = f"{mins}m {secs}s"
        metadata["duration_sec"] = total_sec
    else:
        metadata["duration"] = "Unknown"
        metadata["duration_sec"] = 0

    # Counts
    metadata["segments"] = len(transcripts)
    metadata["subtopics"] = len(summaries)

    # Keyframe count from frame_comparison_final.json
    kf_path = os.path.join(OUTPUTS_DIR, "frame_comparison_final.json")
    if os.path.exists(kf_path):
        try:
            with open(kf_path, "r", encoding="utf-8") as f:
                kf_data = json.load(f)
            metadata["keyframes"] = sum(1 for m in kf_data if m.get("is_clear_keyframe", False))
        except Exception:
            metadata["keyframes"] = 0
    else:
        metadata["keyframes"] = 0

    # Processing time from execution_times.txt
    exec_path = os.path.join(OUTPUTS_DIR, "execution_times.txt")
    if os.path.exists(exec_path):
        with open(exec_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract total time from last line pattern "TOTAL TIME: 123.45 seconds"
        match = re.search(r"TOTAL TIME:\s*([\d.]+)\s*seconds", content)
        if match:
            total = float(match.group(1))
            p_mins = int(total // 60)
            p_secs = int(total % 60)
            metadata["processing_time"] = f"{p_mins}m {p_secs}s"
        else:
            metadata["processing_time"] = "N/A"
    else:
        metadata["processing_time"] = "N/A"

    # Last processed timestamp
    summary_path = os.path.join(OUTPUTS_DIR, "final_summary.md")
    if os.path.exists(summary_path):
        mtime = os.path.getmtime(summary_path)
        metadata["processed_at"] = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    else:
        metadata["processed_at"] = "N/A"

    return metadata


def build_topic_lookup(summaries):
    return {
        str(s.get("subtopic_id")): s.get("title", f"Topic {s.get('subtopic_id')}")
        for s in summaries
    }


def perform_search(query, transcripts, embeddings, embedder, threshold=0.35):
    """Search all segments above threshold, sorted by score descending."""
    query_emb = embedder.encode([query])
    similarities = cosine_similarity(query_emb, embeddings)[0]

    # Return ALL results above threshold, sorted by score
    results = []
    for idx in np.argsort(similarities)[::-1]:
        score = float(similarities[idx])
        if score < threshold:
            break
        results.append(
            {
                "match": transcripts[idx],
                "score": score,
            }
        )
    return results


def get_segment_bounds(item):
    start = item.get("start_sec", item.get("start", 0))
    end = item.get("end_sec", item.get("end", start))
    return float(start), float(end)


def get_outputs_cache_buster():
    files = [
        os.path.join(OUTPUTS_DIR, "transcript.json"),
        os.path.join(OUTPUTS_DIR, "embeddings.npy"),
        os.path.join(OUTPUTS_DIR, "final_topic_summaries.json"),
        os.path.join(OUTPUTS_DIR, "final_summary.md"),
    ]
    return tuple(os.path.getmtime(path) if os.path.exists(path) else 0 for path in files)


def is_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
    return bool(re.match(pattern, url.strip()))


def run_main_pipeline(video_path, threshold=0.3, similarity_threshold=0.30, use_multimodal=True, batch_size=32):
    main_script = os.path.join(SRC_DIR, "main.py")
    command = [
        sys.executable, "-X", "utf8", main_script,
        "--video_path", video_path,
        "--threshold", str(threshold),
        "--similarity_threshold", str(similarity_threshold),
        "--use_multimodal", "True" if use_multimodal else "False",
        "--batch_size", str(batch_size)
    ]
    result = subprocess.run(
        command,
        cwd=SRC_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result

def run_pipeline_stream(video_path, threshold=0.3, similarity_threshold=0.30, use_multimodal=True, batch_size=32):
    main_script = os.path.join(SRC_DIR, "main.py")
    command = [
        sys.executable, "-X", "utf8", "-u", main_script,
        "--video_path", video_path,
        "--threshold", str(threshold),
        "--similarity_threshold", str(similarity_threshold),
        "--use_multimodal", "True" if use_multimodal else "False",
        "--batch_size", str(batch_size)
    ]
    try:
        process = subprocess.Popen(
            command,
            cwd=SRC_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8"
        )
        return process
    except Exception as e:
        st.error(f"Failed to spawn pipeline process: {e}")
        return None

def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"



def assign_subtopics_to_transcripts(transcripts, summaries):
    """
    Assign subtopic_id to each transcript based on evenly dividing the timeline.
    Assumes summaries are ordered chronologically.
    """
    if not transcripts or not summaries:
        return transcripts
    
    # Sort by start time
    sorted_transcripts = sorted(transcripts, key=lambda x: x.get("start", 0))
    
    # Calculate how many transcripts per subtopic (even distribution)
    num_transcripts = len(sorted_transcripts)
    num_subtopics = len(summaries)
    
    if num_subtopics == 0:
        return sorted_transcripts
    
    # Assign subtopic_id based on position in timeline
    transcripts_per_subtopic = num_transcripts / num_subtopics
    
    for i, t in enumerate(sorted_transcripts):
        subtopic_index = min(int(i / transcripts_per_subtopic), num_subtopics - 1)
        t["subtopic_id"] = summaries[subtopic_index]["subtopic_id"]
    
    return sorted_transcripts

# --- UI LAYOUT ---
st.sidebar.title("⚙️ Pipeline Settings")
st.sidebar.markdown("Configure thresholds and processing parameters before running the analysis.")

st.sidebar.subheader("Scene & Frame Filtering")
threshold_val = st.sidebar.slider(
    "Scene Detection Sensitivity",
    min_value=0.05,
    max_value=1.00,
    value=0.30,
    step=0.05,
    help="Lower values detect more scene changes. Higher values detect fewer (only drastic) transitions."
)

st.sidebar.markdown("**Frame Filtering Granularity**")
granularity_level = st.sidebar.selectbox(
    "Select Level",
    ["Low (Fewer frames, faster)", "Medium (Balanced default)", "High (More frames, detailed)"],
    index=1,
    help="Determines how aggressively duplicate or highly similar video frames are filtered out. High level processes more keyframes for higher summarization detail."
)

granularity_mapping = {
    "Low (Fewer frames, faster)": 0.20,
    "Medium (Balanced default)": 0.40,
    "High (More frames, detailed)": 0.65
}
similarity_threshold_val = granularity_mapping[granularity_level]

# Default to Sequential/Native Interleaved mode
processing_mode = "Sequential/Native Interleaved"

batch_size_val = st.sidebar.selectbox(
    "VLM Batch Size",
    [2, 8, 16, 32],
    index=0,
    help="Number of segments processed simultaneously. A batch size of 2 is recommended for Native Interleaved mode to prevent excessive token padding overhead."
)

st.title("AI Video Summarizer Dashboard")

# TOP SECTION: Video Input + Processing (combined)
with st.container():
    st.subheader("Video Input & Processing")
    input_col, action_col = st.columns([5, 1], gap="medium")

    with input_col:
        source_col, value_col = st.columns([2, 5], gap="small")
        with source_col:
            source_type = st.radio("Video Source", ["Local file", "YouTube link"], horizontal=True)
        with value_col:
            uploaded_file = None
            youtube_url = ""
            if source_type == "Local file":
                uploaded_file = st.file_uploader(
                    "Choose a video file",
                    type=["mp4", "mov", "avi"],
                    label_visibility="collapsed",
                )
                if uploaded_file is not None:
                    save_path = os.path.join(BASE_DIR, "data", "raw_videos", uploaded_file.name)
                    if os.name == 'nt':
                        save_path = save_path.replace("\\", "/")
                    
                    # Track in session state to check if a file was uploaded/re-uploaded
                    if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.video_path = save_path
                        clear_video_cache()
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    st.success(f"File saved to: {save_path}")
                else:
                    st.session_state.uploaded_file_name = None
            else:
                youtube_url = st.text_input(
                    "Paste YouTube URL",
                    placeholder="https://www.youtube.com/watch?v=...",
                    label_visibility="collapsed",
                )
                if youtube_url:
                    if is_youtube_url(youtube_url):
                        normalized_url = youtube_url.strip()
                        if st.session_state.video_path != normalized_url:
                            st.session_state.video_path = normalized_url
                            clear_video_cache()
                    else:
                        st.warning("Please enter a valid YouTube URL.")

    with action_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="primary-btn-anchor"></div>', unsafe_allow_html=True)
        run_clicked = st.button("Load Data / Process", use_container_width=True)

    if run_clicked:
        if source_type == "Local file" and uploaded_file is None:
            st.error("❌ No video file uploaded! Please choose a local video file first.")
        elif source_type == "YouTube link" and (('youtube_url' not in locals()) or not youtube_url.strip()):
            st.error("❌ YouTube link is empty! Please provide a valid YouTube URL first.")
        else:
            selected_video = st.session_state.video_path
            # Check if this video has already been processed and exists on disk
            processed_path_file = os.path.join(OUTPUTS_DIR, "processed_video_path.txt")
            processed_params_file = os.path.join(OUTPUTS_DIR, "processed_video_params.json")
            already_processed = False
            
            if os.path.exists(processed_path_file) and os.path.exists(processed_params_file):
                try:
                    with open(processed_path_file, "r", encoding="utf-8") as f:
                        saved_path = f.read().strip()
                    with open(processed_params_file, "r", encoding="utf-8") as f:
                        saved_params = json.load(f)
                    
                    current_params = {
                        "threshold": threshold_val,
                        "similarity_threshold": similarity_threshold_val,
                        "use_multimodal": (processing_mode == "Sequential/Native Interleaved"),
                        "batch_size": batch_size_val
                    }
                    
                    if saved_path == selected_video and saved_params == current_params:
                        # Check if all required outputs exist
                        required_files = [
                            os.path.join(OUTPUTS_DIR, "transcript.json"),
                            os.path.join(OUTPUTS_DIR, "embeddings.npy"),
                            os.path.join(OUTPUTS_DIR, "final_topic_summaries.json"),
                            os.path.join(OUTPUTS_DIR, "final_summary.md"),
                        ]
                        if all(os.path.exists(fpath) for fpath in required_files):
                            already_processed = True
                except Exception:
                    pass
                except Exception:
                    pass
            
            if already_processed:
                st.session_state.data_loaded = True
                st.success("Loading existing processed results from cache...")
                time.sleep(1.0)
                st.rerun()
            else:
                # Instantly purge previous video outputs from the filesystem
                st.session_state.data_loaded = False
                st.session_state.search_results = []
                st.session_state.start_time = 0
                st.session_state.search_query_input = ""
                
                # Delete the old processed video path indicator
                if os.path.exists(processed_path_file):
                    try:
                        os.remove(processed_path_file)
                    except Exception:
                        pass
                
                for fname in ["frame_comparison_final.json", "clustering_graph.png", "interleaved_results.json", "transcript.json", "final_topic_summaries.json", "final_summary.md", "embeddings.npy", "chapter_summaries.txt"]:
                    fpath = os.path.join(OUTPUTS_DIR, fname)
                    if os.path.exists(fpath):
                        try:
                            os.remove(fpath)
                        except Exception:
                            pass
            
            pipeline_steps = [
                {"name": "Extract Frames & Audio", "status": "pending", "duration": ""},
                {"name": "Compute Frame Diffs", "status": "pending", "duration": ""},
                {"name": "ASR & VLM Transcriptions", "status": "pending", "duration": ""},
                {"name": "Build Combined Timeline", "status": "pending", "duration": ""},
                {"name": "Vector Indexing", "status": "pending", "duration": ""},
                {"name": "Dynamic Subtopic Clustering", "status": "pending", "duration": ""},
                {"name": "Subtopic Summarization", "status": "pending", "duration": ""},
                {"name": "Final Summary Generation", "status": "pending", "duration": ""},
            ]
            
            step_map = {
                "1. Extract Frames & Audio": 0,
                "3. Compute Frame Diffs": 1,
                "3.5. Chunk Audio": 2,
                "4 & 5. Native Multimodal Processing": 2,
                "4 & 5. Parallel VLM & ASR": 2,
                "6. Adapt Multimodal Output": 3,
                "6. Build Timeline": 3,
                "7. Embed and Search": 4,
                "8. Cluster Subtopics": 5,
                "9. Summarize Clusters": 6,
                "10. Final Video Summary": 7,
            }

            # Layout columns for real-time preview
            st.markdown("<h3 style='margin-top:20px;'>⚡ Pipeline Execution Studio</h3>", unsafe_allow_html=True)
            left_col, right_col = st.columns([1, 1], gap="large")
            
            with left_col:
                st.subheader("⚙️ Progress Tracker")
                stepper_placeholder = st.empty()
                progress_bar = st.progress(0.0)
                
                st.subheader("💻 Live Execution Logs")
                log_placeholder = st.empty()
                log_history = []
                
            with right_col:
                preview_header = st.empty()
                preview_content = st.empty()
                
                transcripts_header = st.empty()
                transcripts_content = st.empty()
                
                subtopics_header = st.empty()
                subtopics_content = st.empty()

            try:
                # Spawn unbuffered subprocess
                process = run_pipeline_stream(
                    selected_video,
                    threshold=threshold_val,
                    similarity_threshold=similarity_threshold_val,
                    use_multimodal=(processing_mode == "Sequential/Native Interleaved"),
                    batch_size=batch_size_val
                )
                if process is None:
                    st.error("Pipeline process could not be initialized.")
                    st.stop()
                if process.stdout is None:
                    st.error("Process stdout is None. Piping is not available.")
                    st.stop()
                current_step_idx = -1
                
                # Dynamic update loop
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    line_str = line.strip()
                    if not line_str:
                        continue
                        
                    # Add to developer console logs
                    log_history.append(line_str)
                    log_placeholder.code("\n".join(log_history[-12:]))
                    
                    # Update step status on "[STARTED]"
                    if "[STARTED]" in line_str:
                        for step_key, idx in step_map.items():
                            if step_key in line_str:
                                for prev_idx in range(idx):
                                    if pipeline_steps[prev_idx]["status"] == "pending":
                                        pipeline_steps[prev_idx]["status"] = "success"
                                pipeline_steps[idx]["status"] = "active"
                                current_step_idx = idx
                                break
                                
                    # Update step duration and status on "[FINISHED]"
                    elif "[FINISHED]" in line_str:
                        for step_key, idx in step_map.items():
                            if step_key in line_str:
                                pipeline_steps[idx]["status"] = "success"
                                time_match = re.search(r"in ([\d.]+) seconds", line_str)
                                if time_match:
                                    seconds_val = float(time_match.group(1))
                                    if seconds_val < 0.1:
                                        pipeline_steps[idx]["duration"] = f" ({seconds_val:.3f}s)"
                                    else:
                                        pipeline_steps[idx]["duration"] = f" ({seconds_val:.1f}s)"
                                break
                    
                    # Compute relative progress bar percentage
                    prog_val = 0.0
                    if current_step_idx >= 0:
                        prog_val = (current_step_idx + 0.5) / len(pipeline_steps)
                    progress_bar.progress(max(0.0, min(1.0, prog_val)))
                    
                    # Render custom HTML stepper
                    stepper_html = "<div class='timeline-stepper'>"
                    for i, step in enumerate(pipeline_steps):
                        status_class = step["status"]
                        stepper_html += f"""
<div class="timeline-item {status_class}">
<div class="timeline-content">
<strong>Step {i+1}: {step['name']}</strong>{step['duration']}
</div>
</div>
"""
                    stepper_html += "</div>"
                    stepper_placeholder.markdown(stepper_html, unsafe_allow_html=True)
                    
                    # ─── Dynamic Live Renders ───
                    
                    # 1. Keyframes & Clustering Graph Preview
                    json_file = os.path.join(OUTPUTS_DIR, "frame_comparison_final.json")
                    graph_file = os.path.join(OUTPUTS_DIR, "clustering_graph.png")
                    
                    if os.path.exists(json_file):
                        try:
                            with open(json_file, 'r') as f:
                                metrics = json.load(f)
                            keyframes = [m for m in metrics if m.get('is_clear_keyframe', False)]
                            if keyframes:
                                preview_header.markdown(f"#### 🖼️ Keyframe Selection ({len(keyframes)} Clusters)")
                                with preview_content.container(height=420):
                                    if os.path.exists(graph_file):
                                        st.image(graph_file, caption="Dynamic Cosine Agglomerative Clustering Scatter Plot", use_container_width=True)
                                        st.divider()
                                    
                                    st.markdown("**Selected Cluster Representatives:**")
                                    cols_per_row = 5
                                    for row_idx in range(0, len(keyframes), cols_per_row):
                                        row_keyframes = keyframes[row_idx:row_idx + cols_per_row]
                                        cols = st.columns(cols_per_row)
                                        for k_idx, kf in enumerate(row_keyframes):
                                            frame_path = os.path.join(BASE_DIR, "data", "frames", kf['filename'])
                                            if os.path.exists(frame_path):
                                                cols[k_idx].image(frame_path, caption=f"Frame {kf.get('frame_index', k_idx)} ({kf.get('timestamp_sec', 0.0):.1f}s)", use_container_width=True)
                                            else:
                                                cols[k_idx].empty()
                                        for pad_idx in range(len(row_keyframes), cols_per_row):
                                            cols[pad_idx].empty()
                            else:
                                preview_header.empty()
                                preview_content.empty()
                        except Exception as e:
                            preview_header.markdown(f"*Loading keyframes...*")
                            preview_content.empty()
                    else:
                        preview_header.empty()
                        preview_content.empty()
                            
                    # 2. Transcription & Analysis Feed
                    multimodal_path = os.path.join(OUTPUTS_DIR, "interleaved_results.json")
                    transcript_path = os.path.join(OUTPUTS_DIR, "transcript.json")
                    
                    if os.path.exists(multimodal_path):
                        try:
                            with open(multimodal_path, 'r', encoding='utf-8') as f:
                                chunks = json.load(f)
                            if chunks:
                                transcripts_header.markdown("#### 🎙️ Multimodal Analysis Feed")
                                trans_html = "<div class='scroll-container' style='max-height: 250px;'>"
                                for chunk in chunks:
                                    trans_html += f"""
<div class="topic-card" style="padding: 10px; margin-bottom: 8px;">
<span style="font-size: 0.8em; color: var(--text-soft);">[{chunk.get('start_sec', 0.0):.1f}s - {chunk.get('end_sec', 0.0):.1f}s]</span>
<p style="font-size: 0.88em; margin: 2px 0;">{chunk.get('analysis', '')}</p>
</div>
"""
                                trans_html += "</div>"
                                transcripts_content.markdown(trans_html, unsafe_allow_html=True)
                            else:
                                transcripts_header.empty()
                                transcripts_content.empty()
                        except Exception:
                            transcripts_header.empty()
                            transcripts_content.empty()
                    elif os.path.exists(transcript_path):
                        try:
                            with open(transcript_path, 'r', encoding='utf-8') as f:
                                chunks = json.load(f)
                            if chunks:
                                transcripts_header.markdown("#### 🗣️ Speech Transcriptions")
                                trans_html = "<div class='scroll-container' style='max-height: 250px;'>"
                                for chunk in chunks:
                                    trans_html += f"""
<div class="topic-card" style="border-left: 4px solid #2e7d32; padding: 10px; margin-bottom: 8px;">
<span style="font-size: 0.8em; color: var(--text-soft);">[{chunk.get('start_sec', 0.0):.1f}s - {chunk.get('end_sec', 0.0):.1f}s]</span>
<p style="font-size: 0.88em; margin: 2px 0;">{chunk.get('text', '')}</p>
</div>
"""
                                trans_html += "</div>"
                                transcripts_content.markdown(trans_html, unsafe_allow_html=True)
                            else:
                                transcripts_header.empty()
                                transcripts_content.empty()
                        except Exception:
                            transcripts_header.empty()
                            transcripts_content.empty()
                    else:
                        transcripts_header.empty()
                        transcripts_content.empty()
                            
                    # 3. Subtopics Summaries
                    summaries_path = os.path.join(OUTPUTS_DIR, "final_topic_summaries.json")
                    if os.path.exists(summaries_path):
                        try:
                            with open(summaries_path, 'r', encoding='utf-8') as f:
                                subtopics = json.load(f)
                            if subtopics:
                                subtopics_header.markdown("#### 🗂️ Live Subtopics")
                                sub_html = "<div class='scroll-container' style='max-height: 200px;'>"
                                for topic in subtopics:
                                    title = topic.get("title", f"Topic {topic.get('subtopic_id')}").replace("TITLE:", "").strip()
                                    desc = topic.get("description", "Summarizing...").replace("DESCRIPTION:", "").strip()
                                    sub_html += f"""
<div class="topic-card" style="border-left: 4px solid #174ea6; padding: 8px; margin-bottom: 8px;">
<strong style="font-size: 0.9em;">{title}</strong>
<p style="font-size: 0.82em; color: var(--text-soft); margin: 2px 0;">{desc}</p>
</div>
"""
                                sub_html += "</div>"
                                subtopics_content.markdown(sub_html, unsafe_allow_html=True)
                            else:
                                subtopics_header.empty()
                                subtopics_content.empty()
                        except Exception:
                            subtopics_header.empty()
                            subtopics_content.empty()
                    else:
                        subtopics_header.empty()
                        subtopics_content.empty()

                process.stdout.close()
                return_code = process.wait()
                
                if return_code == 0 and os.path.exists(os.path.join(OUTPUTS_DIR, "final_topic_summaries.json")):
                    for step in pipeline_steps:
                        step["status"] = "success"
                    progress_bar.progress(1.0)
                    
                    # Save the processed video path and parameters to enable quick load next time
                    processed_path_file = os.path.join(OUTPUTS_DIR, "processed_video_path.txt")
                    processed_params_file = os.path.join(OUTPUTS_DIR, "processed_video_params.json")
                    try:
                        with open(processed_path_file, "w", encoding="utf-8") as f:
                            f.write(selected_video)
                        with open(processed_params_file, "w", encoding="utf-8") as f:
                            current_params = {
                                "threshold": threshold_val,
                                "similarity_threshold": similarity_threshold_val,
                                "use_multimodal": (processing_mode == "Sequential/Native Interleaved"),
                                "batch_size": batch_size_val
                            }
                            json.dump(current_params, f)
                    except Exception:
                        pass
                    
                    st.cache_data.clear()
                    st.session_state.data_loaded = True
                    st.success("Pipeline completed and outputs loaded successfully!")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.session_state.data_loaded = False
                    st.error("Pipeline failed while processing the selected video.")
                    
            except Exception as e:
                st.session_state.data_loaded = False
                st.error(f"Pipeline execution encountered an error: {e}")

if st.session_state.data_loaded:
    try:
        transcripts, embeddings, summaries = load_data(get_outputs_cache_buster())
        overall_summary = load_overall_summary(get_outputs_cache_buster())
        embedder = load_embedder()
        topic_lookup = build_topic_lookup(summaries)
    except Exception as e:
        st.error(f"Error loading files: {e}")
        st.stop()

    # MIDDLE SECTION: Left Overall Summary, Right Subtopic Summaries
    top_left, top_right = st.columns([1, 1], gap="large")


    with top_left:
        # Create tabs for Overall Summary and Subtopics Summaries
        tab_overall, tab_subtopics = st.tabs(["📄 Overall Summary", "🗂️ Subtopic Summaries"])
        
        with tab_overall:
            clean_tts = overall_summary.replace("**", "").replace("*", "").replace("#", "")
            header_html = f"""
            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }}
                .header-container {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    height: 35px;
                }}
                .header-title {{
                    margin: 0;
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: var(--text-main);
                }}
                .speaker-btn {{
                    background: none;
                    border: none;
                    font-size: 1.3em;
                    cursor: pointer;
                    padding: 0;
                    margin: 0;
                    line-height: 1;
                    outline: none;
                    transition: transform 0.1s ease;
                }}
                .speaker-btn:hover {{
                    transform: scale(1.1);
                }}
            </style>
            <div class="header-container">
                <h3 class="header-title">Overall Summary</h3>
                <button id="tts-speaker-btn" class="speaker-btn" onclick="toggleTTS()">🔊</button>
            </div>
            <script>
                var ttsPlaying = false;
                var ttsUtterance = null;
                
                function toggleTTS() {{
                    var btn = document.getElementById("tts-speaker-btn");
                    var synth = window.speechSynthesis;
                    
                    if (!ttsPlaying) {{
                        var text = {json.dumps(clean_tts)};
                        ttsUtterance = new SpeechSynthesisUtterance(text);
                        ttsUtterance.lang = 'en-US';
                        
                        ttsUtterance.onend = function() {{
                            ttsPlaying = false;
                            btn.innerHTML = "🔊";
                        }};
                        ttsUtterance.onerror = function() {{
                            ttsPlaying = false;
                            btn.innerHTML = "🔊";
                        }};
                        
                        synth.cancel();
                        synth.speak(ttsUtterance);
                        ttsPlaying = true;
                        btn.innerHTML = "🔇";
                    }} else {{
                        synth.cancel();
                        ttsPlaying = false;
                        btn.innerHTML = "🔊";
                    }}
                }}
            </script>
            """
            components.html(header_html, height=35)
    
            # ── Video Metadata Panel ──────────────────────────────────────
            video_meta = get_video_metadata(
                st.session_state.video_path, transcripts, summaries
            )
            st.markdown(f"""
            <div style="
                background-color: #ffffff !important;
                border: 1px solid var(--border-soft);
                border-radius: 12px;
                padding: 14px 18px;
                margin-bottom: 14px;
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 6px 24px;
                font-size: 0.88em;
                color: #000000 !important;
            ">
                <div style="grid-column: span 3;"><strong>📹 Video:</strong> {escape(video_meta['name'])}</div>
                <div><strong>⏱️ Duration:</strong> {video_meta['duration']}</div>
                <div><strong>⚙️ Processing:</strong> {video_meta['processing_time']}</div>
                <div><strong>📅 Processed:</strong> {video_meta['processed_at']}</div>
                <div><strong>📊 Segments:</strong> {video_meta['segments']}</div>
                <div><strong>🖼️ Keyframes:</strong> {video_meta['keyframes']}</div>
                <div><strong>🗂️ Subtopics:</strong> {video_meta['subtopics']}</div>
            </div>
            """, unsafe_allow_html=True)
    
            # Clean overall summary view with aligned height
            st.markdown(f"""
            <div class="scroll-container" id="summary-text-content" style="height: 380px; background-color: #ffffff !important; color: #000000 !important;">
                {overall_summary}
            </div>
            """, unsafe_allow_html=True)
            
        with tab_subtopics:
            subtopics_data = []
            for idx, topic in enumerate(summaries):
                title = topic.get("title", f"Topic {topic.get('subtopic_id')}")
                if "TITLE:" in title:
                    title = title.replace("TITLE:", "").strip()
                desc = topic.get("description", "No description provided.").replace("DESCRIPTION:", "").strip()
                summary = topic.get("summary", "").replace("SUMMARY:", "").strip()
                
                # Text to read: "Title. Summary"
                read_text = f"{title}. {summary}".replace("**", "").replace("*", "").replace("#", "")
                
                subtopics_data.append({
                    "title": title,
                    "desc": desc,
                    "summary": summary,
                    "read_text": read_text
                })
                
            cards_html = ""
            for idx, item in enumerate(subtopics_data):
                esc_title = escape(item['title'])
                esc_desc = escape(item['desc'])
                esc_summary = escape(item['summary'])
                
                cards_html += f"""
                <div class="topic-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                        <h4 style="margin: 0; margin-bottom: 6px; font-size: 1.05rem; font-weight: 600; color: var(--text-main); flex: 1;">{esc_title}</h4>
                        <button id="tts-btn-{idx}" class="speaker-btn" onclick="toggleTopicTTS({idx})">🔊</button>
                    </div>
                    <p style="font-size: 0.9em; color: var(--text-soft); margin-top: 4px; margin-bottom: 8px;"><i>{esc_desc}</i></p>
                    <p style="font-size: 0.92em; color: var(--text-main); line-height: 1.4; margin: 4px 0;">{esc_summary}</p>
                </div>
                """
                
            subtopics_html = f"""
            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }}
                .scroll-container {{
                    height: 550px;
                    overflow-y: auto;
                    overflow-x: hidden;
                    padding: 10px;
                    border: 1px solid var(--border-soft) !important;
                    border-radius: 10px;
                    background-color: #ffffff !important;
                    color: var(--text-main) !important;
                }}
                .scroll-container::-webkit-scrollbar {{
                    width: 8px;
                }}
                .scroll-container::-webkit-scrollbar-thumb {{
                    background: rgba(255, 255, 255, 0.25);
                    border-radius: 10px;
                }}
                .topic-card {{
                    background: #ffffff !important;
                    padding: 18px;
                    border-radius: 12px;
                    margin-bottom: 16px;
                    border: 1px solid var(--border-soft) !important;
                    border-left: 5px solid #2f7be5 !important;
                    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
                    color: var(--text-main);
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
                .speaker-btn {{
                    background: none;
                    border: none;
                    font-size: 1.2em;
                    cursor: pointer;
                    padding: 0;
                    margin: 0;
                    line-height: 1;
                    outline: none;
                    transition: transform 0.1s ease;
                }}
                .speaker-btn:hover {{
                    transform: scale(1.1);
                }}
            </style>
            <div class="scroll-container">
                {cards_html}
            </div>
            <script>
                var activeIndex = -1;
                var synth = window.speechSynthesis;
                var currentUtterance = null;
                
                function toggleTopicTTS(idx) {{
                    var btn = document.getElementById("tts-btn-" + idx);
                    var subtopics = {json.dumps(subtopics_data)};
                    var readText = subtopics[idx].read_text;
                    
                    if (activeIndex === idx) {{
                        synth.cancel();
                        btn.innerHTML = "🔊";
                        activeIndex = -1;
                    }} else {{
                        if (activeIndex !== -1) {{
                            var oldBtn = document.getElementById("tts-btn-" + activeIndex);
                            if (oldBtn) oldBtn.innerHTML = "🔊";
                        }}
                        
                        synth.cancel();
                        
                        currentUtterance = new SpeechSynthesisUtterance(readText);
                        currentUtterance.lang = 'en-US';
                        
                        currentUtterance.onend = function() {{
                            btn.innerHTML = "🔊";
                            activeIndex = -1;
                        }};
                        currentUtterance.onerror = function() {{
                            btn.innerHTML = "🔊";
                            activeIndex = -1;
                        }};
                        
                        synth.speak(currentUtterance);
                        btn.innerHTML = "🔇";
                        activeIndex = idx;
                    }}
                }}
            </script>
            """
            components.html(subtopics_html, height=560)
 
 
    with top_right:
        # Create tabs for Word Cloud and Knowledge Graph
        tab_cloud, tab_graph = st.tabs(["☁️ Word Cloud", "🧠 Knowledge Graph"])
        
        # Fetch visualization data
        viz_data = get_wordcloud_and_graph_data(transcripts, summaries)
        
        with tab_cloud:
            cloud_header_html = """
            <style>
                html, body {
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }
                .header-container {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    height: 35px;
                }
                .header-title {
                    margin: 0;
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: var(--text-main);
                }
            </style>
            <div class="header-container">
                <h3 class="header-title">Word Cloud Visualization</h3>
            </div>
            """
            components.html(cloud_header_html, height=35)

            wordcloud_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        height: 100%;
                        overflow: hidden;
                        background: transparent;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    }}
                    .pane {{
                        height: 515px;
                        background: transparent;
                        border: 1px solid rgba(255, 255, 255, 0.15);
                        border-radius: 12px;
                        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.15);
                        display: flex;
                        position: relative;
                        align-items: center;
                        justify-content: center;
                        box-sizing: border-box;
                    }}
                    #wordcloud-canvas {{
                        width: 100%;
                        height: 100%;
                    }}
                    .zoom-controls {{
                        position: absolute;
                        bottom: 20px;
                        right: 20px;
                        display: flex;
                        gap: 8px;
                        z-index: 10;
                    }}
                    .zoom-controls button {{
                        background: rgba(255, 255, 255, 0.95);
                        border: 1px solid #2f7be5;
                        border-radius: 6px;
                        width: 34px;
                        height: 34px;
                        font-size: 16px;
                        font-weight: bold;
                        color: #2f7be5;
                        cursor: pointer;
                        box-shadow: 0 2px 12px rgba(47, 123, 229, 0.15);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: all 0.2s ease;
                        outline: none;
                    }}
                    .zoom-controls button:hover {{
                        background: #2f7be5;
                        color: #ffffff;
                        box-shadow: 0 4px 16px rgba(47, 123, 229, 0.3);
                    }}
                </style>
            </head>
            <body>
                <div class="pane">
                    <canvas id="wordcloud-canvas"></canvas>
                    <div class="zoom-controls">
                        <button onclick="zoomIn()">➕</button>
                        <button onclick="zoomOut()">➖</button>
                    </div>
                </div>
                <script>
                    var wordCloudData = {json.dumps(viz_data['wordcloud'])};
                    var zoomFactor = 1.0;
                    
                    function zoomIn() {{
                        zoomFactor *= 1.2;
                        drawWordCloud();
                    }}
                    
                    function zoomOut() {{
                        zoomFactor /= 1.2;
                        drawWordCloud();
                    }}
                    
                    function drawWordCloud() {{
                        var canvas = document.getElementById('wordcloud-canvas');
                        var ctx = canvas.getContext('2d');
                        
                        var rect = canvas.parentElement.getBoundingClientRect();
                        canvas.width = rect.width * window.devicePixelRatio;
                        canvas.height = rect.height * window.devicePixelRatio;
                        canvas.style.width = rect.width + 'px';
                        canvas.style.height = rect.height + 'px';
                        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
                        
                        var w = rect.width;
                        var h = rect.height;
                        
                        ctx.clearRect(0, 0, w, h);
                        
                        if (wordCloudData.length === 0) {{
                            ctx.fillStyle = '#c3d1ec';
                            ctx.font = '14px Segoe UI';
                            ctx.fillText('No words loaded', w/2 - 50, h/2);
                            return;
                        }}
                        
                        var maxVal = Math.max.apply(Math, wordCloudData.map(function(o){{return o.size;}}));
                        var minVal = Math.min.apply(Math, wordCloudData.map(function(o){{return o.size;}}));
                        
                        var maxFontSize = 38;
                        var minFontSize = 13;
                        
                        var placedWords = [];
                        var colors = ['#7fb0f8', '#a5b4fc', '#818cf8', '#6366f1', '#a78bfa', '#f472b6', '#38bdf8', '#22d3ee'];
                        
                        wordCloudData.forEach(function(item, idx) {{
                            var fontSize = minFontSize;
                            if (maxVal > minVal) {{
                                fontSize = minFontSize + ((item.size - minVal) / (maxVal - minVal)) * (maxFontSize - minFontSize);
                            }}
                            
                            // Scale font size using zoomFactor
                            var finalFontSize = fontSize * zoomFactor;
                            ctx.font = 'bold ' + Math.round(finalFontSize) + 'px Segoe UI';
                            var wordWidth = ctx.measureText(item.text).width;
                            var wordHeight = finalFontSize;
                            
                            var placed = false;
                            var radius = 0;
                            var angle = 0;
                            var step = 0.15;
                            var radiusStep = 0.45;
                            
                            var cx = w / 2;
                            var cy = h / 2;
                            
                            while (!placed && radius < Math.max(w, h)) {{
                                var x = cx + radius * Math.cos(angle) - wordWidth / 2;
                                var y = cy + radius * Math.sin(angle) + wordHeight / 3;
                                
                                var overlap = false;
                                for (var i = 0; i < placedWords.length; i++) {{
                                    var pw = placedWords[i];
                                    if (x < pw.x + pw.w && x + wordWidth > pw.x &&
                                        y - wordHeight < pw.y && y > pw.y - pw.h) {{
                                        overlap = true;
                                        break;
                                    }}
                                }}
                                
                                if (!overlap) {{
                                    if (x > 5 && x + wordWidth < w - 5 && y - wordHeight > 5 && y < h - 5) {{
                                        ctx.fillStyle = colors[idx % colors.length];
                                        ctx.fillText(item.text, x, y);
                                        placedWords.push({{ x: x, y: y, w: wordWidth, h: wordHeight }});
                                        placed = true;
                                    }}
                                }}
                                
                                angle += step;
                                radius += radiusStep;
                            }}
                        }});
                    }}
                    
                    setTimeout(drawWordCloud, 100);
                    window.addEventListener('resize', drawWordCloud);
                </script>
            </body>
            </html>
            """
            components.html(wordcloud_html, height=525)
            
        with tab_graph:
            graph_header_html = """
            <style>
                html, body {
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }
                .header-container {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    height: 35px;
                }
                .header-title {
                    margin: 0;
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: var(--text-main);
                }
            </style>
            <div class="header-container">
                <h3 class="header-title">Interactive Knowledge Graph</h3>
            </div>
            """
            components.html(graph_header_html, height=35)

            graph_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        height: 100%;
                        overflow: hidden;
                        background: transparent;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    }}
                    .pane {{
                        height: 515px;
                        background: transparent;
                        border: 1px solid rgba(255, 255, 255, 0.15);
                        border-radius: 12px;
                        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.15);
                        display: flex;
                        flex-direction: column;
                        box-sizing: border-box;
                        overflow: hidden;
                    }}
                    #network-container {{
                        height: 515px;
                        position: relative;
                    }}
                    #network-graph {{
                        width: 100%;
                        height: 100%;
                    }}
                    #details-overlay {{
                        position: absolute;
                        top: 15px;
                        left: 15px;
                        width: 290px;
                        max-height: 280px;
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        -webkit-backdrop-filter: blur(10px);
                        border: 1px solid rgba(47, 123, 229, 0.25);
                        border-radius: 12px;
                        padding: 12px 14px;
                        box-shadow: 0 8px 32px rgba(47, 123, 229, 0.12);
                        z-index: 1000;
                        display: none;
                        overflow-y: auto;
                        box-sizing: border-box;
                    }}
                    .details-table {{
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 0.76em;
                    }}
                    .details-table td {{
                        padding: 6px 4px;
                        vertical-align: top;
                    }}
                    .details-table td.prop-title {{
                        font-weight: 600;
                        color: #5b6f95;
                        width: 25%;
                    }}
                    .details-table td.prop-val {{
                        color: #0f1f3d;
                        width: 75%;
                        white-space: normal;
                        word-break: break-word;
                        line-height: 1.4;
                    }}
                    .zoom-controls {{
                        position: absolute;
                        bottom: 20px;
                        right: 20px;
                        display: flex;
                        gap: 8px;
                        z-index: 1000;
                    }}
                    .zoom-controls button {{
                        background: rgba(255, 255, 255, 0.95);
                        border: 1px solid #2f7be5;
                        border-radius: 6px;
                        width: 34px;
                        height: 34px;
                        font-size: 16px;
                        font-weight: bold;
                        color: #2f7be5;
                        cursor: pointer;
                        box-shadow: 0 2px 12px rgba(47, 123, 229, 0.15);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: all 0.2s ease;
                        outline: none;
                    }}
                    .zoom-controls button:hover {{
                        background: #2f7be5;
                        color: #ffffff;
                        box-shadow: 0 4px 16px rgba(47, 123, 229, 0.3);
                    }}
                </style>
                <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
            </head>
            <body>
                <div class="pane">
                    <div id="network-container">
                        <div id="network-graph"></div>
                        <div class="zoom-controls">
                            <button onclick="zoomIn()">➕</button>
                            <button onclick="zoomOut()">➖</button>
                        </div>
                        <div id="details-overlay">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(47, 123, 229, 0.15); padding-bottom: 5px; margin-bottom: 8px;">
                                <span style="font-weight: 600; font-size: 0.82em; color: #0f1f3d;">🔍 Node Inspector</span>
                                <button onclick="closeOverlay()" style="background: none; border: none; font-size: 1.1em; cursor: pointer; color: #5b6f95; padding: 0; line-height: 1; outline: none;">✕</button>
                            </div>
                            <table class="details-table">
                                <tbody>
                                    <tr>
                                        <td class="prop-title">Name</td>
                                        <td id="overlay-name" class="prop-val" style="font-weight: bold;"></td>
                                    </tr>
                                    <tr>
                                        <td class="prop-title">Type</td>
                                        <td id="overlay-type" class="prop-val"></td>
                                    </tr>
                                    <tr>
                                        <td class="prop-title">Info</td>
                                        <td id="overlay-details" class="prop-val"></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <script>
                    var graphData = {json.dumps(viz_data['graph'])};
                    var container = document.getElementById('network-graph');
                    
                    var styledNodes = graphData.nodes.map(function(node) {{
                        var base = {{
                            id: node.id,
                            label: node.label,
                            title: node.title,
                            font: {{ 
                                face: 'Segoe UI', 
                                size: 12, 
                                color: '#31333f',
                                highlight: '#000000'
                            }}
                        }};
                        
                        if (node.group === 0) {{
                            base.color = {{
                                background: '#2f7be5',
                                border: '#174ea6',
                                hover: {{ background: '#1f63c8', border: '#174ea6' }}
                            }};
                            base.font.color = '#ffffff';
                            base.font.highlight = '#ffffff';
                            base.font.size = 14;
                            base.font.bold = true;
                            base.shape = 'box';
                            base.margin = 12;
                        }} else if (node.group === 1) {{
                            base.color = {{
                                background: '#e9f1ff',
                                border: '#2f7be5',
                                hover: {{ background: '#d7e6ff', border: '#1f63c8' }}
                            }};
                            base.shape = 'dot';
                            base.size = 16;
                            base.font.color = '#1f63c8';
                            base.font.highlight = '#000000';
                        }} else {{
                            base.color = {{
                                background: '#f5f7fa',
                                border: '#cfd8dc',
                                hover: {{ background: '#eceff1', border: '#b0bec5' }}
                            }}
                            base.shape = 'dot';
                            base.size = 9;
                            base.font.size = 10;
                            base.font.color = '#000000';
                            base.font.highlight = '#000000';
                        }}
                        base.group = node.group;
                        return base;
                    }});
                    
                    // Deterministic coordinates layout using loops (highly compatible)
                    var rootNode = null;
                    for (var i = 0; i < styledNodes.length; i++) {{
                        if (styledNodes[i].id === "video_root") {{
                            rootNode = styledNodes[i];
                            break;
                        }}
                    }}
                    if (rootNode) {{
                        rootNode.x = 0;
                        rootNode.y = -20;
                    }}
                    
                    var subtopics = [];
                    for (var i = 0; i < styledNodes.length; i++) {{
                        if (styledNodes[i].group === 1) {{
                            subtopics.push(styledNodes[i]);
                        }}
                    }}
                    
                    var numSubtopics = subtopics.length;
                    subtopics.forEach(function(sub, idx) {{
                        var angle = (2 * Math.PI * idx) / numSubtopics - (Math.PI / 2);
                        var r1 = 120; // radius from center
                        sub.x = r1 * Math.cos(angle);
                        sub.y = r1 * Math.sin(angle);
                        
                        var connectedLinks = [];
                        for (var j = 0; j < graphData.links.length; j++) {{
                            if (graphData.links[j].from === sub.id) {{
                                connectedLinks.push(graphData.links[j]);
                            }}
                        }}
                        
                        var kwNodes = [];
                        for (var k = 0; k < styledNodes.length; k++) {{
                            if (styledNodes[k].group === 2) {{
                                var isConnected = false;
                                for (var L = 0; L < connectedLinks.length; L++) {{
                                    if (connectedLinks[L].to === styledNodes[k].id) {{
                                        isConnected = true;
                                        break;
                                    }}
                                }}
                                if (isConnected) {{
                                    kwNodes.push(styledNodes[k]);
                                }}
                            }}
                        }}
                        
                        var numKws = kwNodes.length;
                        kwNodes.forEach(function(kw, kwIdx) {{
                            var fanSpread = 0.8;
                            var startAngle = angle - (fanSpread / 2);
                            var kwAngle = numKws > 1
                                ? startAngle + (fanSpread * kwIdx) / (numKws - 1)
                                : angle;
                                
                            var r2 = 65; // radius from subtopic
                            kw.x = sub.x + r2 * Math.cos(kwAngle);
                            kw.y = sub.y + r2 * Math.sin(kwAngle);
                        }});
                    }});
                    
                    var data = {{
                        nodes: new vis.DataSet(styledNodes),
                        edges: new vis.DataSet(graphData.links)
                    }};
                    
                    var options = {{
                        nodes: {{
                            borderWidth: 2,
                            shadow: true
                        }},
                        edges: {{
                            color: {{ color: 'rgba(44, 153, 255, 0.4)', highlight: '#2f7be5' }},
                            width: 1.5,
                            arrows: {{ to: {{ enabled: false }} }}
                        }},
                        physics: false,
                        interaction: {{
                            dragNodes: true,
                            dragView: true,
                            hover: true,
                            tooltipDelay: 100,
                            zoomView: false,
                            doubleClickZoom: false
                        }}
                    }};
                    
                    var network = new vis.Network(container, data, options);
                    
                    // Fit and center the graph dynamically as soon as the container size is negotiated (handles tab switching and resizing)
                    var resizeObserver = new ResizeObserver(function(entries) {{
                        for (var i = 0; i < entries.length; i++) {{
                            if (entries[i].contentRect.width > 0 && entries[i].contentRect.height > 0) {{
                                setTimeout(function() {{
                                    try {{
                                        network.fit();
                                    }} catch (e) {{}}
                                }}, 50);
                            }}
                        }}
                    }});
                    resizeObserver.observe(container);
                    
                    // Live details panel updater
                    function showNodeDetails(nodeId) {{
                        try {{
                            var node = null;
                            for (var i = 0; i < graphData.nodes.length; i++) {{
                                if (graphData.nodes[i].id === nodeId) {{
                                    node = graphData.nodes[i];
                                    break;
                                }}
                            }}
                            if (!node) return;
                            
                            var name = node.label;
                            var type = "";
                            var details = "";
                            
                            if (node.group === 0) {{
                                type = "📹 Video Root";
                                details = "Represents the overall summary context of the entire video presentation.";
                            }} else if (node.group === 1) {{
                                type = "🗂️ Subtopic";
                                var rawTitle = node.title || "";
                                details = rawTitle.replace(/<[^>]*>/g, ' ').trim();
                            }} else {{
                                type = "🔑 Key Term";
                                details = "Conceptual keyword extracted from transcripts linked directly to this subtopic.";
                            }}
                            
                            document.getElementById('overlay-name').innerText = name;
                            document.getElementById('overlay-type').innerText = type;
                            document.getElementById('overlay-details').innerText = details;
                            document.getElementById('details-overlay').style.display = 'block';
                        }} catch (e) {{
                            console.error("Details render error:", e);
                        }}
                    }}
                    
                    function resetDetails() {{
                        try {{
                            document.getElementById('details-overlay').style.display = 'none';
                        }} catch(e) {{}}
                    }}
                    
                    function closeOverlay() {{
                        try {{
                            document.getElementById('details-overlay').style.display = 'none';
                            network.unselectAll();
                        }} catch(e) {{}}
                    }}
                    
                    // Attach click-based select event listener
                    network.on("selectNode", function (params) {{
                        if (params && params.nodes && params.nodes.length > 0) {{
                            showNodeDetails(params.nodes[0]);
                        }}
                    }});
                    
                    network.on("deselectNode", function () {{
                        resetDetails();
                    }});
                    
                    // Zoom controls implementation
                    function zoomIn() {{
                        try {{
                            var scale = network.getScale();
                            network.moveTo({{
                                scale: scale * 1.35,
                                animation: {{ duration: 150 }}
                            }});
                        }} catch (e) {{}}
                    }}
                    
                    function zoomOut() {{
                        try {{
                            var scale = network.getScale();
                            network.moveTo({{
                                scale: scale / 1.35,
                                animation: {{ duration: 150 }}
                            }});
                        }} catch (e) {{}}
                    }}
                </script>
            </body>
            </html>
            """
            components.html(graph_html, height=525)
            
    st.divider()
    
    # BOTTOM SECTION: Left Semantic Search, Right Video Playback
    bottom_left, bottom_right = st.columns([1, 1], gap="large")
    
    with bottom_left:
        tab_search, tab_keyframes, tab_howto = st.tabs(["🔍 Semantic Search", "🖼️ Visual Keyframes", "📊 Subtopic Extraction"])
        
        with tab_search:
            st.subheader("Semantic Search")
            
            search_query = st.text_input(
                "Enter keyword or description to jump to specific context:",
                placeholder="e.g. exporting to youtube in 4k...",
                key="search_query_input"
            )
            score_threshold = 0.35
            INITIAL_DISPLAY = 3   # Show this many results initially
            
            # Initialize "view more" toggle in session state
            if 'show_all_results' not in st.session_state:
                st.session_state.show_all_results = False
            
            search_container = st.container(height=550)
            
            with search_container:
                if search_query:
                    with st.spinner("Searching timeline conceptually..."):
                        all_results = perform_search(
                            search_query, transcripts, embeddings, embedder,
                            threshold=score_threshold
                        )
                    st.session_state.search_results = all_results
    
                    if all_results:
                        # Determine how many to show
                        total_found = len(all_results)
                        if st.session_state.show_all_results:
                            display_results = all_results
                        else:
                            display_results = all_results[:INITIAL_DISPLAY]
    
                        st.success(
                            f"Found {total_found} relevant segment{'s' if total_found != 1 else ''} "
                            f"(score ≥ {score_threshold:.0%}) — "
                            f"showing {len(display_results)} of {total_found}"
                        )
    
                        desc_lookup = {
                            str(s.get("subtopic_id")): s.get("description", "")
                            for s in summaries
                        }
                        for i, result in enumerate(display_results, start=1):
                            match = result["match"]
                            score = result["score"]
                            hit_start, hit_end = get_segment_bounds(match)
                            hit_text = match.get("text", "")
    
                            subtopic = match.get("subtopic_id")
                            subtopic_str = str(subtopic) if subtopic is not None else "N/A"
                            topic_title = topic_lookup.get(subtopic_str, f"Topic {subtopic_str}")
    
                            label = (
                                f"Top {i}: {topic_title}\n\n"
                                f"🕒 {format_time(hit_start)} - {format_time(hit_end)}\n"
                                f"📊 Match: {score * 100:.1f}%\n\n"
                                f"{hit_text[:150]}..."
                            )
    
                            st.markdown('<div class="search-card-anchor"></div>', unsafe_allow_html=True)
                            if st.button(label, key=f"card_{i}", use_container_width=True):
                                st.session_state.start_time = int(hit_start)
                                st.rerun()
    
                        # ── "View More" / "Show Less" toggle ────────────
                        if total_found > INITIAL_DISPLAY:
                            if st.session_state.show_all_results:
                                st.markdown('<div class="utility-btn-anchor"></div>', unsafe_allow_html=True)
                                if st.button(
                                    f"▲ Show Less (top {INITIAL_DISPLAY} only)",
                                    key="show_less_btn",
                                    use_container_width=True,
                                ):
                                    st.session_state.show_all_results = False
                                    st.rerun()
                            else:
                                remaining = total_found - INITIAL_DISPLAY
                                st.markdown('<div class="utility-btn-anchor"></div>', unsafe_allow_html=True)
                                if st.button(
                                    f"▼ View More ({remaining} more segment{'s' if remaining != 1 else ''})",
                                    key="view_more_btn",
                                    use_container_width=True,
                                ):
                                    st.session_state.show_all_results = True
                                    st.rerun()
    
                    else:
                        st.warning(f"No relevant context found with score ≥ {score_threshold:.0%}.")
                else:
                    st.session_state.search_results = []
                    st.session_state.show_all_results = False
                    st.info("Enter a query to find related subtopics and jump to video segments.")
    
        with tab_keyframes:
            st.subheader("Visual Keyframes")
            
            json_file = os.path.join(OUTPUTS_DIR, "frame_comparison_final.json")
            graph_file = os.path.join(OUTPUTS_DIR, "clustering_graph.png")
            
            kf_container = st.container(height=650)
            with kf_container:
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r') as f:
                            metrics = json.load(f)
                        keyframes = [m for m in metrics if m.get('is_clear_keyframe', False)]
                        
                        if keyframes:
                            if os.path.exists(graph_file):
                                st.image(graph_file, caption="Dynamic Cosine Agglomerative Clustering Scatter Plot", use_container_width=True)
                                st.divider()
                            
                            st.markdown(f"**Selected Cluster Representatives ({len(keyframes)} total):**")
                            
                            cols_per_row = 3
                            for row_idx in range(0, len(keyframes), cols_per_row):
                                row_keyframes = keyframes[row_idx:row_idx + cols_per_row]
                                cols = st.columns(cols_per_row)
                                for k_idx, kf in enumerate(row_keyframes):
                                    frame_path = os.path.join(BASE_DIR, "data", "frames", kf['filename'])
                                    if os.path.exists(frame_path):
                                        cols[k_idx].image(frame_path, use_container_width=True)
                                        cols[k_idx].markdown('<div class="jump-btn-anchor"></div>', unsafe_allow_html=True)
                                        kf_time = kf.get('timestamp_sec', 0.0)
                                        if cols[k_idx].button(f"Jump to {format_time(kf_time)}", key=f"kf_btn_{row_idx}_{k_idx}", use_container_width=True):
                                            st.session_state.start_time = int(kf_time)
                                            st.rerun()
                                    else:
                                        cols[k_idx].empty()
                                for pad_idx in range(len(row_keyframes), cols_per_row):
                                    cols[pad_idx].empty()
                        else:
                            st.info("No keyframes selected by the clustering algorithm.")
                    except Exception as e:
                        st.error(f"Error loading keyframes: {e}")
                else:
                    st.info("Keyframes data not found. Run the pipeline to extract keyframes.")
    
        with tab_howto:
            st.subheader("How Subtopic Summaries Are Generated")
            
            howto_container = st.container(height=650)
            with howto_container:
                st.markdown("""
**The pipeline discovers and summarizes subtopics in 4 stages:**
                """)
                
                # Stage 1
                st.markdown("""
##### 1️⃣ Sentence Embedding
Each transcript segment is converted into a **384-dimensional vector** 
using the `all-MiniLM-L6-v2` sentence transformer. These embeddings 
capture the *semantic meaning* of each segment, so segments about similar 
topics end up close together in vector space.
                """)
                
                # Stage 2
                st.markdown("""
##### 2️⃣ Dynamic Hierarchical Agglomerative Clustering
Instead of pre-defining the number of subtopics or forcing a hard split, the pipeline clusters transcript segments dynamically:
- Transcripts are L2-normalized to calculate semantic similarity.
- A **bottom-up hierarchy** is constructed using **Ward's linkage**, minimizing variance within clusters.
- A **dynamic distance threshold** is applied to determine where to cut the tree.
- If the number of subtopics falls outside the dashboard limits (2–10), the distance threshold **adaptively relaxes or tightens** to guarantee optimal granularity.
 
This means a short video organically gets 2–3 subtopics, while a long video expands into 6–10 subtopics.
                """)
                
                # Display cluster scatter plot if available
                cluster_graph = os.path.join(OUTPUTS_DIR, "subtopic_clusters_graph.png")
                if os.path.exists(cluster_graph):
                    st.image(cluster_graph, caption="PCA 2D projection of transcript segments colored by subtopic cluster", use_container_width=True)
                
                # Stage 3
                st.markdown("""
##### 3️⃣ LLM Subtopic Summarization
For each cluster, all transcript segments are concatenated and sent to 
a **local LLM** (Gemma via TurboQuant server). The model generates:
- **Title** — a short descriptive name
- **Description** — 1-2 sentence overview
- **Summary** — detailed highlights of key points
 
Summaries are saved incrementally so the UI can display them in real-time 
during processing.
                """)
                
                # Stage 4
                st.markdown("""
##### 4️⃣ Final Overall Summary
All subtopic summaries are combined and passed to the LLM one more time 
to produce a **cohesive overall summary** of the entire video, capturing 
the narrative flow across all discovered subtopics.
                """)
                
                st.divider()
                
                # Show current stats
                st.markdown(f"""
**Current Video Stats:**
- 📊 **{len(transcripts)}** transcript segments embedded
- 🗂️ **{len(summaries)}** subtopics discovered
- 🔤 Embedding model: `all-MiniLM-L6-v2` (384-dim)
- 🤖 Summarization model: `Gemma` (local)
                """)

    with bottom_right:
        current_time = format_time(st.session_state.start_time)

        st.subheader(f"Video Playback (Synced at {current_time})")

        # Styled video container that matches the search panel's height
        video_container = st.container()
        with video_container:
            # Check if there is a locally processed video path
            local_video_path = None
            local_path_file = os.path.join(OUTPUTS_DIR, "local_video_path.txt")
            if os.path.exists(local_path_file):
                try:
                    with open(local_path_file, "r", encoding="utf-8") as f:
                        local_video_path = f.read().strip()
                except Exception:
                    pass

            # Choose what path to display
            play_path = st.session_state.video_path
            if is_youtube_url(play_path) and local_video_path and os.path.exists(local_video_path):
                play_path = local_video_path

            if os.path.exists(play_path):
                st.video(play_path, start_time=st.session_state.start_time)
                if play_path == local_video_path:
                    st.caption(f"▶ Playing local downloaded video from {current_time}")
                else:
                    st.caption(f"▶ Playing from {current_time}")
            elif is_youtube_url(play_path):
                st.video(play_path, start_time=st.session_state.start_time)
                st.caption("Searchable topic timeline is currently available for local videos.")
            else:
                st.warning(f"Video file not found at path: {play_path}")
        
        # ─── EXPORT STUDIO ───
        st.divider()
        # st.subheader("Export Studio")
        st.caption("Generate and download study documents, subtitles, and detailed reports based on the pipeline outputs.")
        
        # Force reload export_utils module to clear Streamlit's internal cache
        try:
            import importlib
            import src.utils.export_utils
            importlib.reload(src.utils.export_utils)
        except Exception:
            pass
            
        col_pdf, col_srt, col_md = st.columns(3)
        
        # Pre-load/read keyframes from frame_comparison_final.json
        kf_data = []
        kf_json_path = os.path.join(OUTPUTS_DIR, "frame_comparison_final.json")
        if os.path.exists(kf_json_path):
            try:
                with open(kf_json_path, 'r') as f:
                    kf_data = [m for m in json.load(f) if m.get('is_clear_keyframe', False)]
            except Exception:
                pass
                
        video_name = video_meta.get("name", "video")
        
        with col_pdf:
            # PDF Generation
            try:
                from src.utils.export_utils import export_to_pdf
                frames_dir = os.path.join(BASE_DIR, "data", "frames")
                pdf_data = export_to_pdf(overall_summary, summaries, kf_data, video_meta, frames_dir)
                st.markdown('<div class="download-btn-anchor"></div>', unsafe_allow_html=True)
                st.download_button(
                    label="📄 Download PDF Summary Report",
                    data=pdf_data,
                    file_name=f"{video_name}_summary_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
                
        with col_srt:
            # SRT Generation
            try:
                from src.utils.export_utils import export_to_srt
                srt_data = export_to_srt(transcripts)
                st.markdown('<div class="download-btn-anchor"></div>', unsafe_allow_html=True)
                st.download_button(
                    label="🎙️ Download Subtitles (.srt)",
                    data=srt_data,
                    file_name=f"{video_name}_subtitles.srt",
                    mime="text/plain",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate subtitles: {e}")
                
        with col_md:
            # Markdown Generation
            try:
                from src.utils.export_utils import export_to_markdown
                md_data = export_to_markdown(overall_summary, summaries, kf_data, video_name)
                st.markdown('<div class="download-btn-anchor"></div>', unsafe_allow_html=True)
                st.download_button(
                    label="📖 Download Study Guide (.md)",
                    data=md_data,
                    file_name=f"{video_name}_study_guide.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate study guide: {e}")
        
else:
    st.info("👈 Enter a valid video path and click 'Load Data / Process' to view the dashboard.")
