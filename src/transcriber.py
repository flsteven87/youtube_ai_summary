import os
import logging
from groq import Groq
from config.settings import AUDIO_PATH
from src.audio_splitter import split_audio
import streamlit as st
from openai import OpenAI
from openai.types.audio import Transcription

# 設置日誌記錄
logger = logging.getLogger(__name__)

# 使用 Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

def audio_to_text(audio_path, chunk_duration_seconds=600, service='groq', language='zh'):
    logger.info(f"Starting transcription process for audio: {audio_path}")

    if service == 'groq':
        if not GROQ_API_KEY:
            logger.error("GROQ_API_KEY not found in Streamlit secrets.")
            raise ValueError("GROQ_API_KEY is not set")
        client = Groq(api_key=GROQ_API_KEY)
    elif service == 'openai':
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not found in Streamlit secrets.")
            raise ValueError("OPENAI_API_KEY is not set")
        client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        logger.error("Unsupported service specified.")
        raise ValueError("Unsupported service specified.")

    transcripts = []

    logger.info("Splitting audio into chunks...")
    audio_chunks = split_audio(audio_path, max_duration_seconds=chunk_duration_seconds)
    logger.info(f"Audio split into {len(audio_chunks)} chunks.")

    for i, chunk_path in enumerate(audio_chunks, 1):
        logger.info(f"Processing chunk {i}/{len(audio_chunks)}: {chunk_path}")
        try:
            with open(chunk_path, "rb") as file:
                if service == 'groq':
                    logger.info(f"Sending chunk {i} to Groq API for transcription...")
                    transcription = client.audio.transcriptions.create(
                        file=(chunk_path, file.read()),
                        model="whisper-large-v3",
                        prompt="",
                        language=language,
                        temperature=0.0
                    )
                    transcripts.append(transcription.text)
                elif service == 'openai':
                    logger.info(f"Sending chunk {i} to OpenAI API for transcription...")
                    params = {
                        'file': file,
                        'model': 'whisper-1',
                        'response_format': 'text',
                        'language': language,
                        'temperature': 0.0
                    }
                    transcription: Transcription = client.Audio.transcriptions.create(**params)
                    transcripts.append(transcription['text'])

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
    transcript = audio_to_text(test_audio_path, service='groq')  # 可以選擇 'groq' 或 'openai'
    logger.info(f"Transcript preview: {transcript[:500]}...")  # 顯示��500個字符作為預覽