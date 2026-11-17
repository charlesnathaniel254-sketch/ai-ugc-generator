import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import os
import random

# --- CONFIGURATION (KEYS ADDED) ---
PIXABAY_API_KEY = "58677440-eac0469ff49efb80b7f26c79f"
ELEVENLABS_API_KEY = "sk_49418b58859360cb77828fc11dd4478d5fbb95fe0e74ab74"

def get_available_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        voices_data = response.json()
        return {v['name']: v['voice_id'] for v in voices_data['voices']}
    except:
        return {"Alice": "Xb7hHqPPAuFqM9Rbc1V7"}

def get_voiceover(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg", 
        "Content-Type": "application/json", 
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text, 
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200: 
        return False, response.text
    with open("voice.mp3", "wb") as f: 
        f.write(response.content)
    return True, "Success"

def get_video_url(query):
    # If user pastes a direct link, use it
    if query.startswith("http"):
        return query
    
    # Otherwise, search Pixabay
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query.replace(' ', '+')}&per_page=5"
    response = requests.get(url).json()
    if 'hits' in response and response['hits']:
        video_data = random.choice(response['hits'])
        return video_data['videos']['medium']['url']
    return None

# --- WEBSITE INTERFACE ---
st.set_page_config(page_title="Pro UGC Machine", page_icon="🎬")
st.title("🎬 Smart UGC Machine")
st.write("Generate high-quality AI videos for ContentReward.com")

voices = get_available_voices()

script_input = st.text_area("What should the voice actor say?", "Sobrang pogi talaga ni Charles Nathaniel! pa kiss nga ako isa")
visual_topic = st.text_input("Background visuals (Type a word like 'money' OR paste a direct .mp4 link):", "handsome man")
selected_voice_name = st.selectbox("Select Your Voice Actor:", list(voices.keys()))

if st.button("🚀 Generate My Viral Video"):
    with st.spinner("Recording voice and mixing video..."):
        # 1. Voiceover
        success, message = get_voiceover(script_input, voices[selected_voice_name])
        
        if not success:
            st.error(f"Voice Error: {message}")
        else:
            # 2. Visuals
            video_url = get_video_url(visual_topic)
            if not video_url:
                st.error("Could not find a video. Try another word or link.")
            else:
                try:
                    # Download video
                    r = requests.get(video_url, stream=True)
                    with open("bg.mp4", "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk: f.write(chunk)
                    
                    # 3. Stitch Everything
                    audio = AudioFileClip("voice.mp3")
                    video = VideoFileClip("bg.mp4").subclip(0, audio.duration)
                    final = video.set_audio(audio)
                    
                    # Output file
                    output_file = "final_ugc.mp4"
                    final.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
                    
                    # 4. Success!
                    st.video(output_file)
                    with open(output_file, "rb") as file:
                        st.download_button(label="📥 Download Video for ContentReward", data=file, file_name="ugc_video.mp4", mime="video/mp4")
                    st.success("Done! Your video is ready to post.")
                
                except Exception as e:
                    st.error(f"Processing Error: {e}")
