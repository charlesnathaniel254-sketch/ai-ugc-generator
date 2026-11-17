import streamlit as st
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import os

# --- WEBSITE INTERFACE ---
st.set_page_config(page_title="AI UGC Maker", page_icon="🎬")
st.title("🎬 UGC Maker Machine")
st.write("Generate AI videos for ContentReward.com automatically.")

# User Inputs
script_input = st.text_area("What should the AI say?", "Enter your script here...")
video_link = st.text_input("Background Video URL (Direct .mp4 link)", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4")

if st.button("🚀 Generate My UGC Video"):
    with st.spinner("Creating your video... this takes about 30 seconds."):
        try:
            # 1. Create Voiceover
            tts = gTTS(text=script_input, lang='en')
            tts.save("voice.mp3")

            # 2. Download Video
            r = requests.get(video_link, stream=True)
            with open("bg.mp4", "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: f.write(chunk)

            # 3. Mix Video & Audio
            audio = AudioFileClip("voice.mp3")
            video = VideoFileClip("bg.mp4").subclip(0, audio.duration)
            final = video.set_audio(audio)
            final.write_videofile("output.mp4", fps=24, codec="libx264")

            # 4. Show Video on Website
            st.video("output.mp4")
            
            # 5. Download Button
            with open("output.mp4", "rb") as file:
                st.download_button(label="📥 Download Video", data=file, file_name="my_ugc_video.mp4", mime="video/mp4")
            
            st.success("Video Finished!")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
