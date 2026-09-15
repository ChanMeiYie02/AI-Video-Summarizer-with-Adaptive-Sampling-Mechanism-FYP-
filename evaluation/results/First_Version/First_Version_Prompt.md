**map\_prompt\_template** = """

&#x20;   You are an expert video summarizer. The following is a raw segment of a multimodal video timeline containing spoken audio and keyframe visual descriptions in chronological order.

&#x20;   Extract the core events, topics discussed, and visual actions taking place in this chunk.

&#x20;   

&#x20;   Raw Video Chunk:

&#x20;   {text}

&#x20;   

&#x20;   Chunk Summary:"""





**reduce\_prompt\_template** = """

&#x20;   You have been given a series of chronological summaries covering different chapters of a video.

&#x20;   Synthesize these chunk summaries into a single cohesive, high-level outline and summary of the entire video.

&#x20;   

&#x20;   Chapter Summaries:

&#x20;   {text}

&#x20;   

&#x20;   Final Comprehensive Video Summary:"""



**---------------------------------------------------**

**Conclusion: LLM may generate overly long summaries**

**---------------------------------------------------**



