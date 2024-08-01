import os
from src.downloader import download_video
from src.converter import video_to_audio
from src.transcriber import audio_to_text
from src.organizer import organize_files
from src.summarizer import BertSummarizer, summarize_with_gpt4
from config.settings import DOWNLOAD_PATH, AUDIO_PATH, SUMMARY_PATH

def generate_file_name(url):
    video_id = url.split('v=')[1].split('&')[0]
    return video_id

def process_video(url):
    video_path = download_video(url)
    audio_path = video_to_audio(video_path)
    transcript = audio_to_text(audio_path)
    organize_files(video_path, audio_path, transcript)
    file_name = generate_file_name(url)
    return transcript, audio_path, file_name

def summarize_transcript(transcript, method="bert", num_sentences=3):
    if method == "bert":
        summarizer = BertSummarizer()
        summary = summarizer.summarize(transcript, num_sentences=num_sentences)
    elif method == "gpt-4":
        summary = summarize_with_gpt4(transcript)
    else:
        raise ValueError("Invalid summarization method. Choose 'bert' or 'gpt-4'.")
    return summary

def save_summary(summary, file_name):
    summary_path = os.path.join(SUMMARY_PATH, f"{file_name}_summary.txt")
    with open(summary_path, 'w', encoding='utf-8') as file:
        file.write(summary)
    print(f"Summary saved to {summary_path}")

def main(url=None, transcript_path=None, method="bert"):
    if url:
        transcript, audio_path, file_name = process_video(url)
    elif transcript_path:
        with open(transcript_path, 'r', encoding='utf-8') as file:
            transcript = file.read()
        audio_path = os.path.splitext(transcript_path)[0]
        file_name = os.path.basename(audio_path)
    else:
        raise ValueError("Either a URL or a transcript file path must be provided.")
    
    summary = summarize_transcript(transcript, method=method)
    save_summary(summary, file_name)

if __name__ == '__main__':
    # 提供 YouTube 視頻 URL 或轉錄文本文件路徑來運行
    video_url = "https://www.youtube.com/watch?v=_5jQayO-MQY&ab_channel=MervinPraison"  # 替換為實際 URL
    
    main(url=video_url, method="gpt-4")  # 使用 GPT-4 進行摘要
    # main(url=video_url, method="bert")  # 使用 BERT 進行摘要