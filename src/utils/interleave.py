import json
import re
import os

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_interleaved_timeline(transcript_path, keyframes_path, output_path):
    print("Loading data...")
    transcript = load_json(transcript_path)
    keyframes = load_json(keyframes_path)
    
    events = []
    
    # 1. Process Keyframes
    for frame in keyframes:
        if frame.get("is_clear_keyframe"):
            events.append({
                "time": float(frame["timestamp_sec"]),
                "type": "FRAME",
                "content": frame.get("visual_description", "").replace('\n', ' '),
                "filename": frame.get("filename")
            })
            
    # 2. Process Audio Transcript using "Rough Estimate" Math Division
    for chunk in transcript:
        start_sec = float(chunk["start_sec"])
        end_sec = float(chunk["end_sec"])
        duration = end_sec - start_sec
        text = chunk.get("text", "")
        
        if not text.strip():
            continue
            
        # Split chunk text into rough sentences using punctuation
        # This keeps the punctuation attached to the sentence
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        
        # If no punctuation, fallback to treating the whole chunk as 1 block, or split by comma
        if not sentences:
            sentences = [text.strip()]
            
        num_sentences = len(sentences)
        
        if num_sentences > 0:
            time_per_sentence = duration / num_sentences
            
            for i, sentence in enumerate(sentences):
                # Calculate estimated time for this sentence linearly
                sentence_start = start_sec + (i * time_per_sentence)
                events.append({
                    "time": sentence_start,
                    "type": "AUDIO",
                    "content": sentence
                })
                
    # 3. Sort all events chronologically by time
    events.sort(key=lambda x: x["time"])
    
    # 4. Save to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Text-friendly output format
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=== MULTIMODAL INTERLEAVED TIMELINE ===\n")
        f.write("Generated using rough sentence estimation from 29s chunks.\n\n")
        
        for event in events:
            time_formatted = f"[{event['time']:.2f}s]"
            if event["type"] == "FRAME":
                f.write(f"\n{time_formatted} 🖼️ [FRAME - {event['filename']}]\n")
                f.write(f"Description: {event['content']}\n\n")
            elif event["type"] == "AUDIO":
                f.write(f"{time_formatted} 🔊 [AUDIO]: {event['content']}\n")
                
    # Also save as strict JSON for downstream app usage
    json_path = output_path.replace('.txt', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=4)
        
    print(f"Interleaved timeline saved to: {output_path}")
    print(f"JSON version saved to: {json_path}")
    print(f"Total Events Combined: {len(events)}")


if __name__ == "__main__":
    b_transcript = "outputs/transcript.json"
    b_keyframes = "outputs/transcribed_keyframes.json"
    out_timeline = "outputs/interleaved_timeline.txt"
    
    if os.path.exists(b_transcript) and os.path.exists(b_keyframes):
        build_interleaved_timeline(b_transcript, b_keyframes, out_timeline)
    else:
        print(f"Error: Missing input files in outputs/ directory.")
