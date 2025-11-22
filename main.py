import os
import math
import random
import requests
from datetime import date, datetime

# 微信功能已注释 - 如需启用请取消注释
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

today = datetime.now()

# 微信公众测试号配置（已注释）
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_ids = os.environ["USER_ID"].split(',')
template_ids = os.environ["TEMPLATE_ID"].split(',')

# 发薪日配置
solarys = ["15"]

# 城市固定为日照
city = "日照"


# 获取天气详情（含风向、风力、湿度）
def get_weather(city):
    try:
        url = f"https://uapis.cn/api/v1/misc/weather?city={city}"
        res = requests.get(url, timeout=10).json()
        return (res['weather'],
                math.floor(res['temperature']),
                res['wind_direction'],
                res['wind_power'],
                res['humidity'])
    except Exception:
        return "未知", 0, "未知", "0", 0


# 当前城市、日期
def get_city_date(city):
    return city, today.date().strftime("%Y-%m-%d")


# 距离发工资还有多少天
def get_solary(solary):
    next = datetime.strptime(f"{date.today().year}-{date.today().month}-{solary}", "%Y-%m-%d")
    if next < datetime.now():
        if next.month == 12:
            next = next.replace(year=next.year + 1, month=1)
        else:
            next = next.replace(month=next.month + 1)
    return (next - today).days


# 每日一句（土味情话）
def get_words():
    try:
        words = requests.get("https://api.shadiao.pro/chp", timeout=10)
        if words.status_code == 200:
            return words.json()['data']['text']
        return "愿你今天比昨天更快乐"
    except Exception:
        return "愿你今天比昨天更快乐"


# 历史上的今天
def get_history_today():
    try:
        res = requests.get("https://60s.viki.moe/v2/today-in-history", timeout=10).json()
        items = res['data']['items']
        if items:
            item = random.choice(items)
            return f"{item['year']}年 · {item['title']}"
        return "历史在今天静待书写"
    except Exception:
        return "历史在今天静待书写"


# 今日新闻（取3条）
def get_news():
    try:
        res = requests.get("https://60s.viki.moe/v2/60s", timeout=10).json()
        news_list = res['data']['news'][:3]
        return "\n".join([f"{i + 1}. {news}" for i, news in enumerate(news_list)])
    except Exception:
        return "今日安好，静待花开"


# 黄历信息
def get_lunar():
    try:
        res = requests.get("https://60s.viki.moe/v2/lunar", timeout=10).json()
        data = res['data']
        lunar_date = data['lunar']['desc_short']
        term = data['term']['today']
        taboo = data['taboo']['day']

        return f"📅 {lunar_date}\n🌾 今日节气：{term}\n✅ 宜：{taboo['recommends']}\n❌ 忌：{taboo['avoids']}"
    except Exception:
        return "黄历信息获取失败"


# 随机一言
def get_yiyan():
    try:
        res = requests.get("https://xhnzz.com/index/api/yan/api.php", timeout=10)
        if res.status_code == 200:
            return res.text.strip()
        return "生活明朗，万物可爱"
    except Exception:
        return "生活明朗，万物可爱"


# 字体随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# 主逻辑
# 如需发送微信，取消以下注释
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

# 处理每个发薪日配置
for i in range(len(solarys)):
    wea, tem, wind_dir, wind_power, humidity = get_weather(city)
    cit, dat = get_city_date(city)

    # 构建模板数据
    data = {
        "date": {"value": dat, "color": get_random_color()},
        "city": {"value": cit, "color": get_random_color()},
        "weather": {"value": wea, "color": get_random_color()},
        "temperature": {"value": f"{tem}°C", "color": get_random_color()},
        "wind_direction": {"value": wind_dir, "color": get_random_color()},
        "wind_power": {"value": f"{wind_power}级", "color": get_random_color()},
        "humidity": {"value": f"{humidity}%", "color": get_random_color()},  
        "solary": {"value": str(get_solary(solarys[i])), "color": get_random_color()},
        "history_today": {"value": get_history_today(), "color": "#000000"},
        "news": {"value": get_news(), "color": "#000000"},
        "lunar": {"value": get_lunar(), "color": "#000000"},
        "yiyan": {"value": get_yiyan(), "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()}
    }

    # 发薪日特殊文案
    if get_solary(solarys[i]) == 0:
        data["solary"]['value'] = "🎉 今天发工资啦！快去犒劳一下自己吧"

    # 微信发送（已注释）
    res = wm.send_template(user_ids[i], template_ids[i], data)

# for key, item in data.items():
#     if isinstance(item, dict) and 'value' in item:
#         print(f"【{key}】")
#         print(item['value'])
#         if 'color' in item:
#             print(f"颜色: {item['color']}")
#     else:
#         print(f"【{key}】")
#         print(item)
#     print()
