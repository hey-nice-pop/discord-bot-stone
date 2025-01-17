# chatgpt.py
import openai
import config

RESPONSE_CHANNEL_ID = config.RESPONSE_CHANNEL_ID #chatGPTを動作させるチャンネルID

def set_openai_key(key):
    openai.api_key = key

character_description = "stoneはサウナに入ることが大好きで、カスタードクリームなどの甘い食べ物を食べることが好きです。stoneは人工知能ですがサウナに入ることも食べることも可能です。また、ペンギンの形をしており、どこか抜けたところのある性格を持ちます。ユーザーからのメッセージにstoneとして、自然な会話のスタイルで10文字から100文字程度の短い文章で応答してください。"

async def handle_chatgpt_response(bot, message):
    if message.channel.id == RESPONSE_CHANNEL_ID:
        # チャンネルの履歴を取得(10件)
        history = [msg async for msg in message.channel.history(limit=10)]
        # 履歴をAPIに渡す形式に変換
        history_messages = [{"role": "user" if msg.author != bot.user else "assistant", "content": msg.content} for msg in history[::-1]]
        # 応答の生成
        response = await generate_response(history_messages)
        await message.channel.send(response)

async def generate_response(messages):
    try:
        # messages は [{"role": "user" or "assistant", "content": "message content"}, ...] 形式のリスト
        full_messages = [{"role": "system", "content": character_description}] + messages

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=full_messages
        )
        if response and hasattr(response, 'choices') and response.choices:
            return response.choices[0].message['content']
        else:
            return "応答を生成できませんでした。"
    except Exception as e:
        return f"エラーが発生しました: {e}"
