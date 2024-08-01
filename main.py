import os
from dotenv import load_dotenv
from src.downloader import download_audio
from src.transcriber import audio_to_text
from src.summarizer import GPT4Summarizer
from config.settings import AUDIO_PATH, SUMMARY_PATH, TRANSCRIPT_PATH

load_dotenv()

class VideoProcessor:
    def __init__(self, url):
        self.url = url
        self.audio_path = None
        self.transcript = None
        self.summary = None
        self.openai_summarizer = GPT4Summarizer()

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

    def save_transcript(self, filename="transcript.txt"):
        if not self.transcript:
            raise ValueError("Transcript hasn't been generated yet. Call transcribe() first.")
        os.makedirs(TRANSCRIPT_PATH, exist_ok=True)
        output_path = os.path.join(TRANSCRIPT_PATH, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.transcript)
        print(f"Transcript saved to: {output_path}")

    def save_summary(self, filename="summary.txt"):
        if not self.summary:
            raise ValueError("Summary hasn't been generated yet. Call summarize() first.")
        os.makedirs(SUMMARY_PATH, exist_ok=True)
        output_path = os.path.join(SUMMARY_PATH, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.summary)
        print(f"Summary saved to: {output_path}")

def main():
    video_url = "https://www.youtube.com/watch?v=AHlu9tcz_Zc&ab_channel=%E7%AA%AE%E5%A5%A2%E6%A5%B5%E6%AC%B2"
    processor = VideoProcessor(video_url)
    processor.download_and_convert()
    processor.transcribe()
    processor.save_transcript()
    processor.summarize(method="gpt-4")
    processor.save_summary()

if __name__ == '__main__':
    main()