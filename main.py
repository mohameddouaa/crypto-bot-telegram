import os
from flask import Flask, request
import requests

TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# CoinGecko API
def fetch_top_20():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False
    }
    r = requests.get(url, params=params)
    return r.json()

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/top20":
            coins = fetch_top_20()
            msg = "*📈 أعلى 20 عملة حسب الفوليوم:*
"
            msg += "`#  رمز    التغير%    الفوليوم`
"
            msg += "`-----------------------------`
"
            for i, coin in enumerate(coins, 1):
                symbol = coin["symbol"].upper().ljust(5)
                change = f"{coin['price_change_percentage_24h'] or 0:>6.2f}%"
                volume = f"${int(coin['total_volume'])//1_000_000}M"
                msg += f"`{str(i).rjust(2)}  {symbol}  {change}  {volume}`
"
            send_message(chat_id, msg)
        else:
            send_message(chat_id, "🟡 أرسل /top20 لعرض العملات الأكثر تداولًا")
    return "ok"

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

@app.route("/")
def index():
    return "بوت تيليغرام يعمل ✔️"

if __name__ == "__main__":
    app.run(debug=False)