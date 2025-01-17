import json
import datetime
import discord
from discord import Message
from filelock import FileLock, Timeout
import config

from temperatureModule.reward import send_90_degree_reward

# 温度を送信するチャンネル
TARGET_THREAD_CHANNEL_ID = config.TARGET_THREAD_CHANNEL_ID

# JSONファイルのパス
JSON_FILE_PATH = 'temperature.json'
LOCK_PATH = 'temperature.json.lock'

async def process_message(message: Message):
    # 対象のスレッドを取得
    target_thread = message.guild.get_channel(TARGET_THREAD_CHANNEL_ID)

    try:
        with FileLock(LOCK_PATH, timeout=5):
            data, new_file_created = load_json()
            
            # JSONファイルが新しく作成された場合に60度の通知を送信
            if new_file_created:
                await target_thread.send('------------------------\n現在のサウナ室温度：🌡️ 60℃\n| 🟧 ⬜ ⬜ ⬜ |')

            # 現在の日付を取得
            today = str(datetime.date.today())

            # 日付が変わった場合の処理
            if data['last_date'] != today:
                # 前日のメッセージ数が15未満の場合は15として扱う
                data['yesterday_message_count'] = max(data['message_count'], 15)
                data['message_count'] = 0
                reset_temperature(data)
                data['last_date'] = today
                await target_thread.send('------------------------\n現在のサウナ室温度：🌡️ 60℃\n| 🟧 ⬜ ⬜ ⬜ |')

            previous_temperature = data['temperature']

            # メッセージ数の更新
            data['message_count'] += 1

            # 前日のメッセージ数を基に温度の上昇量を計算
            temperature_increase = 30 / (max(data['yesterday_message_count'], 1) * 0.8)
            data['temperature'] += temperature_increase

            # 特定の温度を超えた場合のメッセージ送信
            await check_temperature_thresholds(message, data, previous_temperature)

            # JSONファイルにデータを保存
            save_json(data)
    except Timeout as e:
        print(f"ロックの獲得に失敗しました: {e}")
        # 必要に応じて、ここで再試行のロジックを追加する

async def check_temperature_thresholds(message: Message, data: dict, previous_temperature: float):
    # 対象のスレッドを取得
    target_thread = message.guild.get_channel(TARGET_THREAD_CHANNEL_ID)

    thresholds = [70, 80, 90]
    for threshold in thresholds:
        if previous_temperature < threshold <= data['temperature']:
            if threshold == 70:
                await target_thread.send(f'------------------------\n現在のサウナ室温度：🌡️ {threshold}℃\n| 🟧 🟧 ⬜ ⬜ |')
            elif threshold == 80:
                await target_thread.send(f'------------------------\n現在のサウナ室温度：🌡️ {threshold}℃\n| 🟧 🟧 🟧 ⬜ |')
            elif threshold == 90:
                # 90度に達した場合、特別な処理を行う
                await handle_90_degree_threshold(data, message)

async def handle_90_degree_threshold(data: dict, message: Message):
    # 対象のスレッドを取得
    target_thread = message.guild.get_channel(TARGET_THREAD_CHANNEL_ID)

    # 90度に達した場合の特別なメッセージの処理
    if 'last_reward_date' not in data or data['last_reward_date'] != str(datetime.date.today()):
        await send_90_degree_reward(TARGET_THREAD_CHANNEL_ID, message.guild, datetime.date.today() - datetime.timedelta(days=1))
        data['last_reward_date'] = str(datetime.date.today())
    # 以下、90度に達した際に60度にリセットする
    #else:
    #    await target_thread.send('------------------------\n現在のサウナ室温度：🌡️ 90℃\n| 🟧 🟧 🟧 🟧 |\n※90℃を超えましたが、本日の拾い物は受取済みです。')
    
    #reset_temperature(data)
    #await target_thread.send('------------------------\n温度がリセットされました\n現在のサウナ室温度：🌡️ 60℃\n| 🟧 ⬜ ⬜ ⬜ |')

def reset_temperature(data: dict):
    data['temperature'] = 60
    for threshold in [70, 80, 90]:
        data[f'notified_{threshold}'] = False

def load_json():
    new_file_created = False
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file), new_file_created
    except FileNotFoundError:
        # ファイルが存在しない場合は初期データを作成し、新ファイル作成フラグをTrueに設定
        new_file_created = True
        initial_data = {'temperature': 60, 'message_count': 0, 'yesterday_message_count': 15, 'last_date': str(datetime.date.today()), 'last_reward_date': ''}
        save_json(initial_data)
        return initial_data, new_file_created

def save_json(data):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

#温度表示コマンド
async def send_current_temperature(interaction: discord.Interaction):
    # JSONファイルから現在の温度を読み込む
    data, _ = load_json()  # new_file_created フラグは無視
    current_temperature = round(data['temperature'], 1)  # 小数点第一位で四捨五入

    # メッセージを送信し、ephemeral=True を指定して本人にのみ表示
    await interaction.response.send_message(f'現在のサウナ室温度は 🌡️ {current_temperature}℃ です。', ephemeral=True)

def setup(bot):
    @bot.tree.command(name='show_temperature', description='現在のサウナ室温度を表示します')
    async def show_temperature(interaction: discord.Interaction):
        await send_current_temperature(interaction)