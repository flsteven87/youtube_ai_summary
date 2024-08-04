import os
import re
from dotenv import load_dotenv
from src.downloader import download_audio
from src.transcriber import audio_to_text
from src.summarizer import GPT4Summarizer
from config.settings import AUDIO_PATH, SUMMARY_PATH, TRANSCRIPT_PATH
from urllib.parse import urlparse, parse_qs
import requests

load_dotenv()

class VideoProcessor:
    def __init__(self, url):
        self.url = url
        self.audio_path = None
        self.transcript = None
        self.summary = None
        self.openai_summarizer = GPT4Summarizer()
        self.video_name = self.extract_video_name(url)

    def extract_video_name(self, url):
        try:
            # 使用requests獲取頁面內容
            response = requests.get(url)
            response.raise_for_status()
            
            # 使用正則表達式從頁面內容中提取視頻標題
            title_match = re.search(r'<title>(.*?)</title>', response.text)
            if title_match:
                video_title = title_match.group(1)
                # 移除" - YouTube"後綴（如果存在）
                video_title = video_title.replace(" - YouTube", "").strip()
                # 將標題轉換為有效的文件名
                video_name = re.sub(r'[^\w\-_\. ]', '_', video_title)
                return video_name
            else:
                return "unknown_video"
        except Exception as e:
            print(f"無法提取視頻名稱: {e}")
            return "unknown_video"

    def download_and_convert(self):
        os.makedirs(AUDIO_PATH, exist_ok=True)
        self.audio_path = download_audio(self.url, AUDIO_PATH)
        print(f"Audio downloaded and saved to: {self.audio_path}")

    def transcribe(self):
        if not self.audio_path:
            raise ValueError("Audio hasn't been downloaded yet. Call download_and_convert() first.")
        self.transcript = audio_to_text(self.audio_path)
        print("Audio transcription completed.")

    def summarize(self, method="gpt-4", num_sentences=3):
        if not self.transcript:
            raise ValueError("Transcript hasn't been generated yet. Call transcribe() first.")
        
        if method == "gpt-4":
            self.summary = self.openai_summarizer.summarize_with_gpt4(self.transcript)
            print("GPT-4 summarization completed.")
        else:
            raise ValueError("Invalid summarization method. Choose 'bert' or 'gpt-4'.")

    def save_transcript(self):
        if not self.transcript:
            raise ValueError("Transcript hasn't been generated yet. Call transcribe() first.")
        os.makedirs(TRANSCRIPT_PATH, exist_ok=True)
        filename = f"{self.video_name}.txt"
        output_path = os.path.join(TRANSCRIPT_PATH, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.transcript)
        print(f"Transcript saved to: {output_path}")

    def save_summary(self):
        if not self.summary:
            raise ValueError("Summary hasn't been generated yet. Call summarize() first.")
        os.makedirs(SUMMARY_PATH, exist_ok=True)
        filename = f"{self.video_name}.txt"
        output_path = os.path.join(SUMMARY_PATH, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.summary)
        print(f"Summary saved to: {output_path}")

def main():
    video_url = "https://www.youtube.com/watch?v=9pGwSCmCYAE&ab_channel=%E4%B8%9C%E4%BA%AC%E8%80%81%E8%90%A7"
    processor = VideoProcessor(video_url)
    processor.download_and_convert()
    processor.transcribe()
    processor.save_transcript()
    processor.summarize(method="gpt-4")
    processor.save_summary()

if __name__ == '__main__':
    main()