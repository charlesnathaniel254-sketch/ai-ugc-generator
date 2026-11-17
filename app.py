import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import os
import random

# --- CONFIGURATION ---
PIXABAY_API_KEY = "58677440-eac0469ff49efb80b7f26c79f"
ELEVENLABS_API_KEY = "sk_49418b58859360cb77828fc11dd4478d5fbb95fe0e74ab74"

# This function gets the REAL voices currently in your account
def get_available_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        voices_data = response.json()
        voice_dict = {v['name']: v['voice_id'] for v in voices_data['voices']}
        return voice_dict
    except:
        return {"Default Voice": "21m00Tcm4TbcDqotnKud"} # Fallback

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
        return False, response.text
    
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

# --- WEBSITE INTERFACE ---
st.title("🎬 UGC Maker Machine")

# Get the list of actors automatically
voices = get_available_voices()

script_input = st.text_area("What should they say?", "Hi, this is a test.")
visual_topic = st.text_input("Background visuals:", "money")
selected_voice_name = st.selectbox("Select Voice Actor:", list(voices.keys()))

if st.button("🚀 Generate Video"):
    with st.spinner("Generating..."):
        # 1. Voice
        success, message = get_voiceover(script_input, voices[selected_voice_name])
        
        if not success:
            st.error(f"ElevenLabs Error: {message}")
        else:
            # 2. Video
            video_url = get_video_url(visual_topic)
            if not video_url:
                st.error("No video found for that topic.")
            else:
                r = requests.get(video_url, stream=True)
                with open("bg.mp4", "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: f.write(chunk)

                # 3. Stitch
                audio = AudioFileClip("voice.mp3")
                video = VideoFileClip("bg.mp4").subclip(0, audio.duration)
                final = video.set_audio(audio)
                final.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")
                st.video("output.mp4")
                st.success("Done!")
