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

# Ensure project root and src directories are in the search path for module resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from preprocessing.extract_frames import extract_frames_ffmpeg
from preprocessing.extract_audio import extract_audio_ffmpeg
from preprocessing.frame_filter import compute_frame_differences
from vision.frame_captioning import transcribe_frames
from audio.transcription import transcribe_audio
from utils.interleave import build_interleaved_timeline
from utils.embed_and_search import embed_and_search
from utils.cluster_subtopics import cluster_subtopics
from utils.summarize_clusters import summarize_clusters
from summarization.summarize import summarize_video
import concurrent.futures
from multimodal.multimodal_processor import test_interleaved_processor
import argparse
import shutil
import time
import subprocess
import re


def safe_rmtree(path):
    if not os.path.exists(path):
        return
    try:
        shutil.rmtree(path)
    except PermissionError:
        print(f"[WARNING] Directory '{path}' is locked by another process (e.g., Streamlit). Cleaning up unlocked files...")
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.rmdir(dir_path)
                except Exception:
                    pass


def run_pipeline(video_path, threshold=0.3, similarity_threshold=0.30, use_multimodal=True, batch_size=32):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(project_root)
    video_path = resolve_video_input(video_path)
    
    # Save the local video path reference for the Streamlit UI
    try:
        local_path_file = os.path.join("outputs", "local_video_path.txt")
        os.makedirs(os.path.dirname(local_path_file), exist_ok=True)
        with open(local_path_file, "w", encoding="utf-8") as f:
            f.write(video_path)
        print(f"[INFO] Saved local video path reference to: {local_path_file}")
    except Exception as e:
        print(f"[WARNING] Failed to save local video path reference: {e}")
    
    # ---------------------------------------------------------
    # GLOBAL TIMELINE SETTINGS
    # Modify these to control the granularity of your timeline!
    # ---------------------------------------------------------
    GLOBAL_FPS = 4.0               # How many frames per second to extract and align
    GLOBAL_AUDIO_CHUNK_SEC = 29    # How many seconds each audio slice should be
    
    # Toggle between native interleaved execution and parallel execution
    USE_MULTIMODAL_PROCESSOR = use_multimodal
    
    print("\n--- OVERHAUL: PURGING OLD CACHE FILES ---")
    # Guaranteed fresh slate for the new video
    for folder in ["data/frames", "data/audio", "outputs"]:
        if os.path.exists(folder):
            safe_rmtree(folder)
        os.makedirs(folder, exist_ok=True)


    b_transcript = "outputs/transcript.json"
    b_keyframes = "outputs/transcribed_keyframes.json"
    out_timeline = "outputs/interleaved_timeline.txt"
    report_path = "outputs/execution_times.txt"
    
    run_times = {}

    def track_time(task_name, func, *args, **kwargs):
        print(f"\n[STARTED] {task_name}...")
        start_t = time.time()
        func(*args, **kwargs)
        end_t = time.time()
        duration = end_t - start_t
        run_times[task_name] = duration
        print(f"[FINISHED] {task_name} in {duration:.4f} seconds.")

    # Preprocessing steps (1 & 2 run in parallel to save time)
    print("\n[STARTED] 1. Extract Frames & Audio...")
    start_parallel = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_frames = executor.submit(extract_frames_ffmpeg, video_path, fps=GLOBAL_FPS)
        future_audio = executor.submit(extract_audio_ffmpeg, video_path)
        
        # Wait for both tasks to complete
        concurrent.futures.wait([future_frames, future_audio])
        
        # Re-raise any exceptions that occurred during execution
        future_frames.result()
        future_audio.result()
        
    duration_parallel = time.time() - start_parallel
    run_times["1. Extract Frames & Audio"] = duration_parallel
    print(f"[FINISHED] 1. Extract Frames & Audio in {duration_parallel:.4f} seconds.")

    track_time("3. Compute Frame Diffs", compute_frame_differences, video_path, fps=GLOBAL_FPS, threshold=threshold, similarity_threshold=similarity_threshold) 
    
    if USE_MULTIMODAL_PROCESSOR:
        from audio.transcription import chunk_audio
        track_time("3.5. Chunk Audio", chunk_audio, "data/audio/output.wav", chunk_length_sec=GLOBAL_AUDIO_CHUNK_SEC)
        
        track_time("4 & 5. Native Multimodal Processing", test_interleaved_processor, fps=GLOBAL_FPS, batch_size=batch_size)
        
        def adapt_multimodal_output():
            import json
            import os
            
            with open('outputs/interleaved_results.json', 'r', encoding='utf-8') as f:
                multimodal_data = json.load(f)
                
            # Create a compatible transcript.json for embedding and clustering
            compatible_transcript = []
            with open(out_timeline, 'w', encoding='utf-8') as txt_out:
                for chunk in multimodal_data:
                    # Rename 'analysis' to 'text' for downstream compatibility
                    compatible_transcript.append({
                        "text": chunk.get("analysis", ""),
                        "start": chunk.get("start_sec", 0.0),
                        "end": chunk.get("end_sec", 0.0)
                    })
                    
                    # Create the text timeline file
                    txt_out.write(f"[{chunk.get('start_sec', 0.0):.1f}s - {chunk.get('end_sec', 0.0):.1f}s]\n")
                    txt_out.write(f"{chunk.get('analysis', '')}\n\n")
                    
            with open(b_transcript, 'w', encoding='utf-8') as f:
                json.dump(compatible_transcript, f, indent=4)
                
        track_time("6. Adapt Multimodal Output", adapt_multimodal_output)
        
    else:
        # -----------------------------------------------------
        # PARALLEL VLM and ASR execution using ProcessPool
        # -----------------------------------------------------
        # By using separate OS processes, we guarantee Python instantly 
        # reclaims their GPU memory completely when they finish, 
        # leaving a perfectly clean slate for the VLLM summarizers.
        
        print("\n[STARTED] 4 & 5. Parallel VLM & ASR Transcriptions...")
        start_para = time.time()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            f_vis = executor.submit(transcribe_frames, fps=GLOBAL_FPS)
            f_aud = executor.submit(transcribe_audio, chunk_length_sec=GLOBAL_AUDIO_CHUNK_SEC)
            
            # Wait for both huge tasks to complete perfectly in parallel
            concurrent.futures.wait([f_vis, f_aud])
            
            # Expose any hidden crashes from the parallel pipeline
            try:
                f_vis.result()
                f_aud.result()
            except Exception as e:
                print(f"\nCRITICAL ERROR IN PARALLEL PROCESS: {e}")
                raise
            
        duration_para = time.time() - start_para
        run_times["4 & 5. Parallel VLM & ASR"] = duration_para
        print(f"[FINISHED] 4 & 5. Parallel VLM/ASR in {duration_para:.2f} seconds.")

        track_time("6. Build Timeline", build_interleaved_timeline, b_transcript, b_keyframes, out_timeline)

    # RAG, Clustering, and Summarization
    track_time("7. Embed and Search", embed_and_search)
    track_time("8. Cluster Subtopics", cluster_subtopics)
    track_time("9. Summarize Clusters", summarize_clusters)
    
    # Final Summarization
    track_time("10. Final Video Summary", summarize_video, input_path=out_timeline)
    
    # Write the report
    total_time = sum(run_times.values())
    print("\n==================================")
    print("PIPELINE EXECUTION TIME REPORT")
    print("==================================")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("PIPELINE EXECUTION TIME REPORT\n")
        f.write("==================================\n\n")
        for task, duration in run_times.items():
            line = f"{task}: {duration:.2f} seconds\n"
            print(line, end="")
            f.write(line)
        f.write("\n==================================\n")
        f.write(f"TOTAL TIME: {total_time:.2f} seconds\n")
        print(f"TOTAL TIME: {total_time:.2f} seconds")
    
    print(f"\nDetailed timing report saved to: {report_path}")


