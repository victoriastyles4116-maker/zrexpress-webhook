from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    event = data.get('event', 'unknown')
    parcel = data.get('data', {})
    tracking = parcel.get('trackingNumber', 'N/A')
    status = parcel.get('state', 'N/A')
    client = parcel.get('clientName', 'N/A')
    phone = parcel.get('phone', 'N/A')

    message = f"""
📦 <b>تحديث طرد جديد</b>
━━━━━━━━━━━━━━
🔔 الحدث: <b>{event}</b>
📬 رقم التتبع: <code>{tracking}</code>
📊 الحالة: {status}
👤 العميل: {client}
📞 الهاتف: {phone}
    """

    send_telegram(message)
    return {"status": "ok"}, 200

@app.route('/', methods=['GET'])
def home():
    return "✅ Webhook server is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
