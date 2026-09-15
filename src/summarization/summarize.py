import os
from langchain_community.document_loaders import TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate

# Setup for Background Server Integration
from langchain_openai import ChatOpenAI


def load_summary_model():
    """
    Connects to the Background TurboQuant Server Engine.
    """
    print("\nConnecting to High-Speed TurboQuant Backend Server...")
    
    try:
        llm = ChatOpenAI(
            model="gemma", # Generic string, the server ignores this locally.
            api_key="sk-no-key-needed", 
            base_url="http://localhost:8080/v1", # The default llama.cpp server route
            max_tokens=1500,
            model_kwargs={
                "stop": ["<unused49>", "<end_of_turn>", "<eos>"]
            }
        )
        return llm
    except Exception as e:
        print(f"Failed to connect to TurboQuant Engine: {e}")
        print("Please ensure your llama-server is running in the background!")
        return None

def summarize_video(input_path="outputs/interleaved_timeline_01.txt", output_path="outputs/final_summary.md"):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run interleave script first.")
        return

    print("1. Loading interleaved timeline...")
    loader = TextLoader(input_path, encoding='utf-8')
    docs = loader.load()

    print("2. Generating Semantic Chunks (Topic boundaries)...")
    # Using a fast, standard embedding model for semantic splitting
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'batch_size': 32}
    )
    
    text_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile" # Splits when similarity drops significantly
    )
    
    # Split the long timeline into perfectly grouped scene chunks!
    raw_semantic_chunks = text_splitter.split_documents(docs)
    
    # Inject metadata so sub-chunks keep their Chapter ID!
    for i, chunk in enumerate(raw_semantic_chunks):
        chunk.metadata["chapter_id"] = i + 1
        
    print(f"   -> Sliced video timeline into {len(raw_semantic_chunks)} specific semantic chapters.")

    # 2b. Safety Net Text Splitter
    # Ensures no single chapter exceeds a safe context limit (4000 chars)
    safety_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    final_safe_chunks = safety_splitter.split_documents(raw_semantic_chunks)
    
    print(f"   -> Safety Net applied: Resulted in {len(final_safe_chunks)} total processable blocks.")

    print("3. Loading LLM Map-Reduce Chain...")
    llm = load_summary_model()
    
    if not llm:
        print("Aborting summarization due to LLM load failure.")
        return

    # Define prompts for Map (summarizing a single chunk) and Reduce (combining summaries)
    map_prompt_template = """<start_of_turn>user
You are an expert multimodal video understanding system.

The following input contains:
1. Spoken dialogue text
2. Visual scene descriptions
arranged chronologically from a video segment.

Your task:
- Identify the main events and topics
- Capture important visual actions and scene changes
- Preserve temporal order
- Remove redundant details
- Produce a concise abstractive summary
- Avoid hallucinating information
- Focus only on important content

Raw Video Chunk:
{text}<end_of_turn>
<start_of_turn>model
Chunk Summary:"""
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])

    reduce_prompt_template = """<start_of_turn>user
You are an expert multimodal video summarization system.

Your task is to generate a coherent abstractive summary of the entire video using the provided chapter summaries.

Requirements:
- Preserve the chronological flow of events
- Combine related events into concise high-level descriptions
- Include both important spoken content and key visual actions
- Avoid repetition between chapters
- Focus only on the most important information
- Maintain factual consistency with the source summaries
- Produce a readable narrative paragraph structure
- Do NOT mention chapter numbers
- Do NOT invent information not present in the summaries

Chapter Summaries:
{text}<end_of_turn>
<start_of_turn>model
Final Comprehensive Video Summary:"""
    reduce_prompt = PromptTemplate(template=reduce_prompt_template, input_variables=["text"])

    # Load the Map-Reduce chain
    summarize_chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
        token_max=16000,  # CRITICAL FIX: Tell LangChain your model has a big context window!
        return_intermediate_steps=True, # Allow us to save the individual chunk summaries!
        verbose=True  # Set to True so you can watch the chunks process!
    )

    print("4. Executing Map-Reduce Final Summarization...")
    try:
        final_result = summarize_chain.invoke({"input_documents": final_safe_chunks})
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the individual semantic chunk summaries
        chunk_summaries = final_result.get("intermediate_steps", [])
        chunk_output_path = "outputs/chapter_summaries.txt"
        
        part_tracker = {}
        with open(chunk_output_path, "w", encoding='utf-8') as f:
            for chunk, chunk_summary in zip(final_safe_chunks, chunk_summaries):
                chap_id = chunk.metadata.get("chapter_id", "Unknown")
                
                # Advance the part counter for this specific chapter
                part_num = part_tracker.get(chap_id, 0) + 1
                part_tracker[chap_id] = part_num
                
                f.write(f"### Semantic Chapter {chap_id} (Part {part_num})\n\n")
                f.write(f"**Original Timeline (Subtitles & Frames):**\n")
                f.write(chunk.page_content + "\n\n")
                f.write(f"**AI Summary:**\n")
                f.write(chunk_summary + "\n\n")
                f.write("=" * 60 + "\n\n")
        print(f"✅ Extracted {len(chunk_summaries)} chunk summaries and saved to: {chunk_output_path}")

        # Save output
        with open(output_path, "w", encoding='utf-8') as f:
            f.write("# Final Multimodal Video Summary\n\n")
            f.write(final_result["output_text"])
            
        print(f"✅ Final Summary generated and saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during summarization execution: {e}")

if __name__ == "__main__":
    summarize_video()
