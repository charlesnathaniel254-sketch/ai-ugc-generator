import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import os
import random

# --- CONFIGURATION ---
PIXABAY_API_KEY = "58677440-eac0469ff49efb80b7f26c79f"
ELEVENLABS_API_KEY = "sk_49418b58859360cb77828fc11dd4478d5fbb95fe0e74ab74"

VOICE_ACTORS = {
    "Adam (Deep Male)": "pNInz6OBpvM9S3FwmsBx",
    "Antoni (Friendly Male)": "ErXwbcqjndD1oXOBrbk5",
    "Bella (Soft Female)": "EXAVITQu4vr4PUHQRh6w",
    "Rachel (High Energy Female)": "21m00Tcm4TbcDqotnKud"
}

def get_voiceover(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {"text": text, "model_id": "eleven_monolingual_v1", "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}}
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        return False, response.text # Return the error message
    
    with open("voice.mp3", "wb") as f:
        f.write(response.content)
    return True, "Success"

def get_video_url(query):
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query.replace(' ', '+')}&per_page=5"
    response = requests.get(url).json()
    if 'hits' in response and response['hits']:
        video_data = random.choice(response['hits'])
        return video_data['videos']['medium']['url']
    return None

# --- WEBSITE ---
st.title("🎬 UGC Maker Machine")

script_input = st.text_area("Script:", "Hi! Start earning rewards today.")
visual_topic = st.text_input("Visuals:", "money")
selected_voice = st.selectbox("Voice Actor:", list(VOICE_ACTORS.keys()))

if st.button("🚀 Generate Video"):
    with st.spinner("Processing..."):
        # 1. Voiceover Check
        success, message = get_voiceover(script_input, VOICE_ACTORS[selected_voice])
        
        if not success:
            st.error(f"ElevenLabs Error: {message}")
            st.info("Check if your ElevenLabs API Key is correct and has 'Text to Speech' access enabled.")
        else:
            # 2. Video Search
            video_url = get_video_url(visual_topic)
            if not video_url:
                st.error("Could not find a video. Try a different visual topic.")
            else:
                # 3. Create Final Video
                r = requests.get(video_url, stream=True)
                with open("bg.mp4", "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: f.write(chunk)

                audio = AudioFileClip("voice.mp3")
                video = VideoFileClip("bg.mp4").subclip(0, audio.duration)
                final = video.set_audio(audio)
                final.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")
                st.video("output.mp4")
                st.success("Done!")
