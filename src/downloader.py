from pytube import YouTube
import os
from config.settings import DOWNLOAD_PATH

def download_video(url, download_path=DOWNLOAD_PATH):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    stream.download(output_path=download_path)
    return os.path.join(download_path, stream.default_filename)
