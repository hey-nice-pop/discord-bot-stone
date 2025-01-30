from dotenv import load_dotenv
load_dotenv()

import os

BOT_TOKEN = os.getenv('BOT_TOKEN')#bottoken
RESPONSE_CHANNEL_ID = int(os.getenv('RESPONSE_CHANNEL_ID'))#chatgpt応答チャンネル
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')#chatgptkey
IGNORED_CATEGORY_ID = int(os.getenv('IGNORED_CATEGORY_ID'))#温度上昇を無視するカテゴリ
TARGET_THREAD_CHANNEL_ID = int(os.getenv('TARGET_THREAD_CHANNEL_ID'))#温度上昇を通知するチャンネル
YOUTUBE_KEY = os.getenv('YOUTUBE_KEY') #youtubeAPIkey