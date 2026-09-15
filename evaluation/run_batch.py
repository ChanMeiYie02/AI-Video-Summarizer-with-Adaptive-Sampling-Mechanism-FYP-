import subprocess
import sys
import os

# List of videos to run: (video_name, video_link)
VIDEOS = [
    (
        "I Built the Most Powerful Cyberdeck in the World",
        "https://youtu.be/mwdgtGI5G84?si=cwGFqZIMLx1GOEsM"
    ),
    (
        "Lecture 11.1 - Reasoning in Knowledge Graphs",
        "https://youtu.be/X9yl0pTP9fY?si=Usz0SZbLErmDi_S_"
    ),
    (
        "AI and human evolution",
        "https://youtu.be/jt3Ul3rPXaE?si=I_72ly2xroly8xlX"
    ),
    (
        "The 50 Easiest 3-Ingredient Recipes",
        "https://youtu.be/WcGYBX6Ucvg?si=jfYFpGtPrnkb2dXV"
    ),
    (
        "Lecture 10.3 - Knowledge Graph Completion Algorithms",
        "https://youtu.be/Xm5VrxZYhu4?si=JNSIbmuamUEfwTzB"
    ),
    (
        "AMD Advancing AI 2026: Lisa Su Full Keynote",
        "https://www.youtube.com/live/jvtPC28nGsc?si=wH3lNI1VQUP26pk_"
    )
]

def run_batch():
    python_exe = sys.executable
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(base_dir, "evaluation", "run_experiment.py")

    total_videos = len(VIDEOS)
    print("\n====================================================")
    print(f"📦 Starting Batch Execution of {total_videos} Videos Sequentially")
    print("====================================================")

    for i, (name, link) in enumerate(VIDEOS):
        print(f"\n🎬 [Video {i+1}/{total_videos}] Starting: '{name}'")
        print(f"🔗 Link: {link}")
        print("----------------------------------------------------")

        cmd = [
            python_exe,
            script_path,
            "--video_link", link,
            "--video_name", name
        ]

        # Execute the run_experiment script; outputs stream directly to sys.stdout/stderr in real-time
        process = subprocess.run(cmd, cwd=base_dir)
        
        if process.returncode == 0:
            print(f"✅ [Video {i+1}/{total_videos}] Completed successfully: '{name}'")
        else:
            print(f"❌ [Video {i+1}/{total_videos}] Failed with exit code {process.returncode}: '{name}'")

    print("\n====================================================")
    print("🎉 All batch experiments completed!")
    print("====================================================\n")

if __name__ == "__main__":
    run_batch()
