import os
from pydub import AudioSegment

def split_audio(audio_path, chunk_size_mb=20):
    audio = AudioSegment.from_file(audio_path)
    file_size = os.path.getsize(audio_path)  # 獲取文件大小（字節）
    total_duration = len(audio)  # 獲取音頻總時長（毫秒）
    
    chunk_size_bytes = chunk_size_mb * 1024 * 1024  # 將大小轉換為字節
    num_chunks = (file_size // chunk_size_bytes) + 1  # 計算需要多少塊
    chunk_duration = total_duration // num_chunks  # 每塊的時長（毫秒）

    chunks = []
    for i in range(0, len(audio), chunk_duration):
        end = min(i + chunk_duration, len(audio))
        chunk = audio[i:end]
        chunk_path = f"{audio_path}_chunk_{i//1000}_{end//1000}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    
    return chunks
