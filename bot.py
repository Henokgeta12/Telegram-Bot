import os
from flask import Flask, request
from flask_migrate import Migrate
import requests
from dotenv import load_dotenv
from models.client import Client, db  # Ensure correct import

load_dotenv()

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
database_url = os.getenv("DATABASE_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
MY_USER_1 = os.getenv("TELEGRAM_ID1")
MY_USER_2 = os.getenv("TELEGRAM_ID2")

User_ID = [MY_USER_1, MY_USER_2]
# Use a dictionary to store client data with chat_id as the key
clients = {}

def send_message(chat_id, text):
    data = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(TELEGRAM_API_URL, data=data)
    except Exception as e:
        print(f"Error sending message: {e}")

def notify_owner(client_data):
    summary = (
        f"Thank you for your information! we will contact you soon\n\n"
        f"Full Name: {client_data['name']}\n"
        f"Phone Number: {client_data['phone']}\n"
        f"Email Address: {client_data['email']}\n"
        f"Business Description: {client_data['Project_description']}"
    )
    for id in User_ID:
        send_message(id, summary)

def send_summary(chat_id, client_data):
    summary = (
        f"Thank you for your information! we will contact you soon\n\n"
        f"Here is the summary of your information:\n\n"
        f"Full Name: {client_data['name']}\n"
        f"Phone Number: {client_data['phone']}\n"
        f"Email Address: {client_data['email']}\n"
        f"Business Description: {client_data['Project_description']}"
    )
    send_message(chat_id, summary)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = str(data['message']['chat']['id'])
        username = data['message']['from'].get('username', 'N/A')
        text = data['message'].get('text', '').strip()

        if chat_id not in clients:
            clients[chat_id] = {'step': 'get_name'}

        client = clients[chat_id]

        if text and text.lower() == '/start':
            welcome_message = f"Hello {username}! Welcome to our arithmetic web development service. What's your full name?"
            send_message(chat_id, welcome_message)
            client['step'] = 'get_name'
        elif client['step'] == 'get_name':
            client['name'] = text
            send_message(chat_id, "Awesome! What's your email address?")
            client['step'] = 'get_email'
        elif client['step'] == 'get_email':
            if "@" in text and "." in text:
                client['email'] = text
                send_message(chat_id, "Got it! What's your phone number?")
                client['step'] = 'get_phone'
            else:
                send_message(chat_id, "Please enter a valid email address.")
        elif client['step'] == 'get_phone':
            if text.isdigit() and len(text) >= 10:
                client['phone'] = text
                send_message(chat_id, "Finally, please describe your project.")
                client['step'] = 'get_description'
            else:
                send_message(chat_id, "Please enter a valid phone number.")
        elif client['step'] == 'get_description':
            client['Project_description'] = text
            send_summary(chat_id, client)
            notify_owner(client)
            client['step'] = 'get_name'

    return '', 200

