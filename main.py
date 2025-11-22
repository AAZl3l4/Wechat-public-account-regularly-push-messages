import os
import math
import random
import requests
from datetime import date, datetime

# 微信功能
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

today = datetime.now()

# 微信配置
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_ids = os.environ["USER_ID"].split(',')
template_ids = os.environ["TEMPLATE_ID"].split(',')

# 打印微信配置
print( f"打印系统参数 : USER_ID: {user_ids}, TEMPLATE_ID: {template_ids}")
print(template_ids[0])

# 发薪日
SOLARY_DAY = "15"
city = "日照"


def get_weather(city):
    try:
        url = f"https://uapis.cn/api/v1/misc/weather?city={city}"
        res = requests.get(url, timeout=10).json()
        return (res['weather'],
                math.floor(res['temperature']),
                res['wind_direction'],
                res['wind_power'],
                res['humidity'])
    except Exception as e:
        print(f"❌ 天气获取失败: {e}")
        return "未知", 0, "未知", "0", 0


def get_city_date(city):
    return city, today.date().strftime("%Y-%m-%d")


def get_solary():
    next = datetime.strptime(f"{date.today().year}-{date.today().month}-{SOLARY_DAY}", "%Y-%m-%d")
    if next < datetime.now():
        if next.month == 12:
            next = next.replace(year=next.year + 1, month=1)
        else:
            next = next.replace(month=next.month + 1)
    return (next - today).days


def get_words():
    try:
        words = requests.get("https://api.shadiao.pro/chp", timeout=10)
        if words.status_code == 200:
            return words.json()['data']['text']
        return "愿你今天比昨天更快乐"
    except Exception as e:
        print(f"❌ 情话获取失败: {e}")
        return "愿你今天比昨天更快乐"


def get_history_today():
    try:
        res = requests.get("https://60s.viki.moe/v2/today-in-history", timeout=10).json()
        items = res['data']['items']
        if items:
            item = random.choice(items)
            return f"{item['year']}年 · {item['title']}"
        return "历史在今天静待书写"
    except Exception as e:
        print(f"❌ 历史获取失败: {e}")
        return "历史在今天静待书写"


def get_news():
    try:
        res = requests.get("https://60s.viki.moe/v2/60s", timeout=10).json()
        news_list = res['data']['news']
        return news_list[0] if news_list else "今日新闻加载中..."
    except Exception as e:
        print(f"❌ 新闻获取失败: {e}")
        return "今日新闻加载中..."


def get_lunar():
    try:
        res = requests.get("https://60s.viki.moe/v2/lunar", timeout=10).json()
        data = res['data']
        lunar_date = data['lunar']['desc_short']
        term = data['term']['today']
        taboo = data['taboo']['day']
        return f"📅 {lunar_date}\n🌾 节气：{term}\n✅ 宜：{taboo['recommends']}\n❌ 忌：{taboo['avoids']}"
    except Exception as e:
        print(f"❌ 黄历获取失败: {e}")
        return "黄历信息获取失败"


def get_yiyan():
    try:
        res = requests.get("https://xhnzz.com/index/api/yan/api.php", timeout=10)
        if res.status_code == 200:
            return res.text.strip()
        return "生活明朗，万物可爱"
    except Exception as e:
        print(f"❌ 一言获取失败: {e}")
        return "生活明朗，万物可爱"


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

# 获取数据（一次）
wea, tem, wind_dir, wind_power, humidity = get_weather(city)
cit, dat = get_city_date(city)
solary_days = get_solary()

# 精简数据（保留核心字段）
data = {
    "header": {"value": f"📍 {cit} | {dat} | {wea} {tem}°C", "color": get_random_color()},
    "weather_detail": {"value": f"💨 {wind_dir} {wind_power}级 | 💧 {humidity}%", "color": get_random_color()},
    "solary": {"value": f"💰 还有{solary_days}天", "color": get_random_color()},
    "history_today": {"value": f"📜 {get_history_today()}", "color": "#000000"},
    "news": {"value": f"📰 {get_news()}", "color": "#000000"},
    "lunar": {"value": get_lunar(), "color": "#000000"},
    "yiyan": {"value": f"💭 {get_yiyan()}", "color": get_random_color()},
    "words": {"value": f"💕 {get_words()}", "color": get_random_color()}
}

if solary_days == 0:
    data["solary"]['value'] = "🎉 今天发工资！"

# 发送给每个用户
for j, user_id in enumerate(user_ids):
    try:
        print(f"发送给用户 {j+1}: {user_id[:10]}...")
        res = wm.send_template(user_id, template_ids[0], data)
        print(f"✅ 成功: {res}")
    except Exception as e:
        print(f"❌ 失败: {e}")


# for key, item in data.items():
#     print(f"  内容: {item['value']}")
#     print(f"  颜色: {item['color']}")
