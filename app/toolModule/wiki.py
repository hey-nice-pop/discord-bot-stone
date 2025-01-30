import discord
from discord.ext import commands
import wikipedia

wikipedia.set_lang('ja')

async def wiki_search(interaction: discord.Interaction, keyword: str):
    search_results = wikipedia.search(keyword, results=10)
    if not search_results:
        await interaction.response.send_message("申し訳ありません、関連するページは見つかりませんでした。", ephemeral=False)
        return

    class WikiSelect(discord.ui.Select):
        def __init__(self, options, **kwargs):
            super().__init__(placeholder="結果から選択してください...", options=options, **kwargs)

        async def callback(self, interaction: discord.Interaction):
            # インタラクションの処理を開始する前に defer を呼び出す
            await interaction.response.defer(ephemeral=False)

            selected_value = self.values[0]  # 選択された値を取得
            try:
                page = wikipedia.page(selected_value)
                summary = page.summary[:1000] + "..."
                # defer した後は followup.send を使用
                await interaction.followup.send(f"**{page.title}**\n{summary}\n詳細: {page.url}", ephemeral=False)
            except wikipedia.exceptions.DisambiguationError as e:
                disambiguation_url = "https://ja.wikipedia.org/wiki/" + selected_value.replace(" ", "_")
                message = f"'{selected_value}'には複数の意味があります。詳細はこちらをご覧ください: {disambiguation_url}"
                await interaction.followup.send(message, ephemeral=False)

    options = [
        discord.SelectOption(label=result, description=f"「{result}」のページを表示", value=result)
        for result in search_results
    ]
    select = WikiSelect(options=options)
    view = discord.ui.View(timeout=600)  # ここでタイムアウトを10分に設定
    view.add_item(select)

    await interaction.response.send_message("以下の結果から選択してください:", view=view, ephemeral=False)

def setup(bot):
    @bot.tree.command(name="wiki", description="Wikipediaを検索")
    async def wiki(interaction: discord.Interaction, keyword: str):
        await wiki_search(interaction, keyword)
