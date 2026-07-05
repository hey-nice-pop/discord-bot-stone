# Discord Bot「stone」

サウナから着想を得たDiscord bot

## 機能

### スラッシュコマンド（`/`）に対応したゲーム
- マインスイーパー

### 指定したチャンネルでのbot応答
- OpenAI（ChatGPT）による自動応答

### 投稿数に応じて上昇する温度計と90℃で配布されるリワード🌡️
- 前日の最もリアクションが多い投稿を紹介
- YouTubeからランダムなホームビデオを検索して紹介

### 投稿推薦機能
- 指定した絵文字でリアクションすると、投稿者にSNS転載可否をDMで確認
- 投稿者が承諾/拒否をボタンで選択すると、指定チャンネルへ結果を通知

### 日本の天気予報

### Wikipedia検索

## 技術スタック
- Python 3.10
- [discord.py](https://github.com/Rapptz/discord.py)
- OpenAI API（`openai==0.28`）
- requests（外部API連携）
- Docker / Docker Compose

## ディレクトリ構成
```
app/
├── main.py                  # エントリーポイント、各モジュールの読み込み
├── config.py                 # .env の値を読み込む設定モジュール
├── gameModule/                # マインスイーパー
├── chatgptModule/             # ChatGPT応答
├── temperatureModule/         # 温度計・90℃リワード
├── recommendationModule/      # 投稿推薦機能
└── toolModule/                 # 天気予報・Wikipedia検索
```

## 環境構築
1 .envのコピー、コピー後に各自.env内の値を調整(BOT_TOKEN必須)

```cp app/.env.example app/.env```

2 dockerにてコンテナ起動

```docker compose up -d```

3 botの起動

```docker exec -it stone python main.py```

※vscodeご利用の場合はdevcontainerから開発コンテナを開いて下記でbot起動

```python main.py```

### 環境変数一覧（`app/.env`）

| 変数名 | 説明 |
| --- | --- |
| `BOT_TOKEN` | Discord bot のトークン（必須） |
| `OPENAI_API_KEY` | OpenAI API キー |
| `RESPONSE_CHANNEL_ID` | ChatGPTが応答するチャンネルID |
| `IGNORED_CATEGORY_ID` | 温度上昇の集計から除外するカテゴリID |
| `TARGET_THREAD_CHANNEL_ID` | 温度上昇を通知するチャンネルID |
| `YOUTUBE_KEY` | YouTube Data API キー（90℃リワードのホームビデオ検索に使用） |
| `RECOMMENDATION_CHANNEL_ID` | 推薦が承諾された投稿を通知するチャンネルID |
| `RECOMMENDATION_EMOJI` | 投稿推薦のトリガーとなるリアクション絵文字 |

### その他コマンド

コンテナをたおす(botの停止)

```docker compose down```

起動中のコンテナに入る

```docker exec -it stone /bin/bash```

起動中のbotのリアルタイムログを確認する

```docker compose logs -f stone```
