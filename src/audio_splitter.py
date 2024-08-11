import os
import logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)

def split_audio(audio_path, max_duration_seconds=600, output_format="mp3"):
    logger.info(f"Starting to split audio file: {audio_path}")
    
    # 載入音頻文件
    audio = AudioSegment.from_file(audio_path)
    total_duration = len(audio)
    logger.info(f"Total audio duration: {total_duration/1000:.2f} seconds")

    # 轉換最大持續時間為毫秒
    max_duration_ms = max_duration_seconds * 1000

    chunks = []
    for start in range(0, total_duration, max_duration_ms):
        end = min(start + max_duration_ms, total_duration)
        
        chunk = audio[start:end]
        
        # 生成輸出文件名
        chunk_filename = f"{os.path.splitext(audio_path)[0]}_chunk_{start//1000}_{end//1000}.{output_format}"
        
        logger.info(f"Exporting chunk: {start//1000}s to {end//1000}s")
        chunk.export(chunk_filename, format=output_format)
        
        chunks.append(chunk_filename)
        
        logger.info(f"Chunk saved as: {chunk_filename}")

    logger.info(f"Audio splitting completed. Total chunks: {len(chunks)}")
    return chunks

def estimate_transcription_cost(audio_path):
    audio = AudioSegment.from_file(audio_path)
    duration_minutes = len(audio) / 60000  # 轉換為分鐘
    cost_per_minute = 0.006  # Whisper API 的價格（可能需要更新）
    estimated_cost = duration_minutes * cost_per_minute
    logger.info(f"Estimated transcription cost for {audio_path}: ${estimated_cost:.2f}")
    return estimated_cost

if __name__ == "__main__":
    # 測試代碼
    audio_file = "path/to/your/audio/file.mp3"
    chunks = split_audio(audio_file)
    estimate_transcription_cost(audio_file)