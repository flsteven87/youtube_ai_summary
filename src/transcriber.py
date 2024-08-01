import os
from groq import Groq
from config.settings import AUDIO_PATH
from src.audio_splitter import split_audio
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')


def audio_to_text(audio_path):
    client = Groq(api_key=GROQ_API_KEY)
    transcripts = []

    audio_chunks = split_audio(audio_path, chunk_size_mb=15)

    for chunk_path in audio_chunks:
        with open(chunk_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(chunk_path, file.read()),
                model="whisper-large-v3",
                prompt="",  # 可選項，根據需要指定上下文或拼寫
                response_format="json",  # 可選項
                language="zh",  # 設置為中文
                temperature=0.0  # 可選項
            )
            transcripts.append(transcription.text)
        os.remove(chunk_path)  # 刪除臨時文件

    full_transcript = "\n".join(transcripts)
    return full_transcript
