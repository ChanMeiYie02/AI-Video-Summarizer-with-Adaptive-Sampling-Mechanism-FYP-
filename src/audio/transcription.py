import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig
import librosa
import soundfile as sf
import os
from tqdm import tqdm

def load_gemma4_audio_model():
    model_id = "google/gemma-4-E2B-it"
    print(f"Loading {model_id} for Audio (unquantized)...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    if device == "cuda":
        # torch.cuda.set_per_process_memory_fraction(1.00) 
        pass
    
    processor = AutoProcessor.from_pretrained(model_id)
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForMultimodalLM.from_pretrained(
        model_id, 
        device_map=device, 
        torch_dtype=dtype,
    )
    
    return processor, model, device

def chunk_audio(audio_path, chunk_length_sec, output_dir="data/audio/chunks/"):
    """
    Gemma 4 only supports up to 30 seconds of audio per prompt. 
    This slices the main audio into 29-second chunks.
    """
    import numpy as np
    print(f"Loading and chunking audio from {audio_path}...")
    audio, sr = librosa.load(audio_path, sr=16000)
    
    total_samples = len(audio)
    chunk_samples = int(chunk_length_sec * sr)
    
    os.makedirs(output_dir, exist_ok=True)
    chunk_paths = []
    
    for i, start in enumerate(range(0, total_samples, chunk_samples)):
        end = min(start + chunk_samples, total_samples)
        chunk_data = audio[start:end]
        
        # Pad tail chunk to ensure exactly chunk_samples length to avoid numpy 2.x pad broadcast bug in transformers
        if len(chunk_data) < chunk_samples:
            pad_len = chunk_samples - len(chunk_data)
            chunk_data = np.pad(chunk_data, (0, pad_len), mode='constant')
            
        chunk_path = os.path.join(output_dir, f"chunk_{i:03d}.wav")
        sf.write(chunk_path, chunk_data, sr)
        chunk_paths.append(chunk_path)
        
    print(f"Created {len(chunk_paths)} chunks (max {chunk_length_sec}s each).")
    return chunk_paths, sr

def transcribe_audio(chunk_length_sec, audio_file='data/audio/output.wav'):
    processor, model, device = load_gemma4_audio_model()
    
    # Chunk the audio to avoid the 30-second context limit
    chunk_paths, _ = chunk_audio(audio_file, chunk_length_sec=chunk_length_sec)
    
    full_transcript = []
    
    import time
    start_time = time.time()
    
    total_input_tokens = 0
    total_output_tokens = 0
    
    print("\nStarting transcription...")
    for i, chunk_path in enumerate(tqdm(chunk_paths, desc="Transcribing Chunks")):
        
        chunk_start_sec = i * chunk_length_sec
        chunk_end_sec = chunk_start_sec + chunk_length_sec
        
        # 03
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "audio", "audio": chunk_path},
                    {"type": "text", "text": "Transcribe the following speech segment in its original language. Follow these specific instructions for formatting the answer:\n* Only output the transcription, with no newlines.\n* When transcribing numbers, write the digits.\n*"}
                ]
            }
        ]

    # 04    
    #       messages = [
    #     {
    #         "role": "user",
    #         "content": [
    #             {"type": "audio", "audio": chunk_path},
    #             {"type": "text", "text": "Transcribe the following speech segment in its original language. Identify logical chapters and for each, provide a start timestamp, title, full transcription, and a brief content summary. Follow these formatting instructions:\n* Use digits for all numbers.\n* Organize the output by chapters using clear headings.\n* Do not add introductory or concluding explanations."}
    #         ]
    #     }
    # ]


        # 05
        # messages = [
        #     {
        #         "role": "user",
        #         "content": [
        #             {"type": "audio", "audio": chunk_path},
        #             {"type": "text", "text": "Transcribe the following speech segment in its original language. Identify logical chapters and for each, provide a title, full transcription, and a brief content summary. Follow these formatting instructions:\n* Use digits for all numbers.\n* Format the content summary into short, clear, and concise bullet points.\n* Organize the output by chapters using clear headings.\n* Do not add introductory or concluding explanations."}
        #         ]
        #     }
        # ]

        # messages = [
        #     {
        #         "role": "user",
        #         "content": [
        #             {"type": "audio", "audio": chunk_path},
        #             {
        #                 "type": "text",
        #                 "text": (
        #                     "Transcribe the following speech segment in its original language and organize it into clearly defined chapters.\n\n"

        #                     "STRICT OUTPUT FORMAT (follow exactly):\n\n"

        #                     "## Chapter X: [Chapter Title]\n"
        #                     "**Transcription:**\n"
        #                     "[Full transcription of this chapter in paragraph form]\n\n"
        #                     "**Summary:**\n"
        #                     "- [Key point 1]\n"
        #                     "- [Key point 2]\n"
        #                     "- [Key point 3]\n\n"

        #                     "RULES:\n"
        #                     "1. Use digits for all numbers (e.g., 1, 2, 3).\n"
        #                     "2. Identify logical chapter boundaries based on topic changes.\n"
        #                     "3. Each chapter MUST include: title, transcription, and summary.\n"
        #                     "4. Keep summaries concise (3–5 bullet points only).\n"
        #                     "5. Do NOT omit any spoken content in transcription.\n"
        #                     "6. Do NOT add any introduction or conclusion outside the chapter format.\n"
        #                     "7. Do NOT explain your process.\n"
        #                     "8. Maintain consistent formatting across all chapters.\n"
        #                 )
        #             }
        #         ]
        #     }
        # ]

        
        # Apply the chat template to build the prompt
        try:
            inputs = processor.apply_chat_template(
                messages,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
                add_generation_prompt=True,
            ).to(device)
            
            input_len = inputs["input_ids"].shape[-1]
            total_input_tokens += input_len

            with torch.inference_mode():
                outputs = model.generate(**inputs, max_new_tokens=512)
                
            # Slice off the prompt tokens to get only the new generation
            generated_tokens = outputs[0][input_len:]
            total_output_tokens += generated_tokens.shape[-1]
            
            response = processor.decode(generated_tokens, skip_special_tokens=True)
            
            full_transcript.append({
                "start_sec": chunk_start_sec,
                "end_sec": chunk_end_sec,
                "text": response.strip()
            })
            
            # Save output incrementally so that frontend UI can read in real-time
            os.makedirs("outputs", exist_ok=True)
            output_path = "outputs/transcript.json"
            with open(output_path, "w", encoding="utf-8") as f:
                import json
                json.dump(full_transcript, f, indent=4)
            
        except Exception as e:
            print(f"\nError processing chunk {chunk_path}: {e}")
            
    end_time = time.time()
    total_time = end_time - start_time
    # Each chunk is dynamically calculated based on the parameter
    total_audio_sec = len(chunk_paths) * chunk_length_sec
    time_per_audio_min = (total_time / total_audio_sec) * 60 if total_audio_sec > 0 else 0
            
    # Save the output as JSON instead of txt
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/transcript.json"
    with open(output_path, "w", encoding="utf-8") as f:
        import json
        json.dump(full_transcript, f, indent=4)
        
    print(f"\n✅ Transcription complete! Saved to {output_path}")
    print(f"⚡ Performance: Processed {total_audio_sec/60:.2f} mins of audio in {total_time:.2f} seconds.")
    print(f"⚡ Speed: {time_per_audio_min:.2f} seconds of processing per real minute of audio.")
    print(f"📊 Token Usage: {total_input_tokens} Input | {total_output_tokens} Output | {total_input_tokens + total_output_tokens} Total Tokens")
    print("\nSnippet (First Chunk):")
    if len(full_transcript) > 0:
        snippet_text = full_transcript[0]['text']
        print(snippet_text[:500] + "..." if len(snippet_text) > 500 else snippet_text)

if __name__ == "__main__":
    transcribe_audio(chunk_length_sec=29)
