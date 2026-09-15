import json
import os
import time

# To use llama2 locally, typically LangChain with Ollama is the fastest/easiest way.
# Ensure you have ollama installed and have run `ollama run llama2` in your terminal.
# pip install langchain langchain-community
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
except ImportError:
    print("Warning: Please install Langchain OpenAI integrations: pip install langchain-openai")
    exit()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLUSTERED_OUTPUT_PATH = os.path.join(BASE_DIR, "outputs", "clustered_subtopics.json")
FINAL_SUMMARIES_PATH = os.path.join(BASE_DIR, "outputs", "final_topic_summaries.json")

def summarize_clusters():
    print("1. Loading Clustered Subtopics...")
    if not os.path.exists(CLUSTERED_OUTPUT_PATH):
        print("Error: Run 02_cluster_subtopics.py first.")
        return

    with open(CLUSTERED_OUTPUT_PATH, 'r', encoding='utf-8') as f:
        subtopics = json.load(f)

    print(f"Loaded {len(subtopics)} subtopics to summarize.")

    # 2. Setup the LLM Model (Gemma via TurboQuant Server)
    print("\n2. Initializing Connection to Local TurboQuant server...")
    llm = ChatOpenAI(
        model="gemma-4-E2B", # Or whatever model string you boot the server with
        api_key="sk-no-key-needed", 
        base_url="http://localhost:8080/v1",
        max_tokens=1024,
        model_kwargs={
            "stop": ["<unused49>", "<end_of_turn>", "<eos>"]
        }
    )

    prompt_template = PromptTemplate(
        input_variables=["context"],
        template=(
            "<start_of_turn>user\n"
            "You are an expert summarizer. I will provide you with transcripts from a specific section of a video.\n\n"
            "CONTEXT:\n{context}\n\n"
            "Please analyze the context and provide three things:\n"
            "1. A short, descriptive TITLE for this topic.\n"
            "2. A very brief DESCRIPTION (1-2 sentences) summarizing what it is about.\n"
            "3. A detailed SUMMARY highlighting the main points discussed.\n\n"
            "Format your output EXACTLY like this:\n"
            "TITLE: [Your Title Here]\n"
            "DESCRIPTION: [Your Description Here]\n"
            "SUMMARY: [Your Summary Here]<end_of_turn>\n"
            "<start_of_turn>model\n"
        )
    )

    # 3. Summarize Each Subtopic
    print("\n3. Generating Subtopic Summaries...")
    final_summaries = []

    for subtopic in subtopics:
        subtopic_id = subtopic["subtopic_id"]
        context = subtopic["combined_context"]
        count = subtopic["chunk_count"]
        
        print(f"\n--- Summarizing Subtopic {subtopic_id} (Based on {count} text chunks) ---")
        
        start_time = time.time()
        
        # Format the prompt and call the local model
        formatted_prompt = prompt_template.format(context=context)
        raw_output = llm.invoke(formatted_prompt)
        
        # Extract content from AIMessage
        if hasattr(raw_output, 'content'):
            raw_output = raw_output.content
            
        # Coerce output to string safely if it is a list or other object type
        if isinstance(raw_output, list):
            # Join text values if it is a list of multimodal elements or strings
            text_parts = []
            for item in raw_output:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
                else:
                    text_parts.append(str(item))
            raw_output = "".join(text_parts)
        elif not isinstance(raw_output, str):
            raw_output = str(raw_output)
            
        end_time = time.time()
        
        # Parse the structured response
        title = "Untitled Subtopic"
        description = "No description provided."
        summary_text = raw_output.strip()
        
        # Simple extraction logic based on our requested format
        try:
            if "TITLE:" in raw_output and "DESCRIPTION:" in raw_output and "SUMMARY:" in raw_output:
                parts = raw_output.split("TITLE:")[-1].split("DESCRIPTION:")
                title = parts[0].strip()
                desc_and_sum = parts[1].split("SUMMARY:")
                description = desc_and_sum[0].strip()
                summary_text = desc_and_sum[1].strip()
        except Exception:
            pass # Fallback to raw output if the local LLM ignores formatting
            
        print(f"Generated in {end_time - start_time:.2f} seconds.")
        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Summary length: {len(summary_text)} chars")
        
        final_summaries.append({
            "subtopic_id": subtopic_id,
            "title": title,
            "description": description,
            "summary": summary_text,
            "raw_output": raw_output.strip()  # Kept for debugging in case parsing fails
        })
        
        # Save output incrementally so that frontend UI can read in real-time
        os.makedirs(os.path.dirname(FINAL_SUMMARIES_PATH), exist_ok=True)
        with open(FINAL_SUMMARIES_PATH, "w", encoding="utf-8") as f:
            json.dump(final_summaries, f, indent=4)

    # Save final results
    with open(FINAL_SUMMARIES_PATH, "w", encoding="utf-8") as f:
        json.dump(final_summaries, f, indent=4)
        
    print(f"\nAll subtopic summaries saved to {FINAL_SUMMARIES_PATH}!")

if __name__ == "__main__":
    summarize_clusters()
