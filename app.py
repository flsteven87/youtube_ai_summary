import streamlit as st
import os
from video_processor import VideoProcessor
from config.settings import TRANSCRIPT_PATH, SUMMARY_PATH
import json
from collections import OrderedDict
import markdown
from streamlit_extras.stylable_container import stylable_container

# 設置 Streamlit 的端口
port = int(os.environ.get("PORT", 5000))

st.set_page_config(layout="wide")

# 使用 Streamlit secrets
# OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"讀取檔案時發生錯誤: {str(e)}"

def save_video_info(video_name, youtube_url, summary_method, summary_language, model):
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = OrderedDict()
    
    video_key = f"{video_name}_{summary_method}_{summary_language}_{model}"
    st.session_state.processed_videos = OrderedDict([(video_key, youtube_url)] + list(st.session_state.processed_videos.items()))
    
    with open('processed_videos.json', 'w') as f:
        json.dump(list(st.session_state.processed_videos.items()), f)

def load_video_info():
    if os.path.exists('processed_videos.json'):
        with open('processed_videos.json', 'r') as f:
            video_list = json.load(f)
            st.session_state.processed_videos = OrderedDict(video_list)
    else:
        st.session_state.processed_videos = OrderedDict()

def create_progress_bar():
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    return progress_bar, status_text

def update_progress(progress_bar, status_text, step, total_steps):
    progress = int(step / total_steps * 100)
    progress_bar.progress(progress)
    status_text.text(f"總體進度: {progress}%")

def analyze_video(youtube_url, summary_method, video_language, summary_language, model, user_api_key=None, force_summarize=False):
    try:
        processor = VideoProcessor(youtube_url)
        
        duration = processor.get_video_duration()
        if duration > 3600:
            st.warning("由於影片時長超過60分鐘，目前不支援。請選擇較短的影片。")
            return None

        with stylable_container(
            key="progress_container",
            css_styles="""
                {
                    background-color: #2b2b2b;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                }
            """
        ):
            st.markdown("### 分析進度")
            progress_bar, status_text = create_progress_bar()
            total_steps = 4  # 總步驟數
            
            # 下載並轉換影片
            update_progress(progress_bar, status_text, 1, total_steps)
            processor.download_and_convert(force=False)
            
            # 轉錄影片
            update_progress(progress_bar, status_text, 2, total_steps)
            transcribe_language = 'zh' if video_language.startswith('zh') else video_language
            processor.transcribe(service='groq', force=False, language=transcribe_language)
            
            # 保存轉錄文本
            update_progress(progress_bar, status_text, 3, total_steps)
            processor.save_transcript()
            
            # 生成摘要
            update_progress(progress_bar, status_text, 4, total_steps)
            if model == "gpt-4o" and user_api_key:
                processor.summarize(summary_method=summary_method, force=force_summarize, language=summary_language, model=model, api_key=user_api_key)
            else:
                processor.summarize(summary_method=summary_method, force=force_summarize, language=summary_language, model=model)
            processor.save_summary(summary_method, language=summary_language, model=model)
        
        st.success("影片分析成功完成！")
        save_video_info(processor.video_name, youtube_url, summary_method, summary_language, model)
        return processor.video_name
    except Exception as e:
        st.error(f"分析過程中發生錯誤: {str(e)}")
        return None

def display_video_content(video_name, summary_method, language, model):
    summary_path = os.path.join(SUMMARY_PATH, f"{video_name}_{summary_method}_{language}_{model}.txt")
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

def custom_language_selector(key_prefix, default_language='zh-tw'):
    languages = {
        "繁體中文": "zh-tw",
        "简体中文": "zh-cn",
        "English": "en",
        "日本語": "ja",
        "한국어": "ko",
        "Français": "fr",
        "Deutsch": "de",
        "Español": "es"
    }
    
    if f'{key_prefix}_selected_language' not in st.session_state:
        st.session_state[f'{key_prefix}_selected_language'] = default_language

    selected_language = st.selectbox(
        f"選擇{key_prefix}語言",
        options=list(languages.keys()),
        format_func=lambda x: x,
        key=f"{key_prefix}_language_selector"
    )
    
    return languages[selected_language]

def custom_model_selector():
    models = {
        "GPT-4o-mini": "gpt-4o-mini",
        "GPT-4o": "gpt-4o",
    }
    
    selected_model = st.selectbox(
        "選擇模型",
        options=list(models.keys()),
        index=0,  # 設置 GPT-4o-mini 為預設選項
        format_func=lambda x: x,
        key="model_selector"
    )
    
    if models[selected_model] == "gpt-4o":
        user_api_key = st.text_input("請輸入您的 OpenAI API Key", type="password")
        return models[selected_model], user_api_key
    else:
        return models[selected_model], None

