from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

ALERT_SLUGS = [
    "appel_telephonique",
    "en_attente_du_client",
    "reporter_a_une_date_ulterieure"
]

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
    event_type = data.get('EventType', '')
    parcel = data.get('Data', {})

    tracking = parcel.get('TrackingNumber', 'N/A')
    customer = parcel.get('Customer', {})
    client = customer.get('Name', 'N/A')
    phone = customer.get('Phone', {}).get('Number1', 'N/A')
    amount = parcel.get('Amount', 'N/A')
    city = parcel.get('DeliveryAddress', {}).get('City', 'N/A')

    if event_type == 'parcel.state.situation.created':
        situation = parcel.get('Situation', {})
        slug = situation.get('Slug', '')
        description = situation.get('Description', 'N/A')

        print(f"SLUG RECEIVED: '{slug}'")
        print(f"SLUG IN LIST: {slug in ALERT_SLUGS}")

        if slug in ALERT_SLUGS:
            message = f"""
⚠️ <b>تنبيه طرد</b>
━━━━━━━━━━━━━━
📬 رقم التتبع: <code>{tracking}</code>
📊 الحالة: <b>{description}</b>
👤 العميل: {client}
📞 الهاتف: {phone}
🏙️ المدينة: {city}
💰 المبلغ: {amount} دج
            """
            send_telegram(message)

    return {"status": "ok"}, 200

@app.route('/', methods=['GET'])
def home():
    return "✅ Webhook server is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
