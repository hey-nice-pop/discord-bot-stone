import discord
from discord.ext import commands
import config

# マインスイーパー機能
import gameModule.minesweeper as minesweeper

#news
import toolModule.news as news

#wikipedia
import toolModule.wiki as wiki

#weather
import toolModule.weather as weather

# 現在の温度表示機能
import temperatureModule.temperature as temperature
from temperatureModule.temperature import process_message

from chatgptModule.chatgpt import set_openai_key, handle_chatgpt_response

YOUR_BOT_TOKEN = config.BOT_TOKEN
IGNORED_CATEGORY_ID = config.IGNORED_CATEGORY_ID  # 温度上昇を無視するカテゴリのID
OPENAI_API_KEY = config.OPENAI_API_KEY
set_openai_key(OPENAI_API_KEY)

# インテントを有効化
intents = discord.Intents.all()

# Botオブジェクトの生成
bot = commands.Bot(
    command_prefix='/', 
    intents=intents, 
    sync_commands=True,
    activity=discord.Game("水風呂")
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'ログイン完了: {bot.user}')


minesweeper.setup(bot)

temperature.setup(bot)

news.setup(bot)

wiki.setup(bot)

weather.setup(bot)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # ChatGPT応答処理を実行
    await handle_chatgpt_response(bot, message)

    # 温度更新処理を実行
    if message.channel.category_id != IGNORED_CATEGORY_ID:
        await process_message(message)

    # 他のコマンドも処理
    await bot.process_commands(message)

# Discordボットを起動
bot.run(YOUR_BOT_TOKEN)