import moviepy.editor as mp
import os
from config.settings import AUDIO_PATH

def video_to_audio(video_path, target_bitrate="64k",):
    video = mp.VideoFileClip(video_path)
    audio_path = os.path.join(AUDIO_PATH, os.path.splitext(os.path.basename(video_path))[0] + '.mp3')
    video.audio.write_audiofile(audio_path, bitrate=target_bitrate)
    return audio_path
