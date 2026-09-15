# Recursive Logic

# Step A: It looks for \n\n. if it can't find them, it moves to \n.

# Step B: If the text is still > 1000 characters, it looks for the nearest period followed by a space(. ) to avoid cutting a sentence in half.




# Step C: If a single sentence is somehow longer than 1000 characters, it will resort to splitting at the nearest space ( ).

import time
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from IPython.display import Markdown, display
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Initialize the model with Ollama
# You need to have Ollama server running and the 'llama2' model pulled.
# For example: ollama run llama2
llm = OllamaLLM(model="llama2")

# 1. Define your splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # Large enough to hold a full idea
    chunk_overlap=200,     # Overlap to maintain narrative flow
    separators=["\n\n", "\n", ". ", " ", ""]
)

# 2. Split your long document
text = "Hi everyone, my name is Kevin. Today I want to show you how you could take a PowerPoint presentation and convert it into a video for YouTube or any other video service, whether it be Vimeo or anything else or Facebook or wherever you want to upload your video to. and as a full disclosure before we jump into this i work at microsoft as a full-time employee all right well let's jump on the pc here i am at my desktop and i have powerpoint on my taskbar here this is a powerpoint that comes with office 365 This in greatest version. However, if you have an older version of PowerPoint, you should also be able to do this, but I just can't guarantee that things will look the same. Okay, well, so I have this slide deck and what I'd love to do is I want to add some narration, some video on. Top and then I want to package it all and upload it to YouTube as a video. So the first thing that we're going to do is click on this pivot option that says slideshow. So I'm going to go ahead and click on that and then under here you'll see an option right under transcribe the following segment in its original language. Follow these specific instructions for formatting the answer. This slideshow pivot that says record slideshow. And what I'm going to do is you could either record from the current slide or from the beginning, but in this case the current slide is the beginning, so it doesn't matter which one I choose. So I'm going to go ahead and say from the beginning. Now, a few things that I could do on it. Transcribe the following segment. You see this big red record button well that's how I record I could also stop recording and then I could also play it to hear how it sounds I have some settings under here where I could choose my microphone I could choose my camera I'm in this case you see me showing up here because using my webcam to get my video onto this slide and you have options where you could turn your microphone on and off your camera on and off and you could turn on the preview or not the preview so it's kind of cool because what i could do is i can record myself going through this presentation Going through it and people can also see me on the video, so it's a really nice format for say a YouTube video. What I can also do as I'm going through it is I also have a pen and I have a highlighter. Um so here I can highlight things on my slide as I'm going through. and those different animations will show up as I go through the slides so let's let's give this a shot and i could also show notes if i want to okay so let's let's go ahead and record hi everyone my name is kevin with Eleven's cookie company and today I wanted to walk through some of our recent results that we've had with the cookie company. Now, sales have really been growing exponentially. You see these cookies represent our growth right there and really customers love our products. Say love, I mean they really love these cookies and also not only do our customers love our cookies but our staff love working for this company. In fact, people love us so much that we've enabled to open three additional locations. We have a location at. Recently opened up in Pennsylvania, we have a new New Jersey location and a New York location. In addition to all these other blue dots, we are a very big company because look at all these locations all over the map. Sales, sales have been doing fantastic. There's really nothing bad to report. We've had just amazing performance. And that wraps up the presentation. So now that I've finished the presentation, what I'm going to do is I'm going to click on the stop button and And now what I can do is I can just close this out and you can see the total recording was about 1 minute long. I'm going to hit this X button. Now that I've finished recording it, here I am back on the main slide view and on each slide now you see a video that I can move around to different locations. this is my video of me talking and each slide has that and what i could do is i could simply click on this play button my name is Kevin with Kevin's Cookie Company and today i want and so now what i could do is i could send the deck out to someone that could go slide by slide and they could see my recording or what I could do is if I want to prep it where it's just kind of a package that I could send off to YouTube or Facebook or Vimeo or wherever I want to share this um now I could simply click on export and create a video um you can do it in uh create video um you can do it in Ultra HD which is 4K or 1080p. So I'll just do 4K and I'm going to create the video. And what it's going to do is I'm going to use my recorded timings as I was going through it and I also want to use my narrations. So sure it sounds good. Let's create the video. And now I just have to choose a location so I'm going to put it on my desktop and we'll say we'll just call this Kevin Cookie Company video and let's put it on my desktop it's going to take a little bit of time to go through See in the bottom right hand corner it's rendering the video and depending on, you know, how long it is, how many slides you have, how much video narration included, it might take a little bit longer to go through and render, so we'll just hang out for a moment until it's done. How long is this video render going? Wing it to take. I don't know. It's going kind of slow. Looks like it has finished rendering the video. I'm going to go ahead and minimize PowerPoint and go back to my desktop and let's uh play this. Hey everyone, my name is Kevin with Kevin's Cookie Company and today I wanted to walk through some of our recent updates that we've had with the cookie company. Now sales have really So there you see, uh the video is playing. See these cookies that represent our So here you see a video with my PowerPoint presentation. It has the annotations that I do there this slide. It has my video down in the bottom right-hand corner, and then it also has my narration on top of the slide. Um so this is a video that's really ready to go and let's say I transcribe the following segment in its original language. my Kevin Cookie company website or my channel on YouTube that i want to upload to i can now take this file and it is just an mp4 file and i can just upload that to youtube i'm going to go to youtube here all i do is transcribe the following segment Top right hand corner, I click on this plus button, upload video, and what I could do then is I'm going to go ahead and show my desktop. I could drag this video that I just created and I could drag and drop it and upload it to my YouTube channel. I'm not going to do that because this is just a a A video that I created, uh just for this walkthrough. Uh but that's really as simple as it is. I could create a video in PowerPoint, include my video image on there, or webcam image. I could have narration on top. I could have the annotations. Um you could really make some rich content. in PowerPoint and then export it as a pmp4 file that you could upload to any video service if this video helped you create your first PowerPoint that you can now upload online please give this video a thumbs up if you want to see more videos like this in the future please hit subscribe Subscribe button that way you'll get a notification anytime new content like this comes out and if there are any other video topics that you want me to cover in the future leave a comment down below I read them and I'll add it to my list of videos to create in the future all right well thanks a lot for tuning in I'll see you next time bye"

