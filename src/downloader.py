import yt_dlp
import os
import logging
from config.settings import AUDIO_PATH

# 設置日誌記錄
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 創建一個控制台處理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 創建一個格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 將處理器添加到日誌記錄器
logger.addHandler(console_handler)

def download_audio(url, audio_path=AUDIO_PATH):
    logger.info(f"Starting download process for URL: {url}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(audio_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': logger,
        'progress_hooks': [logging_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Extracting video information...")
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            final_filename = os.path.splitext(filename)[0] + '.mp3'
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