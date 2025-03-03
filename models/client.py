from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Client(db.model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    chat_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50) ,nullable=False)
    email= db.Column(db.String(50), nullable=False,unique=True)
    phone_number = db.Column(db.Integer, nullable=False)
    Project description = db.Column(db.String(50), nullable=True)
    created_at = db.Column(TIMESTAMP(timezone=True), nullable=False, datetime.now())
    step = db.Column(db.String(50), default='get_name')

    def __init__(self, chat_id):
        self.chat_id = chat_id