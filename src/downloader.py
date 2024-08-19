import yt_dlp
import os
import logging
from config.settings import AUDIO_PATH

logger = logging.getLogger(__name__)

def download_audio(url, audio_path=AUDIO_PATH, video_name=None):
    logger.info(f"Starting download process for URL: {url}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(audio_path, f'{video_name}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': logger,
        'progress_hooks': [logging_hook],
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'cookiefile': 'cookies.txt',  # Ensure you have a valid cookies.txt file in the working directory
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Extracting video information...")
            ydl.download([url])
            final_filename = os.path.join(audio_path, f'{video_name}.mp3')
            logger.info(f"Download completed. File saved as: {final_filename}")
            return final_filename
    except Exception as e:
        logger.error(f"An error occurred during download: {str(e)}")
        raise

def logging_hook(d):
    if d['status'] == 'downloading':
        percent = d['_percent_str']
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        logger.info(f"Downloading: {percent} complete - Speed: {speed} - ETA: {eta}")
    elif d['status'] == 'finished':
        logger.info(f"Download finished, now converting...")
    elif d['status'] == 'error':
        logger.error(f"Error occurred during download")
