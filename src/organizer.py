import os

def save_transcript(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

def organize_files(video_path, audio_path, transcript):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    text_path = f'data/transcripts/{base_name}.txt'
    save_transcript(transcript, text_path)
