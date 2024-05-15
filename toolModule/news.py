import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests

def get_nhk_news():
    news_data = []
    base_url = 'https://www3.nhk.or.jp'
    url = f'{base_url}/news/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  # 追加: エンコーディングをUTF-8に設定
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # トップニュースの取得
        content_header = soup.find('div', class_='content--header')
        if content_header:
            top_news_a_tag = content_header.find('a')
            if top_news_a_tag and 'href' in top_news_a_tag.attrs:
                top_news_title = content_header.find('em', class_='title').text.strip() if content_header.find('em', class_='title') else "タイトルが見つかりません"
                top_news_url = base_url + top_news_a_tag.get('href')
                news_data.append([top_news_title, top_news_url])
        
        # その他のニュース項目の取得
        content_items = soup.find('div', class_='content--items')
        if content_items:
            for dl in content_items.find_all('dl', limit=8):  # 最初の8記事のみ
                a_tag = dl.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    title = dl.find('em', class_='title').text.strip() if dl.find('em', class_='title') else "タイトルが見つかりません"
                    news_url = base_url + a_tag.get('href')
                    news_data.append([title, news_url])
    else:
        news_data.append([f"ウェブサイトへのアクセスに失敗しました。ステータスコード: {response.status_code}"])

    return news_data

async def news_command(interaction: discord.Interaction):
    news_list = get_nhk_news()
    # ニュースリストをチェックし、特別なメッセージ（エラーなど）を処理する
    if len(news_list) == 1 and isinstance(news_list[0], str):
        # ニュースリストに単一の文字列が含まれる場合（エラーメッセージなど）
        await interaction.response.send_message(news_list[0])
    else:
        # 通常のニュースリスト処理
        response = "最新のニュース:\n"
        for item in news_list:
            if isinstance(item, list) and len(item) == 2:
                title, url = item
                response += f"[{title}]({url})\n"
            else:
                response += "ニュースの取得に問題がありました。\n"
        await interaction.response.send_message(response)

def setup(bot: commands.Bot):
    @bot.tree.command(name="news", description="最新ニュースを表示")
    async def news(interaction: discord.Interaction):
        await news_command(interaction)
