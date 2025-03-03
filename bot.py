import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import requests
from dotenv import load_dotenv
from .models import Client
load_dotenv()

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
database_url = os.getenv("DATABASE_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"


def send_message(chat_id, text):
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(TELEGRAM_API_URL, data=data)

def send_summary(chat_id,client):
    summary = (
        f"Thank you for your information! we will contact you soon\n\n"
        f"Full Name: {client.name}\n"
        f"Phone Number: {client.phone_number}\n"
        f"Email Address: {client.email}\n"
        f"Business Description: {client.Project description}"
    )
    send_message(chat_id, summary)


app = Flask(__name__)
# Database configuration (adjust for SQLite or MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'database_url'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.init_app(app)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = str(data['message']['chat']['id'])
        username = data['message']['from'].get('username', 'N/A')
        text = data['message'].get('text', '').strip()
        
        client = Client.query.filter_by(chat_id=chat_id).first()
        
        if text and text.lower() == '/start':
            welcome_message = f"Hello {username}! Welcome to our arithmetic web development service. whats your full name?"
            send_message(chat_id, welcome_message)
        elif client.step == "get_name":
            client.name = text
            client.step = 'get_email'
            db.session.commit()
            send_message(chat_id, "Awesome! What's your email address?")
        elif client.step == 'get_email':
            if "@" in text and "." in text:
                client.email = text
                client.step = 'get_phone' 
                db.session.commit()
                send_message(chat_id, "Got it! What's your phone number")
        elif client.step == 'get_phone':
            if text.isdigit() and len(text) >= 10:
                client.phone = text
                client.step = 'get_email'
                db.session.commit()
                send_message(chat_id, "Finally, please describe your project description.")
            else:
                send_message(chat_id, "Please enter a valid phone number.")
        elif client.step == 'get_description':
            client.description = text
            db.session.commit()
            send_summary(chat_id, client)
            # Reset user step or remove from DB if necessary
            client.step = 'completed'
            db.session.commit()
            
    return '', 200
    
