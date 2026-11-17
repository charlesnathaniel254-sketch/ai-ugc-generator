import streamlit as st
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import os
import random

# --- CONFIGURATION ---
PIXABAY_API_KEY = 58677440-eac0469ff49efb80b7f26c79f

def get_video_url(query):
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query.replace(' ', '+')}&per_page=5"
    response = requests.get(url).json()
    if response['hits']:
        # Pick a random video from the results
        video_data = random.choice(response['hits'])
        # Get the URL for a medium-sized video
        return video_data['videos']['medium']['url']
    return None

# --- WEBSITE INTERFACE ---
st.set_page_config(page_title="Pixabay UGC Maker", page_icon="🎬")
st.title("🎬 Smart UGC Machine (Pixabay Edition)")

script_input = st.text_area("What should the AI say?", "Enter your script here...")
visual_topic = st.text_input("What should the video show? (e.g. money, cars, crypto)", "technology")

if st.button("🚀 Generate My AI Video"):
    if PIXABAY_API_KEY == "PASTE_YOUR_PIXABAY_KEY_HERE":
        st.error("Please paste your Pixabay API Key in the code first!")
    else:
        with st.spinner("AI is finding the perfect video and recording voice..."):
            try:
                # 1. Create Voiceover
                tts = gTTS(text=script_input, lang='en')
                tts.save("voice.mp3")

                # 2. Search and Download Video
                video_url = get_video_url(visual_topic)
                if not video_url:
                    st.error("Could not find a video for that topic. Try a simpler word!")
                else:
                    r = requests.get(video_url, stream=True)
                    with open("bg.mp4", "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk: f.write(chunk)

                    # 3. Mix Video & Audio
                    audio = AudioFileClip("voice.mp3")
                    video = VideoFileClip("bg.mp4").subclip(0, audio.duration)
                    final = video.set_audio(audio)
                    final.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")

                    # 4. Show Video
                    st.video("output.mp4")
                    with open("output.mp4", "rb") as file:
                        st.download_button(label="📥 Download Video", data=file, file_name="ai_ugc_video.mp4", mime="video/mp4")
                    
                    st.success("Video Created! You are ready for ContentReward!")

            except Exception as e:
                st.error(f"Something went wrong: {e}")
