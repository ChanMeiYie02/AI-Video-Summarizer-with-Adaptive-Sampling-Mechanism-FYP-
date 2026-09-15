import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig
from PIL import Image
import json
import os
from tqdm import tqdm

def load_gemma4_model():
    """
    Loads the newly released Gemma 4 E2B Multimodal model.
    """
    model_id = "google/gemma-4-E2B-it"
    
    print(f"Loading {model_id} (unquantized)...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    if device == "cuda":
        # Safe 50% allocation
        # torch.cuda.set_per_process_memory_fraction(0.50) 
        pass
    
    processor = AutoProcessor.from_pretrained(model_id)
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForMultimodalLM.from_pretrained(
        model_id, 
        device_map=device, 
        torch_dtype=dtype,
    )
    
    return processor, model, device

def transcribe_frames(fps, json_file='outputs/frame_comparison_final.json', frames_dir='data/frames/'):
    """
    Reads the keyframes JSON, and uses the model to transcribe ONLY the clear keyframes.
    This saves immense amounts of time compared to doing every single frame.
    """
    # Load model
    processor, model, device = load_gemma4_model()
    
    # Load keyframes tracking JSON
    with open(json_file, 'r') as f:
        metrics = json.load(f)
        
    # Get only the keyframes that were flagged as BOTH significant and NOT blurry
    keyframes = [m for m in metrics if m.get('is_clear_keyframe', False)]
    print(f"Found {len(keyframes)} clear keyframes for visual transcription.")
    
    # We will store our frame descriptions here
    frame_descriptions = []
    
    import time
    start_time = time.time()
    
    total_input_tokens = 0
    total_output_tokens = 0
    
    for kf in tqdm(keyframes, desc="Transcribing Vision"):
        # Use pre-calculated timestamp if available, fallback to filename parsing
        if kf.get('timestamp_sec') is None:
            try:
                # Assuming filename format is "frame_XXXX.jpg"
                frame_idx = int(kf['filename'].split('_')[1].split('.')[0])
                kf['timestamp_sec'] = (frame_idx - 1) / fps
            except Exception:
                kf['timestamp_sec'] = 0.0

        image_path = os.path.join(frames_dir, kf['filename'])
        image = Image.open(image_path).convert("RGB")
        
        # Following Gemma 4 E2B Chat Template format for images:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": "Identify if the image is primarily a document or a scene. If it contains significant text, transcribe it exactly. If it is a scene with little to no text, describe the setting and action in 2 detailed sentences."}
                ]
            }
        ]
        
        # Apply the chat template to build the exact sequence of <image> tokens the model expects
        prompt_text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Prepare inputs combining text and the PIL image
        model_inputs = processor(
            text=prompt_text, 
            images=image, 
            return_tensors="pt"
        ).to(device)
        
        input_len = model_inputs["input_ids"].shape[-1]
        total_input_tokens += input_len

        # Generate output text
        with torch.inference_mode():
            generation = model.generate(
                **model_inputs, 
                max_new_tokens=150, 
                do_sample=False
            )
            
            # Slice output to only have the generated tokens
            generated_tokens = generation[0][input_len:]
            total_output_tokens += generated_tokens.shape[-1]
            
            decoded_text = processor.decode(generated_tokens, skip_special_tokens=True)
            
        kf['visual_description'] = decoded_text
        frame_descriptions.append(kf)
        
        # Save output incrementally so that frontend UI can read in real-time
        os.makedirs('outputs', exist_ok=True)
        output_path = 'outputs/transcribed_keyframes.json'
        with open(output_path, 'w') as f:
            json.dump(frame_descriptions, f, indent=4)

    end_time = time.time()
    total_time = end_time - start_time
    time_per_frame = total_time / len(keyframes) if len(keyframes) > 0 else 0

    # Save to a new JSON document
    output_path = 'outputs/transcribed_keyframes.json'
    with open(output_path, 'w') as f:
        json.dump(frame_descriptions, f, indent=4)
        
    print(f"\n✅ All frame descriptions saved to {output_path}")
    print(f"⚡ Performance: Processed {len(keyframes)} frames in {total_time:.2f} seconds.")
    print(f"⚡ Speed: {time_per_frame:.2f} seconds per frame.")
    print(f"📊 Token Usage: {total_input_tokens} Input | {total_output_tokens} Output | {total_input_tokens + total_output_tokens} Total Tokens")

if __name__ == "__main__":
    transcribe_frames(fps=4.0)
