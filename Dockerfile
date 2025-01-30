# ベースイメージとして軽量な Python を使用
FROM python:3.10-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコンテナにコピー
COPY requirements.txt .

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーション全体をコンテナにコピー
COPY . .

# デフォルトのコマンドは docker-compose.yml で指定しているため、CMD は不要