chunks = splitter.split_text(text)

# 3. Define the prompt (CRITICAL FIX)
summarize_prompt = PromptTemplate.from_template("Summarize the following text:\n{text}")

# Start the total timer
start_total = time.perf_counter()

chunk_times = []
summaries = []

# 3. Summarization Logic with Timing
for i, c in enumerate(chunks):
    print(f"\n" + "="*50)
    print(f"PROCESSING CHUNK {i+1}")
    print(f"="*50)
    
    # Print the FULL original text chunk
    print(f"\n[ORIGINAL TEXT]:\n{c}")
    
    start_chunk = time.perf_counter()
    response = llm.invoke(summarize_prompt.format(text=c))
    end_chunk = time.perf_counter()
    
    duration = end_chunk - start_chunk
    chunk_times.append(duration)
    
    content = response.content if hasattr(response, 'content') else response
    summaries.append(content)
    
    # Print the summary
    print(f"\n[SUMMARY]:\n{content}")
    print(f"\nTime: {duration:.2f} seconds")


# Final Reduce Step
final_response = llm.invoke(summarize_prompt.format(text=" ".join(summaries)))
final_summary = final_response.content if hasattr(final_response, 'content') else final_response

# End the total timer
end_total = time.perf_counter()
total_duration = end_total - start_total

# Display results
display(Markdown(f"# Final Summary\n{final_summary}"))
print(f"\nTotal Processing Time: {total_duration:.2f} seconds")
# Added a check to avoid division by zero if chunks is empty
if chunk_times:
    print(f"Average time per chunk: {sum(chunk_times)/len(chunk_times):.2f} seconds")
