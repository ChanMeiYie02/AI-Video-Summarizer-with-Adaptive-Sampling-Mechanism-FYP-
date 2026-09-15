import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig
from PIL import Image
from typing import Any
import librosa
import soundfile as sf
import json
import os
import time
from tqdm import tqdm


def load_gemma4_model():

    model_id = "google/gemma-4-E2B-it"
    print(f"Loading {model_id} for Native Interleaved Execution (unquantized)...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    if device == "cuda":
        # Safe 95% allocation since we run standalone
        # torch.cuda.set_per_process_memory_fraction(0.95) 
        pass
        
    processor = AutoProcessor.from_pretrained(model_id)
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    try:
        model = AutoModelForMultimodalLM.from_pretrained(
            model_id, 
            device_map=device, 
            torch_dtype=dtype,
            attn_implementation="flash_attention_2"
        )
    except Exception:
        print("[Multimodal Processor] Flash Attention 2 not available. Falling back to SDPA.")
        model = AutoModelForMultimodalLM.from_pretrained(
            model_id, 
            device_map=device, 
            torch_dtype=dtype,
            attn_implementation="sdpa"
        )
    return processor, model, device

def test_interleaved_processor(fps=4.0, batch_size=32):
    print("\n==============================================")
    print("🚀 NATIVE MULTIMODAL INTERLEAVED PROCESSOR")
    print("==============================================\n")
    
    frames_dir = 'data/frames/'
    audio_path = 'data/audio/output.wav'
    json_file = 'outputs/frame_comparison_final.json'
    
    if not os.path.exists(json_file) or not os.path.exists(audio_path):
        print(f"CRITICAL ERROR: Make sure {json_file} and {audio_path} exist first!")
        return

    # Load resources
    processor, model, device = load_gemma4_model()
    
    # Configure padding side to left for batched generation
    processor.tokenizer.padding_side = "left"
    if processor.tokenizer.pad_token is None:
        processor.tokenizer.pad_token = processor.tokenizer.eos_token
    
    import glob
    
    # Reload Keyframes from JSON
    with open(json_file, 'r') as f:
        metrics = json.load(f)
    keyframes = [m for m in metrics if m.get('is_clear_keyframe', False)]
    print(f"\nLoaded {len(keyframes)} critical keyframes from tracker.")

    # 1. We will natively scan for pre-existing audio chunks
    audio_chunks_dir = 'data/audio/chunks/'
    available_chunks = sorted(glob.glob(os.path.join(audio_chunks_dir, "chunk_*.wav")))
    
    if len(available_chunks) == 0:
        print(f"CRITICAL ERROR: Make sure audio chunks exist in {audio_chunks_dir}!")
        return

    print(f"\nFound {len(available_chunks)} pre-sliced audio chunks. Beginning timeline sweep...\n")
    
    chunk_length_sec = 29.0
    total_chunks = len(available_chunks)
    
    results: list[Any] = [None] * total_chunks
    active_payloads = []  # List of tuples: (chunk_idx, messages, images, block_frames, start_sec, end_sec)
    
    # Step 1: Pre-scan chunks for silence-skipping or active processing
    for chunk_idx, temp_audio_path in enumerate(available_chunks):
        start_sec = chunk_idx * chunk_length_sec
        end_sec = start_sec + chunk_length_sec
        
        # Filter frames that fit precisely in this 29-second chunk
        block_frames = []
        for kf in keyframes:
            timestamp_sec = kf.get('timestamp_sec')
            if timestamp_sec is None:
                try:
                    frame_idx = int(kf['filename'].split('_')[1].split('.')[0])
                    timestamp_sec = (frame_idx - 1) / fps
                except Exception:
                    timestamp_sec = 0.0
            
            if start_sec <= timestamp_sec < end_sec:
                kf['timestamp_sec'] = timestamp_sec
                block_frames.append(kf)
                
        # SAFEGUARD: Keep only the Top 3 most visually different frames to prevent VRAM explosion
        if len(block_frames) > 3:
            block_frames = sorted(block_frames, key=lambda x: x.get('change_score', 0.0), reverse=True)[:3]
            block_frames = sorted(block_frames, key=lambda x: x['timestamp_sec'])
            
        # Silence Detection Check
        import numpy as np
        try:
            y, sr = sf.read(temp_audio_path)
            rms = np.sqrt(np.mean(y**2)) if len(y) > 0 else 0.0
        except Exception as e:
            print(f"Error reading audio chunk: {e}")
            rms = 1.0  # Default to not silent on error
            
        is_silent = rms < 0.005
        
        if len(block_frames) == 0 and is_silent:
            print(f"🤫 [SKIPPED] Chunk {start_sec}s - {end_sec:.1f}s is silent (RMS: {rms:.5f}) with no keyframes. Skipping LLM call.")
            results[chunk_idx] = {
                "chunk_id": chunk_idx,
                "start_sec": start_sec,
                "end_sec": end_sec,
                "included_frames": [],
                "analysis": ""
            }
            # Save output incrementally so that frontend UI can read in real-time
            os.makedirs('outputs', exist_ok=True)
            out_path = 'outputs/interleaved_results.json'
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump([r for r in results if r is not None], f, indent=4)
        else:
            # Construct Multimodal Payload
            content = []
            images = []
            for kf in block_frames:
                image_path = os.path.join(frames_dir, kf['filename'])
                image = Image.open(image_path).convert("RGB")
                content.append({"type": "image", "image": image})
                images.append(image)
                
            content.append({"type": "audio", "audio": temp_audio_path})
            
            if len(block_frames) == 0:
                text_prompt = "Transcribe the following speech segment in its original language. Follow these specific instructions for formatting the answer:\n* Only output the transcription, with no newlines.\n* When transcribing numbers, write the digits.\n*"
            else:
                text_prompt = f"Analyze this chronological sequence of {len(block_frames)} video frames and the accompanying 29 seconds of audio. Provide a consolidated summary synthesizing exactly what physically happens on screen alongside what is being discussed verbally."
                
            content.append({"type": "text", "text": text_prompt})
            messages = [{"role": "user", "content": content}]
            
            active_payloads.append((chunk_idx, messages, images, block_frames, start_sec, end_sec))

    # Step 2: Process active chunks in mini-batches of size 2
    BATCH_SIZE = batch_size
    total_active = len(active_payloads)
    print(f"\n🚀 Ready to process {total_active} active chunks in mini-batches of size {BATCH_SIZE}...")
    
    total_start_time = time.time()
    
    for batch_start_idx in range(0, total_active, BATCH_SIZE):
        batch = active_payloads[batch_start_idx : batch_start_idx + BATCH_SIZE]
        batch_messages = [item[1] for item in batch]
        
        print(f"\n[Batch] Processing {len(batch)} chunks: {[item[0]+1 for item in batch]}...")
        batch_start_time = time.time()
        
        # Apply the chat template to the batch of inputs
        model_inputs = processor.apply_chat_template(
            batch_messages,
            tokenize=True,
            return_dict=True,
            padding=True,
            return_tensors="pt",
            add_generation_prompt=True,
        ).to(device)
        
        with torch.inference_mode():
            generations = model.generate(**model_inputs, max_new_tokens=500, do_sample=False)
            
        batch_dur = time.time() - batch_start_time
        print(f"⏱️ Batch Process Time: {batch_dur:.2f} seconds ({batch_dur/len(batch):.2f}s per chunk)")
        
        # Decode and map back to individual chunks
        for batch_i, (chunk_idx, _, images, block_frames, start_sec, end_sec) in enumerate(batch):
            input_len = model_inputs["input_ids"].shape[-1]
            generated_tokens = generations[batch_i][input_len:]
            decoded_text = processor.decode(generated_tokens, skip_special_tokens=True)
            
            print(f"🧠 Chunk {chunk_idx+1} Analysis: {decoded_text.strip()}")
            
            results[chunk_idx] = {
                "chunk_id": chunk_idx,
                "start_sec": start_sec,
                "end_sec": end_sec,
                "included_frames": [kf['filename'] for kf in block_frames],
                "analysis": decoded_text.strip()
            }
            
            # Close PIL Image handles
            for img in images:
                img.close()
                
        # Save output incrementally so that frontend UI can read in real-time
        os.makedirs('outputs', exist_ok=True)
        out_path = 'outputs/interleaved_results.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump([r for r in results if r is not None], f, indent=4)
            
        # Clean VRAM cache
        del model_inputs
        del generations
        torch.cuda.empty_cache()

    total_duration = time.time() - total_start_time
    average_duration = total_duration / total_chunks if total_chunks > 0 else 0
    
    print("==============================================")
    print("🏁 CHUNK-CENTRIC EXECUTION COMPLETE")
    print(f"Total Processing Time: {total_duration:.2f} seconds")
    print(f"Average Time per 29s Block: {average_duration:.2f} seconds")
    print("==============================================\n")
    
    # Save the final output
    os.makedirs('outputs', exist_ok=True)
    out_path = 'outputs/interleaved_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump([r for r in results if r is not None], f, indent=4)
        
    print(f"✅ Chunked timeline natively saved to: {out_path}")

if __name__ == "__main__":
    test_interleaved_processor(fps=4.0)
