import discord
from discord.ext import commands
import requests

# 地域名と地域IDのマッピング
regions = {
    "北海道地方": {
        "北海道": "016010",  # 札幌
    },
    "東北地方": {
        "青森県": "020010",  # 青森
        "岩手県": "030010",  # 盛岡
        "宮城県": "040010",  # 仙台
        "秋田県": "050010",  # 秋田
        "山形県": "060010",  # 山形
        "福島県": "070010",  # 福島
    },
    "関東地方": {
        "東京都": "130010",  # 東京
        "神奈川県": "140010",  # 横浜
        "埼玉県": "110010",  # さいたま
        "千葉県": "120010",  # 千葉
        "茨城県": "080010",  # 水戸
        "栃木県": "090010",  # 宇都宮
        "群馬県": "100010",  # 前橋
    },
    "中部地方": {
        "山梨県": "190010",  # 甲府
        "新潟県": "150010",  # 新潟
        "長野県": "200010",  # 長野
        "富山県": "160010",  # 富山
        "石川県": "170010",  # 金沢
        "福井県": "180010",  # 福井
        "愛知県": "230010",  # 名古屋
        "岐阜県": "210010",  # 岐阜
        "静岡県": "220010",  # 静岡
    },
    "近畿地方": {
        "三重県": "240010",  # 津
        "大阪府": "270000",  # 大阪
        "兵庫県": "280010",  # 神戸
        "京都府": "260010",  # 京都
        "滋賀県": "250010",  # 大津
        "奈良県": "290010",  # 奈良
        "和歌山県": "300010",  # 和歌山
    },
    "中国地方": {
        "鳥取県": "310010",  # 鳥取
        "島根県": "320010",  # 松江
        "岡山県": "330010",  # 岡山
        "広島県": "340010",  # 広島
        "山口県": "350020",  # 山口
    },
    "四国地方": {
        "徳島県": "360010",  # 徳島
        "香川県": "370000",  # 高松
        "愛媛県": "380010",  # 松山
        "高知県": "390010",  # 高知
    },
    "九州地方": {
        "福岡県": "400010",  # 福岡
        "大分県": "440010",  # 大分
        "長崎県": "420010",  # 長崎
        "佐賀県": "410010",  # 佐賀
        "熊本県": "430010",  # 熊本
        "宮崎県": "450010",  # 宮崎
        "鹿児島県": "460010",  # 鹿児島
    },
    "沖縄地方": {
        "沖縄県": "471010"   # 那覇
    }
}

# 天気情報を取得する関数
def get_weather_info(region_id):
    url = f'https://weather.tsukumijima.net/api/forecast/city/{region_id}'
    response = requests.get(url)
    data = response.json()
    
    if 'forecasts' not in data:
        return None

    # 今日と明日の天気情報を取得
    today = data['forecasts'][0]
    tomorrow = data['forecasts'][1]

    weather_info = {
        'location': data['location']['city'],
        'today': {
            'date': today['date'],
            'weather': today['telop'],
            'high_temp': today['temperature']['max']['celsius'] if today['temperature']['max'] else 'N/A',
            'low_temp': today['temperature']['min']['celsius'] if today['temperature']['min'] else 'N/A',
            'precip_morning': today['chanceOfRain']['T06_12'] if 'T06_12' in today['chanceOfRain'] else 'N/A',
            'precip_afternoon': today['chanceOfRain']['T12_18'] if 'T12_18' in today['chanceOfRain'] else 'N/A'
        },
        'tomorrow': {
            'date': tomorrow['date'],
            'weather': tomorrow['telop'],
            'high_temp': tomorrow['temperature']['max']['celsius'] if tomorrow['temperature']['max'] else 'N/A',
            'low_temp': tomorrow['temperature']['min']['celsius'] if tomorrow['temperature']['min'] else 'N/A',
            'precip_morning': tomorrow['chanceOfRain']['T06_12'] if 'T06_12' in tomorrow['chanceOfRain'] else 'N/A',
            'precip_afternoon': tomorrow['chanceOfRain']['T12_18'] if 'T12_18' in tomorrow['chanceOfRain'] else 'N/A'
        },
        'description': data['description']['text'] if 'description' in data else '概要はありません。'
    }
    return weather_info

class RegionSelect(discord.ui.Select):
    def __init__(self, region_name, options):
        super().__init__(placeholder=f"{region_name}の県を選択してください", options=options)
        self.region_name = region_name

    async def callback(self, interaction: discord.Interaction):
        region_id = self.values[0]
        weather_info = get_weather_info(region_id)

        if not weather_info:
            await interaction.response.send_message('天気情報を取得できませんでした。')
            return

        # 天気情報を整形して返信
        description_message = f"概要:\n{weather_info['description']}"

        formatted_weather_info = f"【{weather_info['today']['date']}の天気】\n" \
                                f"天気: {weather_info['today']['weather']}\n" \
                                f"最高気温: {weather_info['today']['high_temp']}℃\n" \
                                f"最低気温: {weather_info['today']['low_temp']}℃\n" \
                                f"午前の降水確率: {weather_info['today']['precip_morning']}\n" \
                                f"午後の降水確率: {weather_info['today']['precip_afternoon']}\n\n" \
                                f"【{weather_info['tomorrow']['date']}の天気】\n" \
                                f"天気: {weather_info['tomorrow']['weather']}\n" \
                                f"最高気温: {weather_info['tomorrow']['high_temp']}℃\n" \
                                f"最低気温: {weather_info['tomorrow']['low_temp']}℃\n" \
                                f"午前の降水確率: {weather_info['tomorrow']['precip_morning']}\n" \
                                f"午後の降水確率: {weather_info['tomorrow']['precip_afternoon']}\n\n" \
                                f"{description_message}"

        await interaction.response.send_message(f'{weather_info["location"]}の天気予報です:\n{formatted_weather_info}')  # 天気情報を送信

class MainRegionSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=region_name, value=region_name) for region_name in regions.keys()]
        super().__init__(placeholder="地方を選択してください", options=options)

    async def callback(self, interaction: discord.Interaction):
        region_name = self.values[0]
        region_data = regions[region_name]
        options = [discord.SelectOption(label=label, value=value) for label, value in region_data.items()]
        view = discord.ui.View()
        view.add_item(RegionSelect(region_name, options))
        await interaction.response.send_message(f"{region_name}の県を選択してください", view=view)

class RegionMenu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MainRegionSelect())

# setup関数でBotにコマンドを登録
def setup(bot: commands.Bot):
    @bot.tree.command(name="weather", description="指定した地名の天気を表示します")
    async def weather(interaction: discord.Interaction):
        await interaction.response.send_message("地方を選択してください", view=RegionMenu())