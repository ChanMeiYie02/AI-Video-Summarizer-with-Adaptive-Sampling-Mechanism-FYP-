import ffmpeg
import os

def extract_frames_ffmpeg(video_path, fps, output_folder="data/frames"):
    os.makedirs(output_folder, exist_ok=True)

    output_pattern = os.path.join(output_folder, "frame_%04d.jpg")

    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_pattern, vf=f'fps={fps}')
            .run(quiet=True)
        )
        print(f"✅ Frames saved in '{output_folder}'")
    except ffmpeg.Error as e:
        print(f"❌ Error running ffmpeg: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

