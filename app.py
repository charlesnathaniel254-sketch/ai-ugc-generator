import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import os
import random

# --- CONFIGURATION ---
PIXABAY_API_KEY = "58677440-eac0469ff49efb80b7f26c79f"
ELEVENLABS_API_KEY = "sk_49418b58859360cb77828fc11dd4478d5fbb95fe0e74ab74"

# Voice Actor IDs (These are real human-sounding voices)
VOICE_ACTORS = {
    "Adam (Deep Male - Hype)": "pNInz6OBpvM9S3FwmsBx",
    "Antoni (Friendly Male - Relaxed)": "ErXwbcqjndD1oXOBrbk5",
    "Bella (Soft Female - Trustworthy)": "EXAVITQu4vr4PUHQRh6w",
    "Rachel (High Energy Female - UGC Style)": "21m00Tcm4TbcDqotnKud"
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
    with open("voice.mp3", "wb") as f:
        f.write(response.content)

def get_video_url(query):
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query.replace(' ', '+')}&per_page=5"
    response = requests.get(url).json()
    if response['hits']:
        video_data = random.choice(response['hits'])
        return video_data['videos']['medium']['url']
    return None

# --- WEBSITE INTERFACE ---
st.set_page_config(page_title="Pro UGC Machine", page_icon="🎙️")
st.title("🎬 Smart UGC Machine")

script_input = st.text_area("What should the voice actor say?", "Hey guys! Check out this amazing rewards app.")
visual_topic = st.text_input("Background visuals (e.g. money, beach, coding)", "money")

# DROPDOWN FOR VOICE ACTORS
selected_voice_name = st.selectbox("Select your Voice Actor:", list(VOICE_ACTORS.keys()))
selected_voice_id = VOICE_ACTORS[selected_voice_name]

if st.button("🚀 Generate AI UGC Video"):
    if PIXABAY_API_KEY == "YOUR_PIXABAY_KEY" or ELEVENLABS_API_KEY == "YOUR_ELEVENLABS_KEY":
        st.error("Please add both API keys to the code!")
    else:
        with st.spinner("Voice actor is recording and AI is finding video..."):
            try:
                # 1. Get Human-like Voiceover
                get_voiceover(script_input, selected_voice_id)

                # 2. Get Video
                video_url = get_video_url(visual_topic)
                r = requests.get(video_url, stream=True)
                with open("bg.mp4", "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: f.write(chunk)

                # 3. Mix
                audio = AudioFileClip("voice.mp3")
                video = VideoFileClip("bg.mp4").subclip(0, audio.duration)
                final = video.set_audio(audio)
                final.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")

                st.video("output.mp4")
                st.success(f"Video finished using {selected_voice_name}!")
                
            except Exception as e:
                st.error(f"Error: {e}")
