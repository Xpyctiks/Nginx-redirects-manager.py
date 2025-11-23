from .db import db
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    realname = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False,default="0")
    created = db.Column(db.DateTime,default=datetime.now)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegramChat = db.Column(db.String(16), nullable=True)
    telegramToken = db.Column(db.String(64), nullable=True)
    logFile = db.Column(db.String(512), nullable=False)
    sessionKey = db.Column(db.String(64), nullable=False)
    nginxFolder = db.Column(db.String(64), nullable=False)
    nginxAddConfigsFolder = db.Column(db.String(100), nullable=False)

class Domains(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(12), nullable=False)
    created = db.Column(db.DateTime,default=datetime.now)

class Templates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(12), nullable=False)
    template= db.Column(db.String(1500), nullable=False)
    created = db.Column(db.DateTime,default=datetime.now)
    