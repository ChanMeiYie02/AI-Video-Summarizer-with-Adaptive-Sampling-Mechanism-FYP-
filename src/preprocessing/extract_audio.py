import subprocess

def extract_audio_ffmpeg(video_path, output_file="data/audio/output.wav"):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-ac", "1",          # mono
        "-ar", "16000",     # 16kHz
        "-vn",              # no video
        output_file
    ]

    subprocess.run(command)
    print(f"✅ Audio saved as '{output_file}'")