import os
import logging
from groq import Groq
from config.settings import AUDIO_PATH
from src.audio_splitter import split_audio
from dotenv import load_dotenv

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

load_dotenv()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def audio_to_text(audio_path, chunk_duration_seconds=600):
    logger.info(f"Starting transcription process for audio: {audio_path}")
    
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not found in environment variables.")
        raise ValueError("GROQ_API_KEY is not set")

    client = Groq(api_key=GROQ_API_KEY)
    transcripts = []

    logger.info("Splitting audio into chunks...")
    audio_chunks = split_audio(audio_path, max_duration_seconds=chunk_duration_seconds)
    logger.info(f"Audio split into {len(audio_chunks)} chunks.")

    for i, chunk_path in enumerate(audio_chunks, 1):
        logger.info(f"Processing chunk {i}/{len(audio_chunks)}: {chunk_path}")
        try:
            with open(chunk_path, "rb") as file:
                logger.info(f"Sending chunk {i} to Groq API for transcription...")
                transcription = client.audio.transcriptions.create(
                    file=(chunk_path, file.read()),
                    model="whisper-large-v3",
                    prompt="",
                    response_format="json",
                    language="zh",
                    temperature=0.0
                )
                transcripts.append(transcription.text)
                logger.info(f"Chunk {i} transcription completed.")
            
            logger.info(f"Removing temporary file: {chunk_path}")
            os.remove(chunk_path)
        except Exception as e:
            logger.error(f"Error processing chunk {i}: {str(e)}")
            # 可以選擇在這裡添加重試邏輯

    logger.info("All chunks processed. Combining transcripts...")
    full_transcript = "\n".join(transcripts)
    logger.info(f"Full transcription completed. Total length: {len(full_transcript)} characters.")

    return full_transcript

if __name__ == "__main__":
    # 測試代碼
    test_audio_path = "path/to/your/test/audio.mp3"
    transcript = audio_to_text(test_audio_path)
    logger.info(f"Transcript preview: {transcript[:500]}...")  # 顯示前500個字符作為預覽