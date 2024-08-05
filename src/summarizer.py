import os
import logging
from openai import OpenAI
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

# 載入環境變量
load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables.")
    raise ValueError("OPENAI_API_KEY is not set")

client = OpenAI()

class GPT4Summarizer:
    def __init__(self):
        logger.info("Initializing GPT-4 Summarizer")
        self.user_prompt_path = "src/prompts/summary2.txt"
        self.load_user_prompt()

    def load_user_prompt(self):
        logger.info(f"Loading user prompt from {self.user_prompt_path}")
        try:
            with open(self.user_prompt_path, "r") as file:
                self.user_prompt = file.read()
            logger.info("User prompt loaded successfully")
        except FileNotFoundError:
            logger.error(f"User prompt file not found: {self.user_prompt_path}")
            raise
        except IOError as e:
            logger.error(f"Error reading user prompt file: {str(e)}")
            raise

    def summarize_with_gpt4(self, transcript):
        logger.info("Starting GPT-4 summarization process")
        logger.info(f"Transcript length: {len(transcript)} characters")
        language_prompt = "請你將你的總結，以繁體中文 language:zh-tw\n 輸出"

        try:
            logger.info("Sending request to OpenAI API")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self.user_prompt + language_prompt + "transcript:" + transcript},    
                ],
                temperature=0.2
            )
            logger.info("Received response from OpenAI API")

            summary = response.choices[0].message.content
            logger.info(f"Summary generated. Length: {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"Error during GPT-4 summarization: {str(e)}")
            raise

def summarize_text(text, method="gpt-4"):
    logger.info(f"Starting summarization using method: {method}")

    if method == "gpt-4":
        summarizer = GPT4Summarizer()
        summary = summarizer.summarize_with_gpt4(text)
    else:
        logger.error(f"Unsupported summarization method: {method}")
        raise ValueError(f"Unsupported summarization method: {method}")

    logger.info("Summarization completed")
    return summary

if __name__ == "__main__":
    # 測試代碼
    test_text = "這是一個測試文本，用於演示摘要功能。" * 50
    summary = summarize_text(test_text)
    logger.info(f"Summary preview: {summary[:200]}...")  # 顯示前200個字符作為預覽