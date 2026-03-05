from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

ALERT_STATES = [
    # Description
    "Ne répond pas 2",
    "Ne répond pas 3",
    "Commande annulée",
    "Annulé par le client",
    "Le prix est faux",
    "Wilaya erronée",
    "Injoignable / Éteint",
    "Fausse commande",
    "Appel sans réponse",
    # Name
    "ne_repond_pas_2",
    "ne_repond_pas_3",
    "commande_annulee",
    "annule_par_le_client",
    "le_prix_est_faux",
    "wilaya_erronee",
    "injoignable_eteint",
    "fausse_commande",
    "appel_sans_reponse"
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

    parcel = data.get('Data', {})
    tracking = parcel.get('TrackingNumber', 'N/A')
    state = parcel.get('State', {})
    status_desc = state.get('Description', 'N/A')
    status_name = state.get('Name', 'N/A')
    customer = parcel.get('Customer', {})
    client = customer.get('Name', 'N/A')
    phone = customer.get('Phone', {}).get('Number1', 'N/A')
    amount = parcel.get('Amount', 'N/A')
    city = parcel.get('DeliveryAddress', {}).get('City', 'N/A')

    if status_desc in ALERT_STATES or status_name in ALERT_STATES:
        message = f"""
⚠️ <b>تنبيه طرد</b>
━━━━━━━━━━━━━━
📬 رقم التتبع: <code>{tracking}</code>
📊 الحالة: <b>{status_desc}</b>
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
