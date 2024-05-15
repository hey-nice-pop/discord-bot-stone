import discord
from discord import app_commands
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import geocoder
from urllib.parse import quote

def extract_location_details(address):
    components = address.split(',')
    components = [component.strip() for component in components]  # 余分な空白を削除

    # 都道府県と市区町村を格納する変数を初期化
    prefecture = None
    city = None

    # 逆順で住所コンポーネントを処理
    for component in reversed(components):
        if "都" in component or "府" in component or "県" in component or "道" in component:
            prefecture = component
        elif "市" in component or "区" in component or "町" in component or "村" in component:
            city = component
            break  # 市区町村を見つけたらループを抜ける

    if not prefecture or not city:
        return None  # 都道府県または市区町村が見つからない場合はNoneを返す

    return prefecture, city


# 天気情報を取得する関数
def get_weather_info(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # 追加: エンコーディングをUTF-8に設定
    soup = BeautifulSoup(response.text, 'html.parser')
    # 日付を取得
    dates = soup.find_all('h3', class_='left-style')
    today_date = dates[0].text.strip()
    tomorrow_date = dates[1].text.strip()

    # 天気を取得
    weather_conditions = soup.find_all('p', class_='weather-telop')
    today_weather = weather_conditions[0].text.strip()
    tomorrow_weather = weather_conditions[1].text.strip()

    # 最高気温と最低気温を取得
    temps = soup.find_all('div', class_='date-value-wrap')
    today_temps = temps[0].find_all('dd', class_='temp')
    tomorrow_temps = temps[1].find_all('dd', class_='temp')
    today_high = today_temps[0].text.strip()
    today_low = today_temps[1].text.strip()
    tomorrow_high = tomorrow_temps[0].text.strip()
    tomorrow_low = tomorrow_temps[1].text.strip()

    # 降水確率を取得
    precipitations = soup.find_all('tr', class_='rain-probability')
    today_precip = precipitations[0].find_all('td')
    tomorrow_precip = precipitations[1].find_all('td')
    today_precip_morning = today_precip[1].text.strip()
    today_precip_afternoon = today_precip[2].text.strip()
    tomorrow_precip_morning = tomorrow_precip[1].text.strip()
    tomorrow_precip_afternoon = tomorrow_precip[2].text.strip()

    # 情報をまとめる
    weather_info = {
        'today': {
            'date': today_date,
            'weather': today_weather,
            'high_temp': today_high,
            'low_temp': today_low,
            'precip_morning': today_precip_morning,
            'precip_afternoon': today_precip_afternoon
        },
        'tomorrow': {
            'date': tomorrow_date,
            'weather': tomorrow_weather,
            'high_temp': tomorrow_high,
            'low_temp': tomorrow_low,
            'precip_morning': tomorrow_precip_morning,
            'precip_afternoon': tomorrow_precip_afternoon
        }
    }

    # 注意報を抽出
    warnings = []
    warn_box = soup.find('div', class_='common-warn-entry-box')
    if warn_box:
        alert_entries = warn_box.find_all('dd', class_='alert-entry')
        for entry in alert_entries:
            warnings.append(entry.text.strip())

    # 注意報情報をweather_info辞書に追加
    weather_info['warnings'] = warnings

    return weather_info

# setup関数でBotにコマンドを登録
def setup(bot: commands.Bot):
    @bot.tree.command(name="weather", description="指定した地名の天気を表示します")
    async def weather(interaction: discord.Interaction, location: str):
        # geocoderを使用して地名から住所を取得
        g = geocoder.osm(location, country_codes='jp')
        if not g.ok:
            await interaction.response.send_message('地名を特定できませんでした。')
            return
        
        # 住所から都道府県と市区町村を抽出
        prefecture, city = extract_location_details(g.address)

        # tenki.jpの検索クエリ用の住所形式を生成
        search_query = f"{prefecture}{city}"

        # tenki.jpの検索URLを構築
        search_url = f'https://tenki.jp/search/?keyword={quote(search_query)}'
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        forecast_link_element = soup.select_one(".search-entry-data a")
        
        if not forecast_link_element:
            await interaction.response.send_message('検索結果が見つかりませんでした。地名を確認してください。')
            return

        forecast_link = forecast_link_element['href']
        forecast_url = 'https://tenki.jp' + forecast_link
        print(forecast_url)
        weather_info = get_weather_info(forecast_url)
            
        # 天気情報を整形して返信
        warnings_formatted = "\n".join([f"- {warning}" for warning in weather_info['warnings']])
        warnings_message = f"注意報:\n{warnings_formatted}" if warnings_formatted else "注意報はありません。"

        formatted_weather_info = f"【{weather_info['today']['date']}の天気】\n" \
                                f"天気: {weather_info['today']['weather']}\n" \
                                f"最高気温: {weather_info['today']['high_temp']}\n" \
                                f"最低気温: {weather_info['today']['low_temp']}\n" \
                                f"午前の降水確率: {weather_info['today']['precip_morning']}\n" \
                                f"午後の降水確率: {weather_info['today']['precip_afternoon']}\n\n" \
                                f"【{weather_info['tomorrow']['date']}の天気】\n" \
                                f"天気: {weather_info['tomorrow']['weather']}\n" \
                                f"最高気温: {weather_info['tomorrow']['high_temp']}\n" \
                                f"最低気温: {weather_info['tomorrow']['low_temp']}\n" \
                                f"午前の降水確率: {weather_info['tomorrow']['precip_morning']}\n" \
                                f"午後の降水確率: {weather_info['tomorrow']['precip_afternoon']}\n\n" \
                                f"{warnings_message}"

        await interaction.response.send_message(f'{location}の天気予報です:\n{formatted_weather_info}')  # 天気情報を送信
