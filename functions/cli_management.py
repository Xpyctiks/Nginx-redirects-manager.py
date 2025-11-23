import logging
from db.db import db
from db.database import Settings,User
from functions.load_config import load_config
from flask import current_app
from werkzeug.security import generate_password_hash

def set_telegramChat(tgChat: str) -> None:
    """CLI only function: sets Telegram ChatID value in database"""
    t = Settings(id=1,telegramChat=tgChat.strip())
    db.session.merge(t)
    db.session.commit()
    load_config(current_app)
    print("Telegram ChatID added successfully")
    try:
        logging.info(f"Telegram ChatID updated successfully!")
    except Exception as err:
        pass

def set_telegramToken(tgToken: str) -> None:
    """CLI only function: sets Telegram Token value in database"""
    t = Settings(id=1,telegramToken=tgToken)
    db.session.merge(t)
    db.session.commit()
    load_config(current_app)
    print("Telegram Token added successfully")
    try:
        logging.info(f"Telegram Token updated successfully!")
    except Exception as err:
        pass

def set_logpath(logpath: str) -> None:
    """CLI only function: sets Logger file path value in database"""
    t = Settings(id=1,logFile=logpath)
    db.session.merge(t)
    db.session.commit()
    load_config(current_app)
    updated = db.session.get(Settings, 1)
    print(f"logPath updated successfully. New log path: \"{updated.logFile}\"")
    try:
        logging.info(f"logPath updated to \"{updated.logFile}\"")
    except Exception as err:
        pass

def register_user(username: str,password: str,realname: str,role: str = "0") -> None:
    """CLI only function: adds new user and saves to database"""
    try:
        if User.query.filter_by(username=username).first():
            print(f"User \"{username}\" creation error - already exists!")
            logging.error(f"User \"{username}\" creation error - already exists!")
        else:
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                realname=realname,
                role=role
            )
            db.session.add(new_user)
            db.session.commit()
            load_config(current_app)
            print(f"New user \"{username}\" - \"{realname}\" created successfully!")
            logging.info(f"New user \"{username}\" - \"{realname}\" created successfully!")
    except Exception as err:
        logging.error(f"User \"{username}\" - \"{realname}\" creation error: {err}")
        print(f"User \"{username}\" - \"{realname}\" creation error: {err}")

def update_user(username: str,password: str) -> None:
    """CLI only function: password change for existing user"""
    try:
        user = User.query.filter_by(username=username).first()
        if user:
            d = User(id=user.id,password_hash=generate_password_hash(password))
            db.session.merge(d)
            db.session.commit()
            print(f"Password for user \"{user.username}\" updated successfully!")
            logging.info(f"Password for user \"{user.username}\" updated successfully!")
        else:
            print(f"User \"{username}\" set password error - no such user!")
            logging.error(f"User \"{username}\" set password error - no such user!")
            quit(1)
    except Exception as err:
        logging.error(f"User \"{username}\" set password error: {err}")
        print(f"User \"{username}\" set password error: {err}")

def delete_user(username: str) -> None:
    """CLI only function: deletes an existing user from database"""
    try:
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            load_config(current_app)
            print(f"User \"{user.username}\" deleted successfully!")
            logging.info(f"User \"{user.username}\" deleted successfully!")
        else:
            print(f"User \"{username}\" delete error - no such user!")
            logging.error(f"User \"{username}\" delete error - no such user!")
            quit(1)
    except Exception as err:
        logging.error(f"User \"{username}\" delete error: {err}")
        print(f"User \"{username}\" delete error: {err}")

def set_ngxFolder(data: str) -> None:
    """CLI only function: sets webFolder parameter in database"""
    try:
        t = Settings(id=1,nginxFolder=data)
        db.session.merge(t)
        db.session.commit()
        load_config(current_app)
        updated = db.session.get(Settings, 1)
        print(f"Nginx folder updated successfully. New path: \"{updated.nginxFolder}\"")
        logging.info(f"Nginx folder updated to \"{updated.nginxFolder}\"")
    except Exception as err:
        logging.error(f"Nginx folder \"{data}\" set error: {err}")
        print(f"Nginx folder \"{data}\" set error: {err}")

def set_ngxAddConfDir(data: str) -> None:
    """CLI only function: sets Nginx SSL certs path parameter in database"""
    try:
        t = Settings(id=1,nginxAddConfigsFolder=data)
        db.session.merge(t)
        db.session.commit()
        load_config(current_app)
        updated = db.session.get(Settings, 1)
        print(f"Nginx additional configs folder updated successfully. New path: \"{updated.nginxAddConfigsFolder}\"")
        logging.info(f"Nginx additional configs folder updated to \"{updated.nginxAddConfigsFolder}\"")
    except Exception as err:
        logging.error(f"Nginx additional configs folder \"{data}\" set error: {err}")
        print(f"Nginx additional configs folder \"{data}\" set error: {err}")

def show_users() -> None:
    users = User.query.order_by(User.username).all()
    if len(users) == 0:
        print("No users found in DB!")
        quit()
    for i, s in enumerate(users, 1):
        print(f"ID: {s.id}, Login: {s.username}, RealName: {s.realname}, Role: {s.role}, Created: {s.created}")
