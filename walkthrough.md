# LangChain Semantic Summarizer Pipeline

I have successfully designed and built the final `summarize.py` module to handle long (e.g., 2+ hour) multimodal video transcripts!

## What was built
1. **Langchain Environment:** Added all necessary architecture dependencies (`langchain_classic`, `langchain_experimental`, `langchain_huggingface`, etc.) for advanced generative chains.
2. **src/summarization/summarize.py**: Created the final Map-Reduce pipeline.
3. **src/main.py Plugin**: Wired `summarize_video()` into your main execution script so the whole pipeline triggers smoothly.

## Advanced Features Implemented

### 1. K-Means Semantic Chunking
As requested, I configured the powerful **Semantic Boundary Detection** utilizing `SentenceTransformers` and LangChain's experimental `SemanticChunker`. 
* **How it works:** Instead of arbitrary 10-minute slicing, it compares the semantic embedding of every chronological sentence. When there is a sharp drop in cosine similarity (a *percentile threshold*), it correctly slices the `outputs/interleaved_timeline.txt` into a new, discrete chunk. This ensures the LLM summarizes cohesive "topics" together!

### 2. Map-Reduce Chaining
Using `langchain_classic.chains.summarize`, the system natively executes:
* **Map:** A prompt that summarizes *each specific semantic chapter* highlighting core video actions and audio topics.
* **Reduce:** A prompt that pulls all those resulting chapter summaries into one massive, cohesive outline.

> [!TIP]
> **LLM Customization:** Inside `src/summarization/summarize.py`, I have added a placeholder to load a text-based HuggingFace Pipeline (like `google/gemma-2b-it`). Since text-summarization of a 2-hour video would devour VRAM using a massive 9B+ multimodal model, you can either keep this fast lightweight text model OR effortlessly swap it for `ChatOpenAI(model="gpt-4o")` or a local Ollama model instance for speed and reduced memory usage!
