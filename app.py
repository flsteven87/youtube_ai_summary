import streamlit as st
import os
from video_processor import VideoProcessor
from config.settings import TRANSCRIPT_PATH, SUMMARY_PATH
import json
from streamlit_extras.stoggle import stoggle

# Function to read file content
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Function to save processed video info
def save_video_info(video_name, youtube_url):
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = {}
    st.session_state.processed_videos[video_name] = youtube_url
    
    # Save to a JSON file
    with open('processed_videos.json', 'w') as f:
        json.dump(st.session_state.processed_videos, f)

# Function to load processed video info
def load_video_info():
    if os.path.exists('processed_videos.json'):
        with open('processed_videos.json', 'r') as f:
            st.session_state.processed_videos = json.load(f)
    else:
        st.session_state.processed_videos = {}

# Main function for video analysis
def analyze_video(youtube_url, summary_method, force_summarize=False):
    try:
        processor = VideoProcessor(youtube_url)
        
        # Check video duration
        duration = processor.get_video_duration()
        if duration > 3600:  # 3600 seconds = 1 hour
            st.warning("Due to the video duration exceeding 60 minutes, it is currently not supported. Please choose a shorter video.")
            return None

        with st.spinner("Analyzing video..."):
            processor.download_and_convert(force=False)
            processor.transcribe(service='groq', force=False)
            processor.save_transcript()
            processor.summarize(summary_method=summary_method, force=force_summarize)
            processor.save_summary(summary_method)
        
        st.success("Video analysis completed successfully!")
        save_video_info(processor.video_name, youtube_url)
        return processor.video_name
    except Exception as e:
        st.error(f"An error occurred during the analysis process: {str(e)}")
        return None

# Function to display video summary and transcript using stoggle
def display_video_content(video_name, summary_method):
    summary_path = os.path.join(SUMMARY_PATH, f"{video_name}_{summary_method}.txt")
    transcript_path = os.path.join(TRANSCRIPT_PATH, f"{video_name}.txt")
    
    # Display Summary
    summary_content = read_file_content(summary_path)
    stoggle("Summary", summary_content)
    
    # Display Transcript
    transcript_content = read_file_content(transcript_path)
    stoggle("Full Transcript", transcript_content)

# Main app
def main():
    st.set_page_config(layout="wide")
    
    if 'processed_videos' not in st.session_state:
        load_video_info()
    
    st.sidebar.title("Dashboard")
    page = st.sidebar.radio("Navigate", ["New Analysis", "View Summaries"])
    
    if page == "New Analysis":
        st.title("YouTube Video Content Analysis")
        youtube_url = st.text_input("Enter YouTube Video URL:")
        
        # Add summary method selection
        summary_method = st.selectbox(
            "Select Summary Method",
            ["executive", "detailed", "brief"],
            format_func=lambda x: {
                "executive": "執行摘要",
                "detailed": "詳細摘要",
                "brief": "簡短摘要"
            }.get(x, x)
        )
        
        force_summarize = st.checkbox("重新生成摘要")
        
        if st.button("分析影片"):
            if youtube_url:
                video_name = analyze_video(youtube_url, summary_method, force_summarize=force_summarize)
                if video_name:
                    st.success(f"已完成影片分析: {video_name}")
                    display_video_content(video_name, summary_method)
            else:
                st.warning("請輸入有效的 YouTube 網址。")
    
    elif page == "View Summaries":
        st.title("Video Summaries")
        if st.session_state.processed_videos:
            selected_video = st.sidebar.selectbox("Select a video", list(st.session_state.processed_videos.keys()))
            if selected_video:
                summary_method = st.selectbox(
                    "Select Summary Method",
                    ["executive", "detailed", "brief"],
                    format_func=lambda x: {
                        "executive": "執行摘要",
                        "detailed": "詳細摘要",
                        "brief": "簡短摘要"
                    }.get(x, x)
                )
                display_video_content(selected_video, summary_method)
        else:
            st.info("No processed videos available. Please analyze a video first.")

if __name__ == "__main__":
    main()