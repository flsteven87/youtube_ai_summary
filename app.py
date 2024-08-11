import streamlit as st
import os
from video_processor import VideoProcessor
from config.settings import TRANSCRIPT_PATH, SUMMARY_PATH
import json
from collections import OrderedDict
import markdown

st.set_page_config(layout="wide")

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"讀取檔案時發生錯誤: {str(e)}"

def save_video_info(video_name, youtube_url):
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = OrderedDict()
    
    video_name = video_name.rstrip('_')
    st.session_state.processed_videos = OrderedDict([(video_name, youtube_url)] + list(st.session_state.processed_videos.items()))
    
    with open('processed_videos.json', 'w') as f:
        json.dump(list(st.session_state.processed_videos.items()), f)

def load_video_info():
    if os.path.exists('processed_videos.json'):
        with open('processed_videos.json', 'r') as f:
            video_list = json.load(f)
            st.session_state.processed_videos = OrderedDict(video_list)
    else:
        st.session_state.processed_videos = OrderedDict()

def analyze_video(youtube_url, summary_method, force_summarize=False):
    try:
        processor = VideoProcessor(youtube_url)
        
        duration = processor.get_video_duration()
        if duration > 3600:
            st.warning("由於影片時長超過60分鐘，目前不支援。請選擇較短的影片。")
            return None

        with st.spinner("正在分析影片..."):
            processor.download_and_convert(force=False)
            processor.transcribe(service='groq', force=False)
            processor.save_transcript()
            processor.summarize(summary_method=summary_method, force=force_summarize)
            processor.save_summary(summary_method)
        
        st.success("影片分析成功完成！")
        save_video_info(processor.video_name, youtube_url)
        return processor.video_name
    except Exception as e:
        st.error(f"分析過程中發生錯誤: {str(e)}")
        return None

def display_video_content(video_name, summary_method):
    summary_path = os.path.join(SUMMARY_PATH, f"{video_name}_{summary_method}.txt")
    transcript_path = os.path.join(TRANSCRIPT_PATH, f"{video_name}.txt")
    
    st.subheader("影片摘要")
    summary_content = read_file_content(summary_path)
    html_content = markdown.markdown(summary_content)
    st.markdown(f"""
    <div style="background-color: #2e2e2e; color: #ffffff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <div style="font-size: 16px; line-height: 1.6;">{html_content}</div>
    </div>
    """, unsafe_allow_html=True)
    
    transcript_content = read_file_content(transcript_path)
    with st.expander("查看完整文字稿"):
        st.text_area("", transcript_content, height=300)

def main():
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] div[data-testid="column"] div.stButton > button {
            width: 100%;
            border: none;
            font-weight: bold;
            margin-bottom: 0px;
        }
        div[data-testid="stHorizontalBlock"] div[data-testid="column"] div.stButton + div {
            margin-top: 0px;
        }
        .sidebar-video-button {
            margin-bottom: 0px !important;
        }
        .sidebar-color-line {
            margin-top: 0px !important;
            margin-bottom: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if 'processed_videos' not in st.session_state:
        load_video_info()
    
    st.sidebar.title("Summaries")
    
    if st.sidebar.button("新增分析", use_container_width=True):
        st.session_state.current_page = "New Analysis"
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("已分析的影片")
    
    button_colors = {
        "brief": "#4CAF50",
        "executive": "#2196F3",
        "detailed": "#9C27B0"
    }
    
    for video_name, youtube_url in st.session_state.processed_videos.items():
        summary_method = get_summary_method(video_name)
        button_color = button_colors.get(summary_method, "#808080")
        
        if st.sidebar.button(
            f"📺 {video_name}",
            key=video_name,
            use_container_width=True,
            type="secondary",
            help=f"查看 {video_name} 的摘要",
            on_click=lambda vn=video_name: set_selected_video(vn)
        ):
            pass
        
        st.sidebar.markdown(
            f'<div class="sidebar-color-line" style="width:100%;height:3px;background-color:{button_color};"></div>',
            unsafe_allow_html=True
        )

    if not hasattr(st.session_state, 'current_page'):
        st.session_state.current_page = "New Analysis"
    
    if st.session_state.current_page == "New Analysis":
        display_new_analysis_page()
    elif st.session_state.current_page == "View Summary":
        display_summary_page()

def display_new_analysis_page():
    
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.title("YouTube Summarizer")
        youtube_url = st.text_input("", placeholder="輸入 YouTube 影片網址", key="youtube_url")
        
        button_styles = {
            "brief": {"label": "簡短摘要", "color": "#4CAF50"},
            "executive": {"label": "執行摘要", "color": "#2196F3"},
            "detailed": {"label": "詳細摘要", "color": "#9C27B0"}
        }
        
        col1, col2, col3 = st.columns(3)
        
        for method, style in button_styles.items():
            col = [col1, col2, col3][list(button_styles.keys()).index(method)]
            if col.button(
                style["label"],
                key=f"btn_{method}",
                use_container_width=True,
                help=f"生成{style['label']}"
            ):
                analyze_and_display(youtube_url, method)
            
            col.markdown(
                f'<div style="width:100%;height:3px;background-color:{style["color"]};"></div>',
                unsafe_allow_html=True
            )
        
        force_summarize = st.checkbox("重新生成摘要")
        st.session_state.force_summarize = force_summarize

def analyze_and_display(youtube_url, summary_method):
    if youtube_url:
        video_name = analyze_video(youtube_url, summary_method, force_summarize=st.session_state.force_summarize)
        if video_name:
            st.success(f"已完成影片分析: {video_name}")
            st.session_state.current_page = "View Summary"
            st.session_state.selected_video = video_name
            st.session_state.selected_summary_method = summary_method  # 保存所選的摘要方法
            st.rerun()
    else:
        st.warning("請輸入有效的 YouTube 網址。")

def get_summary_method(video_name):
    for method in ["brief", "executive", "detailed"]:
        if os.path.exists(os.path.join(SUMMARY_PATH, f"{video_name}_{method}.txt")):
            return method
    return "unknown"

def set_selected_video(video_name):
    st.session_state.current_page = "View Summary"
    st.session_state.selected_video = video_name

def display_summary_page():
    if hasattr(st.session_state, 'selected_video'):
        video_name = st.session_state.selected_video
        st.title(f"{video_name}")
        
        # 使用保存的摘要方法作為預設值
        default_method = st.session_state.get('selected_summary_method', 'brief')
        
        summary_method = st.selectbox(
            "選擇摘要方法",
            ["brief", "executive", "detailed"],
            format_func=lambda x: {
                "brief": "簡短摘要",
                "executive": "執行摘要",
                "detailed": "詳細摘要"
            }.get(x, x),
            key="summary_method_selector",
            index=["brief", "executive", "detailed"].index(default_method)
        )
        
        # 更新選擇的摘要方法
        st.session_state.selected_summary_method = summary_method
        
        display_video_content(video_name, summary_method)
    else:
        st.info("請先選一個已分析的影片。")

if __name__ == "__main__":
    main()