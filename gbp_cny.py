import requests
from datetime import datetime
import os

# ===== 必填：换成你自己的 Server酱 SendKey =====
SEND_KEY = "SCT292092THXz7gyCYuUmrtEYFBuQU3Xof"  # ← 把这里替换成你的 SendKey

API_URL = "https://api.exchangerate-api.com/v4/latest/GBP"
LAST_FILE = "last_rate.txt"

def get_gbp_to_cny():
    """获取当前英镑兑人民币汇率"""
    r = requests.get(API_URL, timeout=8)
    r.raise_for_status()
    data = r.json()
    return float(data["rates"]["CNY"])

def send_wechat(title: str, content: str):
    """通过 Server酱推送到微信"""
    url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    data = {"title": title, "desp": content}
    resp = requests.post(url, data=data, timeout=8)
    return resp.status_code, resp.text

def read_last():
    """读取上次汇率"""
    if os.path.exists(LAST_FILE):
        try:
            return float(open(LAST_FILE, "r", encoding="utf-8").read().strip())
        except:
            return None
    return None

def write_last(rate: float):
    """保存本次汇率"""
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(str(rate))

if __name__ == "__main__":
    try:
        rate = get_gbp_to_cny()
        last = read_last()
        diff = (rate - last) if last is not None else None
        arrow = ""
        if diff is not None:
            arrow = "↑" if diff > 0 else ("↓" if diff < 0 else "→")

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"GBP/CNY {rate:.4f} {arrow}"
        body = f"""时间：{now}
当前英镑兑人民币：{rate:.4f}
{('较上次变化：' + ('+' if diff>0 else '') + f'{diff:.4f}') if diff is not None else '首次记录'}
数据来源：exchangerate-api.com
"""
        code, text = send_wechat(title, body)
        write_last(rate)
        print("已推送到微信。HTTP状态：", code)
    except Exception as e:
        print("获取或推送失败：", e)
