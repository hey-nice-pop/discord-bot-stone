# recommendationModule/recommendation.py
import discord
from discord.ext import commands
import config

class Recommendation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Bot自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            return

        # 対象のリアクション絵文字が config.RECOMMENDATION_EMOJI 以外は無視
        if payload.emoji.name != config.RECOMMENDATION_EMOJI:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel(payload.channel_id)
        if channel is None:
            try:
                channel = await guild.fetch_channel(payload.channel_id)
            except Exception as e:
                print("チャンネル取得エラー:", e)
                return

        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            print("メッセージ取得エラー:", e)
            return

        # 自分自身の投稿へのリアクションは無視
        if message.author.id == payload.user_id:
            return

        # 重ね押しチェック
        target_reaction = None
        for reaction in message.reactions:
            if isinstance(reaction.emoji, str):
                if reaction.emoji == config.RECOMMENDATION_EMOJI:
                    target_reaction = reaction
                    break
            else:
                if reaction.emoji.name == config.RECOMMENDATION_EMOJI:
                    target_reaction = reaction
                    break
        if target_reaction is not None and target_reaction.count > 1:
            return

        # 元の投稿リンクを作成
        original_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

        # DM用Embedの作成（投稿リンク、推薦者情報を追加）
        dm_embed = discord.Embed(
            title="[lsbhb]投稿内容の確認",
            description=(
                "あなたの投稿が推薦されました！SNSに投稿の許可はいただけますでしょうか？\n"
                "回答期限はこのDMから1日で、回答なしの場合『拒否』となります。\n"
                "許可後もSTAFFへDMすることで拒否可能です。"
            ),
            color=discord.Color.blue()
        )
        dm_embed.add_field(
            name="投稿内容",
            value=message.content if message.content else "なし",
            inline=False
        )
        dm_embed.add_field(
            name="投稿リンク",
            value=f"[こちら]({original_link})",
            inline=False
        )
        # 推薦者情報の追加
        recommender = guild.get_member(payload.user_id)
        if recommender:
            dm_embed.add_field(
                name="推薦者",
                value=recommender.mention,
                inline=True
            )
        dm_embed.set_footer(text="下のボタンで『承諾』または『拒否』を選択してください。")

        view = RecommendationView(message, self.bot, recommender)
        try:
            await message.author.send(embed=dm_embed, view=view)
        except discord.Forbidden:
            print(f"{message.author} にDMを送信できませんでした (Forbidden)")
        except Exception as e:
            print("DM送信エラー:", e)

class RecommendationView(discord.ui.View):
    def __init__(self, original_message: discord.Message, bot: commands.Bot, recommender: discord.Member):
        super().__init__(timeout=86400)  # タイムアウトは1日
        self.original_message = original_message
        self.bot = bot
        self.recommender = recommender

    @discord.ui.button(label="承諾", style=discord.ButtonStyle.success)
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        result_embed = discord.Embed(
            title="投稿承諾",
            description=self.original_message.content,
            color=discord.Color.green()
        )
        result_embed.add_field(name="選択", value="承諾", inline=False)
        original_link = f"https://discord.com/channels/{self.original_message.guild.id}/{self.original_message.channel.id}/{self.original_message.id}"
        result_embed.add_field(name="投稿リンク", value=f"[こちら]({original_link})", inline=False)
        result_embed.add_field(name="推薦者", value=self.recommender.mention, inline=True)
        result_embed.set_author(
            name=self.original_message.author.display_name,
            icon_url=(self.original_message.author.avatar.url if self.original_message.author.avatar else None)
        )

        target_channel = self.bot.get_channel(int(config.RECOMMENDATION_CHANNEL_ID))
        if target_channel:
            await target_channel.send(embed=result_embed)
        else:
            print("指定されたチャンネルが見つかりません。")
        # DMなので ephemeral フラグは不要
        await interaction.response.send_message("承諾が選択されました。\nご協力ありがとうございます！")
        self.stop()

    @discord.ui.button(label="拒否", style=discord.ButtonStyle.danger)
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        result_embed = discord.Embed(
            title="投稿拒否",
            description=self.original_message.content,
            color=discord.Color.red()
        )
        result_embed.add_field(name="選択", value="拒否", inline=False)
        original_link = f"https://discord.com/channels/{self.original_message.guild.id}/{self.original_message.channel.id}/{self.original_message.id}"
        result_embed.add_field(name="投稿リンク", value=f"[こちら]({original_link})", inline=False)
        result_embed.add_field(name="推薦者", value=self.recommender.mention, inline=True)
        result_embed.set_author(
            name=self.original_message.author.display_name,
            icon_url=(self.original_message.author.avatar.url if self.original_message.author.avatar else None)
        )

        target_channel = self.bot.get_channel(int(config.RECOMMENDATION_CHANNEL_ID))
        if target_channel:
            await target_channel.send(embed=result_embed)
        else:
            print("指定されたチャンネルが見つかりません。")
        await interaction.response.send_message("拒否が選択されました。")
        self.stop()

async def setup(bot: commands.Bot):
    await bot.add_cog(Recommendation(bot))