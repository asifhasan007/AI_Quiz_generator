import os
import yt_dlp
from moviepy import VideoFileClip
import logging 

def extract_audio_from_local_video(video_path, audio_output_path):
    try:
        print(f"-> Loading video: {os.path.basename(video_path)}")
        video_clip = VideoFileClip(video_path)
        print("--> Extracting audio...")
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_output_path, codec='mp3', logger=None)
        audio_clip.close()
        video_clip.close()
        print("---> Audio extraction successful.")
        return audio_output_path
    except Exception as e:
        print(f"Error processing local video: {e}")
        return None

def extract_audio_from_url(video_url, audio_output_path="temp_audio.mp3"):
    try:
        print(f"-> Connecting to URL: {video_url}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'outtmpl': audio_output_path.replace('.mp3', '')
        }
        print("--> Downloading and extracting audio...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        final_path = audio_output_path
        if not os.path.exists(final_path):
             final_path = audio_output_path.replace('.mp3', '.mp3')
        print("---> Audio extraction successful.")
        return final_path
    except Exception as e:
        print(f"Error processing URL: {e}")
        return None