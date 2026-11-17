import os
import requests
from gtts import gTTS
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip

# ==========================================
# 1. CONFIGURATION
# ==========================================
TOPIC = "Make money online with crypto apps"
OUTPUT_FILENAME = "final_ugc_video.mp4"

# ==========================================
# 2. GENERATE SCRIPT & VOICEOVER
# ==========================================
print("🎙️ Generating AI Voiceover...")

# UGC Script text for the video
script_text = (
    "Stop scrolling! Here is how people are making extra rewards every single day. "
    "Check out this platform, complete simple tasks, and claim your rewards directly to your wallet. "
    "Don't miss out, click the link in bio to start today!"
)

# Generate AI Voiceover (Audio MP3)
tts = gTTS(text=script_text, lang='en', slow=False)
tts.save("voiceover.mp3")

# ==========================================
# 3. DOWNLOAD HD B-ROLL VIDEO CLIPS
# ==========================================
print("🎥 Fetching HD Video Clips...")

# Sample high-quality background video
video_url = "https://assets.mixkit.co/videos/preview/mixkit-hands-holding-a-smartphone-with-green-screen-41528-large.mp4"
r = requests.get(video_url)
with open("background.mp4", "wb") as f:
    f.write(r.content)

# ==========================================
# 4. ASSEMBLE FINAL VIDEO
# ==========================================
print("🎬 Assembling AI Video...")

# Load Audio & Video
audio_clip = AudioFileClip("voiceover.mp3")
video_clip = VideoFileClip("background.mp4").subclip(0, audio_clip.duration)

# Set Video Audio to the AI Voiceover
final_video = video_clip.set_audio(audio_clip)

# Export the Final MP4 Video
final_video.write_videofile(OUTPUT_FILENAME, fps=24)

print(f"✅ SUCCESS! Your AI Video is ready: {OUTPUT_FILENAME}")
