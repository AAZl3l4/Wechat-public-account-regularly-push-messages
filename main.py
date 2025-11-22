import os
import math
import random
import requests
from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

today = datetime.now()

# 微信配置
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_ids = os.environ["USER_ID"].split(',')
template_ids = os.environ["TEMPLATE_ID"].split(',')

SOLARY_DAY = "15"
city = "日照"


def get_weather(city):
    try:
        url = f"https://uapis.cn/api/v1/misc/weather?city={city}"
        res = requests.get(url, timeout=10).json()
        return (res['weather'],
                int(res['temperature']),
                res['wind_direction'],
                res['wind_power'],
                res['humidity'])
    except Exception as e:
        print(f"❌ 天气失败: {e}")
        return "未知", 0, "未知", "0", 0


def get_solary():
    try:
        next = datetime.strptime(f"{date.today().year}-{date.today().month}-{SOLARY_DAY}", "%Y-%m-%d")
        if next < datetime.now():
            if next.month == 12:
                next = next.replace(year=next.year + 1, month=1)
            else:
                next = next.replace(month=next.month + 1)
        return (next - today).days
    except Exception as e:
        print(f"❌ 发薪日失败: {e}")
        return 999


def get_words():
    try:
        words = requests.get("https://api.shadiao.pro/chp", timeout=10)
        return words.json()['data']['text'] if words.status_code == 200 else "愿你快乐"
    except Exception:
        return "愿你快乐"

def get_city_date(city):
    return city, today.date().strftime("%Y-%m-%d")

def get_history_today():
    try:
        res = requests.get("https://60s.viki.moe/v2/today-in-history", timeout=10).json()
        items = res.get('data', {}).get('items', [])
        if items:
            item = random.choice(items)
            return f"{item['year']}年 · {item['title']}"
        return "历史在今天静待书写"
    except Exception:
        return "历史在今天静待书写"


def get_news():
    try:
        res = requests.get("https://60s.viki.moe/v2/60s", timeout=10).json()
        news_list = res.get('data', {}).get('news', [])
        return news_list[0] if news_list else "今日安好，静待花开"
    except Exception:
        return "今日安好，静待花开"


def get_lunar():
    try:
        res = requests.get("https://60s.viki.moe/v2/lunar", timeout=10).json()
        data = res.get('data', {})
        lunar_date = data.get('lunar', {}).get('desc_short', '')
        term = data.get('term', {}).get('today', '')
        taboo = data.get('taboo', {}).get('day', {})
        return {
            "date": lunar_date,
            "term": term,
            "yi": taboo.get('recommends', ''),
            "ji": taboo.get('avoids', '')
        }
    except Exception:
        return {"date": "", "term": "", "yi": "", "ji": ""}


def get_yiyan():
    try:
        res = requests.get("https://xhnzz.com/index/api/yan/api.php", timeout=10)
        return res.text.strip() if res.status_code == 200 else "生活明朗"
    except Exception:
        return "生活明朗"


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# 主逻辑
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

wea, tem, wind_dir, wind_power, humidity = get_weather(city)
cit, dat = get_city_date(city)
solary_days = get_solary()
lunar_info = get_lunar()

data = {
    # 只传纯文本值，不加符号
    "city": cit,
    "date": dat,
    "weather": wea,
    "temp": str(tem),
    "wind_dir": wind_dir,
    "wind_power": wind_power,
    "humidity": str(humidity),
    "solary_days": str(solary_days),
    "history": get_history_today(),
    "news": get_news(),
    "lunar_date": lunar_info["date"],
    "lunar_term": lunar_info["term"],
    "lunar_yi": lunar_info["yi"],
    "lunar_ji": lunar_info["ji"],
    "yiyan": get_yiyan(),
    "words": get_words()
}

# 发送
for user_id in user_ids:
    res = wm.send_template(user_id, template_ids[0], data)
    print(f"发送给 {user_id[:10]}: {res}")
