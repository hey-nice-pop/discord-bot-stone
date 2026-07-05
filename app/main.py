import asyncio
import discord
from discord.ext import commands
import config
import logging

# ログの基本設定（INFOレベル以上を表示）
logging.basicConfig(level=logging.INFO)

# マインスイーパー機能
import gameModule.minesweeper as minesweeper
# wikipedia
import toolModule.wiki as wiki
# weather
import toolModule.weather as weather
# 現在の温度表示機能
import temperatureModule.temperature as temperature
from temperatureModule.temperature import process_message
# ChatGPT関連
from chatgptModule.chatgpt import set_openai_key, handle_chatgpt_response

YOUR_BOT_TOKEN = config.BOT_TOKEN
IGNORED_CATEGORY_ID = config.IGNORED_CATEGORY_ID  # 温度上昇を無視するカテゴリのID
OPENAI_API_KEY = config.OPENAI_API_KEY
set_openai_key(OPENAI_API_KEY)

# インテントを有効化
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix='/',
    intents=intents,
    sync_commands=True,
    activity=discord.Game("水風呂")
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"ログイン完了: {bot.user}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    # コマンド実行時のエラーは全員に通知
    message = "コマンドの実行中にエラーが発生しました。時間をおいて再度お試しください。"
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=False)
    else:
        await interaction.response.send_message(message, ephemeral=False)
    logging.exception("App command error: %s", error)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ChatGPT応答処理
    await handle_chatgpt_response(bot, message)

    # 温度更新処理（指定カテゴリを無視）
    if message.channel.category_id != IGNORED_CATEGORY_ID:
        await process_message(message)

    # その他のコマンド処理
    await bot.process_commands(message)

async def main():
    async with bot:
        # 同期的なモジュールの初期化
        minesweeper.setup(bot)
        wiki.setup(bot)
        weather.setup(bot)
        temperature.setup(bot)
        # 非同期に recommendation モジュール（cog）を読み込む
        await bot.load_extension("recommendationModule.recommendation")
        await bot.start(YOUR_BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Botが Ctrl+C により停止しました。")