def is_youtube_url(path_or_url):
    return bool(re.match(r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$", str(path_or_url).strip()))


def download_youtube_video(url, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Delete existing target file to prevent yt-dlp from skipping the download
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            print(f"[INFO] Cleared previous YouTube download at: {output_path}")
        except Exception as e:
            print(f"[WARNING] Failed to clear old YouTube download: {e}")

    candidate_cmds = [
        ["yt-dlp", "-f", "mp4/best", "--extractor-args", "youtube:player_client=ios,android", "-o", output_path, url],
        [sys.executable, "-m", "yt_dlp", "-f", "mp4/best", "--extractor-args", "youtube:player_client=ios,android", "-o", output_path, url],
    ]

    last_error = ""
    for cmd in candidate_cmds:
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            # Command executable not found, try next candidate.
            continue

        if process.returncode == 0 and os.path.exists(output_path):
            return output_path

        last_error = process.stderr.strip() or process.stdout.strip() or "Unknown yt-dlp error."

    raise RuntimeError(
        "Failed to download YouTube video. Neither 'yt-dlp' nor 'python -m yt_dlp' worked.\n"
        "Install yt-dlp in the same environment that runs main.py, then retry.\n"
        f"Last error: {last_error}"
    )


def resolve_video_input(video_path):
    if is_youtube_url(video_path):
        import datetime
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean URL string to extract last 5 characters (excluding special symbols)
        url_str = str(video_path).strip()
        clean_url = "".join(c for c in url_str if c.isalnum() or c in ['-', '_'])
        suffix = clean_url[-5:] if len(clean_url) >= 5 else clean_url
        
        filename = f"{now_str}_{suffix}.mp4"
        target = os.path.abspath(os.path.join("data", "raw_videos", filename))
        print(f"\n[INFO] YouTube URL detected. Downloading to: {target}")
        return download_youtube_video(video_path, target)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video path does not exist: {video_path}")
    return video_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run video summarization pipeline.")
    parser.add_argument(
        "--video_path",
        required=True,
        help="Absolute path to the video file to process.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.3,
        help="Scene boundary detection threshold.",
    )
    parser.add_argument(
        "--similarity_threshold",
        type=float,
        default=0.30,
        help="Frame clustering similarity threshold.",
    )
    parser.add_argument(
        "--use_multimodal",
        type=str,
        choices=["True", "False"],
        default="True",
        help="Whether to use native multimodal processing.",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=2,
        help="Batch size for native multimodal processor.",
    )
    args = parser.parse_args()
    
    use_multi_bool = args.use_multimodal == "True"
    run_pipeline(
        args.video_path,
        threshold=args.threshold,
        similarity_threshold=args.similarity_threshold,
        use_multimodal=use_multi_bool,
        batch_size=args.batch_size
    )
