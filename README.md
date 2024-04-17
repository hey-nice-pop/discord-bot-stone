# Discord Bot
サウナから着想を得たDiscord bot
## 機能
### スラッシュコマンド( / )に対応したゲーム
- マインスイーパー
### 指定したチャンネルでのbot応答
- chatGPT
### 投稿数に応じて上昇する温度計と90度で配布されるリワード🌡️
- 昨日の最もリアクションが多い投稿
- YouTubeからランダムなホームビデオを検索

## Installation
- discord.py
- openai(0.28)
- python-dotenv
- filelock
```bash
pip install discord
pip install openai==0.28
pip install python-dotenv
pip install filelock
```

- .env
```.env
BOT_TOKEN = 'YOURTOKEN' # bottoken
OPENAI_API_KEY = 'YOURKEY' # openaikey
RESPONSE_CHANNEL_ID = 123456789 # chatgptを応答させるチャンネル
IGNORED_CATEGORY_ID = 123456789 # 温度上昇を無視するチャンネル
TARGET_THREAD_CHANNEL_ID = 123456789 # 温度上昇を通知するチャンネル
YOUTUBE_KEY = 'YOUTUBEAPIKEY' # youtubekey
```

