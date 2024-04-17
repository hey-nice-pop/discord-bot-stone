import datetime
import discord
import requests
import random
import config

IGNORED_CATEGORY_ID = config.IGNORED_CATEGORY_ID  # 温度上昇を無視するカテゴリのID

# YouTube Data APIのエンドポイントとAPIキー
YOUTUBE_SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_KEY = config.YOUTUBE_KEY  # APIキーを設定

def generate_random_keyword():
    # "DSC"または"IMG"にランダムな4桁の数字を追加
    prefix = random.choice(["DSC", "IMG"])
    random_number = f"{random.randint(0, 9999):04d}"  # 4桁の数字を生成
    return prefix + random_number

async def get_random_youtube_video_url():
    query = generate_random_keyword()
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 50,
        'key': YOUTUBE_KEY
    }
    response = requests.get(YOUTUBE_SEARCH_API_URL, params=params)
    if response.status_code != 200:
        print(f"APIエラー: {response.status_code}")
        print(response.text)
        return None
    videos = response.json().get('items', [])

    if videos:
        selected_video = random.choice(videos)
        video_id = selected_video['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"

    return None


async def get_most_reacted_post(guild: discord.Guild, date):
    most_reacted_post = None
    max_reactions = 0

    start_of_day = datetime.datetime.combine(date, datetime.time.min)
    end_of_day = datetime.datetime.combine(date, datetime.time.max)

    for channel in guild.text_channels:
        # 無視するカテゴリIDのチェックを追加
        if channel.category_id == IGNORED_CATEGORY_ID:
            continue  # このチャンネルは無視するカテゴリーに属しているのでスキップ

        try:
            async for message in channel.history(limit=100, after=start_of_day, before=end_of_day):
                total_reactions = sum(reaction.count for reaction in message.reactions)
                if total_reactions > max_reactions:
                    most_reacted_post = message
                    max_reactions = total_reactions
        except Exception as e:
            print(f"チャンネル {channel.name} の履歴取得中にエラー: {e}")

    return most_reacted_post


async def send_90_degree_reward(channel_id: int, guild: discord.Guild, date):
    channel = guild.get_channel(channel_id)
    if not channel:
        print(f"チャンネルID {channel_id} が見つかりません。")
        return

    youtube_video_url = await get_random_youtube_video_url()

    most_reacted_post = await get_most_reacted_post(guild, date)
    if most_reacted_post:
        post_url = most_reacted_post.jump_url
        await channel.send(f'------------------------\n@here\n現在のサウナ室温度：🌡️ 90℃\n| 🟧 🟧 🟧 🟧 |\n\nstoneがととのいました\n### 最近のHOTな投稿\n- {post_url}\n### stoneの拾い物\n- {youtube_video_url}')
    else:
        await channel.send('------------------------\n現在のサウナ室温度：🌡️ 90℃\n| 🟧 🟧 🟧 🟧 |\n※90℃に達しましたが、前日の投稿は見つかりませんでした。')