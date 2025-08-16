from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Variables de entorno (Render las maneja)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi_token_de_verificacion")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")  # token de Meta Cloud API
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")  # ID de número de WhatsApp

# Endpoint de verificación (Meta pide esto al registrar webhook)
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Error: token no válido", 403
    return "Hola, soy tu bot en Render!", 200


# Endpoint para mensajes entrantes
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # Debug
    print("Mensaje recibido:", data)

    if "messages" in data["entry"][0]["changes"][0]["value"]:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        # Respuesta automática
        send_whatsapp_message(from_number, f"Recibí tu mensaje: {text}")

    return jsonify({"status": "ok"}), 200


# Función para enviar mensajes de vuelta a WhatsApp
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Respuesta de WhatsApp:", response.json())
    return response.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuración Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_ID = "1wanP530LIQdJYm32uZVmvRhxCns-d4j59c5Mx_zZoCs"
sheet = client.open_by_key(SHEET_ID).sheet1

def guardar_en_sheets(numero, mensaje, respuesta):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([fecha, numero, mensaje, respuesta])


