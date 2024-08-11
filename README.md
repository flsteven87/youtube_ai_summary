# YouTube AI Summary

## Overview

YouTube AI Summary is a powerful tool designed to automate the process of transcribing and summarizing YouTube video content. Leveraging advanced AI technologies, this application provides users with concise, accurate summaries of video content, saving time and enhancing content comprehension.

## Features

- **Video Transcription**: Automatically transcribes YouTube video audio using state-of-the-art speech recognition technology.
- **AI-Powered Summarization**: Generates summaries using GPT-4, offering three levels of detail:
  - Executive Summary
  - Detailed Summary
  - Brief Summary
- **User-Friendly Interface**: Streamlit-based web application for easy interaction and result viewing.
- **Multilingual Support**: Capable of processing and summarizing content in multiple languages.
- **Efficient Processing**: Handles videos up to 60 minutes in length, with built-in audio splitting for longer content.

## Technology Stack

- Python 3.x
- Streamlit
- OpenAI GPT-4
- yt-dlp
- FFmpeg
- Groq API

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/flsteven87/youtube_ai_summary
   cd youtube_ai_summary
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

## Usage

1. Start the Streamlit application:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the provided local URL (usually `http://localhost:8501`).

3. Enter a YouTube video URL and select the desired summary method.

4. Click "Analyze Video" to start the process.

5. View the generated summary and full transcript in the application interface.

## Project Structure

- `app.py`: Main Streamlit application file.
- `src/`: Contains core functionality modules:
  - `downloader.py`: Handles YouTube video audio extraction.
  - `transcriber.py`: Manages audio transcription.
  - `summarizer.py`: Implements AI-powered summarization.
  - `audio_splitter.py`: Splits long audio files for processing.
- `config/`: Configuration files and settings.
- `data/`: Storage for audio files, transcripts, and summaries.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- OpenAI for GPT-4 technology
- Groq for their API services
- The yt-dlp team for their YouTube download library

## Contact

Your Name - flsteven87@gmail.com

Project Link: [https://github.com/flsteven87/youtube_ai_summary](https://github.com/flsteven87/youtube_ai_summary)