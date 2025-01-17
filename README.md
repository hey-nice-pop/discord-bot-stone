# Discord Bot
サウナから着想を得たDiscord bot

## 機能
### スラッシュコマンド( / )に対応したゲーム
- マインスイーパー
### 指定したチャンネルでのbot応答
- openAI
### 投稿数に応じて上昇する温度計と90度で配布されるリワード🌡️
- 昨日の最もリアクションが多い投稿
- YouTubeからランダムなホームビデオを検索
### ニュース
### 日本の天気予報
### wikipedia検索

## Installation
.envのコピー、コピー後に各自.envの値を調整

```cp app/.env.example app/.env```

dockerにてコンテナ・botをバックグラウンド起動

```docker compose up -d```

コンテナをたおす

```docker compose down```

起動中のコンテナに入る

```docker exec -it stone /bin/bash```

起動中のbotのリアルタイムログを確認する

```docker compose logs -f stone```