def display_new_analysis_page():
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.title("YouTube Summarizer")
        youtube_url = st.text_input(
            "YouTube URL",
            label_visibility="collapsed",
            placeholder="輸入 YouTube 影片網址",
            key="youtube_url"
        )
        
        # 將語言選擇和模型選擇放在同一行
        col1, col2, col3 = st.columns(3)
        with col1:
            video_language = custom_language_selector("影片")
        with col2:
            summary_language = custom_language_selector("總結")
        with col3:
            selected_model, user_api_key = custom_model_selector()
        
        # 只保留詳細摘要按鈕
        if st.button(
            "生成詳細摘要",
            key="btn_detailed",
            use_container_width=True,
            help="生成詳細摘要"
        ):
            analyze_and_display(youtube_url, "detailed", video_language, summary_language, selected_model, user_api_key)
        
        st.markdown(
            '<div style="width:100%;height:3px;background-color:#9C27B0;"></div>',
            unsafe_allow_html=True
        )
        
        st.session_state.force_summarize = False

def analyze_and_display(youtube_url, summary_method, video_language, summary_language, model, user_api_key):
    if youtube_url:
        if model == "gpt-4o" and not user_api_key:
            st.warning("請輸入您的 OpenAI API Key 以使用 GPT-4o 模型。")
            return
        
        video_name = analyze_video(youtube_url, summary_method, video_language, summary_language, model, user_api_key, force_summarize=st.session_state.force_summarize)
        if video_name:
            st.success(f"已完成影片分析: {video_name}")
            save_video_info(video_name, youtube_url, summary_method, summary_language, model)
            st.session_state.current_page = "View Summary"
            st.session_state.selected_video = f"{video_name}_{summary_method}_{summary_language}_{model}"
            st.rerun()
    else:
        st.warning("請輸入有效的 YouTube 網址。")

def get_summary_method_name(method):
    return "詳細摘要"

def set_selected_video(video_key):
    st.session_state.current_page = "View Summary"
    st.session_state.selected_video = video_key

def display_summary_page():
    if 'selected_video' in st.session_state and st.session_state.selected_video:
        video_name, summary_method, summary_language, model = st.session_state.selected_video.rsplit('_', 3)
        
        st.title(f"{video_name}")
        st.subheader(f"摘要方法: {get_summary_method_name(summary_method)}")
        st.subheader(f"摘要語言: {get_language_name(summary_language)}")
        st.subheader(f"使用模型: {model}")
        
        display_video_content(video_name, summary_method, summary_language, model)
    else:
        st.warning("請先選擇一個視頻進行分析。")

def get_available_languages(video_name, summary_method):
    available_languages = []
    for language in ["zh-tw", "zh-cn", "en", "ja", "ko", "fr", "de", "es"]:
        if os.path.exists(os.path.join(SUMMARY_PATH, f"{video_name}_{summary_method}_{language}.txt")):
            available_languages.append(language)
    return available_languages

def get_language_name(language_code):
    language_names = {
        "zh-tw": "繁體中文",
        "zh-cn": "简体中文",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español"
    }
    return language_names.get(language_code, language_code)

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
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        .stProgress {
            background-color: #1e1e1e;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }
        .stProgress > div {
            height: 100%;
            width: 100%;
            background-color: #4CAF50 !important;
        }
        .stProgress > div > div {
            height: 100%;
        }
        .stProgress > div > div > div {
            height: 100%;
        }
        .stInfo, .stSuccess, .stError, .stWarning {
            padding: 10px;
            border-radius: 5px;
            color: #e0e0e0;
            margin-bottom: 10px;
        }
        .stInfo {
            background-color: #1e3a5f;
        }
        .stSuccess {
            background-color: #1e5f1e;
        }
        .stError {
            background-color: #5f1e1e;
        }
        .stWarning {
            background-color: #5f4b1e;
        }
        body {
            color: #e0e0e0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
        }
        .stTextInput > div > div > input {
            color: #e0e0e0;
            background-color: #3a3a3a;
        }
        .stSelectbox > div > div > select {
            color: #e0e0e0;
            background-color: #3a3a3a;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if 'processed_videos' not in st.session_state:
        load_video_info()
    
    # 初始化 current_page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "New Analysis"
    
    st.sidebar.title("Summaries")
    
    if st.sidebar.button("新增分析", use_container_width=True):
        st.session_state.current_page = "New Analysis"
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("已分析的影片")
    
    button_colors = {
        "detailed": "#9C27B0"
    }
    
    for video_key, youtube_url in st.session_state.processed_videos.items():
        video_name, summary_method, summary_language, model = video_key.rsplit('_', 3)
        button_color = button_colors.get(summary_method, "#808080")
        
        if st.sidebar.button(
            f"📺 {video_name} ({get_summary_method_name(summary_method)} - {get_language_name(summary_language)} - {model})",
            key=video_key,
            use_container_width=True,
            type="secondary",
            help=f"查看 {video_name} 的 {get_summary_method_name(summary_method)} ({get_language_name(summary_language)})",
            on_click=set_selected_video,
            args=(video_key,)
        ):
            pass
        
        st.sidebar.markdown(
            f'<div class="sidebar-color-line" style="width:100%;height:3px;background-color:{button_color};"></div>',
            unsafe_allow_html=True
        )

    if st.session_state.current_page == "New Analysis":
        display_new_analysis_page()
    elif st.session_state.current_page == "View Summary":
        display_summary_page()

if __name__ == "__main__":
    main()

    # heroku ps:scale web=0 -a youtube-ai-summary