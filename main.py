#!/usr/local/bin/python3

from flask import Flask
from flask_login import LoginManager
import os,sys
from datetime import timedelta

CONFIG_DIR = "/etc/nginx-redirects-manager/"
DB_FILE = os.path.join(CONFIG_DIR,"nginx-redirects-manager.db")
JOB_COUNTER = JOB_TOTAL = 1
application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_FILE
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config['PERMANENT_SESSION_LIFETIME'] = 28800
application.config['SESSION_COOKIE_SECURE'] = False
application.config['SESSION_COOKIE_HTTPONLY'] = True
application.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
application.config['SESSION_USE_SIGNER'] = True
application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
from db.db import db
from db.database import User
db.init_app(application)
application.config['SESSION_SQLALCHEMY'] = db
from functions.load_config import load_config, generate_default_config
generate_default_config(application,CONFIG_DIR,DB_FILE)
load_config(application)
application.secret_key = application.config["SECRET_KEY"]
login_manager = LoginManager()
login_manager.login_view = "main.login.login"
login_manager.session_protection = "strong"
login_manager.init_app(application)
with application.app_context():
    db.create_all()
from functions.cli_management import set_telegramChat,set_telegramToken,set_logpath,delete_user,register_user,update_user,set_ngxFolder,set_ngxAddConfDir,show_users

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))
from pages import blueprint as routes_blueprint
application.register_blueprint(routes_blueprint)

def main() -> None:
    load_config(application)

if __name__ == "__main__":
    application.app_context().push()
    if len(sys.argv) > 2:
        if sys.argv[1] == "set" and sys.argv[2] == "chat":
            if (len(sys.argv) == 4):
                set_telegramChat(sys.argv[3].strip())
            else:
                print("Error! Enter ChatID")
        elif sys.argv[1] == "set" and sys.argv[2] == "token":
            if (len(sys.argv) == 4):
                set_telegramToken(sys.argv[3].strip())
            else:
                print("Error! Enter Token")
        elif sys.argv[1] == "set" and sys.argv[2] == "log":
            if (len(sys.argv) == 4):
                set_logpath(sys.argv[3].strip())
            else:
                print("Error! Enter log path")
        elif sys.argv[1] == "user" and sys.argv[2] == "add":
            #if no "role" specified
            if (len(sys.argv) == 6):
                register_user(sys.argv[3].strip(),sys.argv[4].strip(),sys.argv[5].strip())
            #if "role" is specified
            elif (len(sys.argv) == 7):
                if not sys.argv[6].strip().isdigit():
                    print("Role can be only a digit.")
                    quit()
                register_user(sys.argv[3].strip(),sys.argv[4].strip(),sys.argv[5].strip(),sys.argv[6].strip())
            else:
                print("Error! Reqired: username/password/realname, role can be set too. ")
        elif sys.argv[1] == "user" and sys.argv[2] == "setpwd":
            if (len(sys.argv) == 5):
                update_user(sys.argv[3].strip(),sys.argv[4].strip())
            else:
                print("Error! Enter both username and new password")
        elif sys.argv[1] == "user" and sys.argv[2] == "del":
            if (len(sys.argv) == 4):
                delete_user(sys.argv[3].strip())
            else:
                print("Error! Enter both username and new password")
        elif sys.argv[1] == "set" and sys.argv[2] == "ngx-folder":
            if (len(sys.argv) == 4):
                set_ngxFolder(sys.argv[3].strip())
            else:
                print("Error! Enter root folder for Nginx. /etc/nginx for example.")
        elif sys.argv[1] == "set" and sys.argv[2] == "ngx-add-conf":
            if (len(sys.argv) == 4):
                set_ngxAddConfDir(sys.argv[3].strip())
            else:
                print("Error! Enter path to the folder with additional nginx files with redirects")
        elif sys.argv[1] == "show" and sys.argv[2] == "config":
            if (len(sys.argv) == 3):
                print (f"""
    Telegram ChatID:       {application.config["TELEGRAM_TOKEN"]}
    Telegram Token:        {application.config["TELEGRAM_CHATID"]}
    Log file:              {application.config["LOG_FILE"]}
    SessionKey:            {application.config["SECRET_KEY"]}
    Nginx folder:          {application.config["NGX_FOLDER"]}
    Nginx add. config dir: {application.config["NGX_ADD_CONF_DIR"]}
    Session secret key:    {application.secret_key}
                """)
        elif sys.argv[1] == "show" and sys.argv[2] == "users":
            show_users()
    #if we call the script from console with argument "main" to start provision process
    elif len(sys.argv) == 2 and sys.argv[1] == "main":
        main()
    #else just show help info.
    elif len(sys.argv) <= 2:
        print(f"""Usage: \n{sys.argv[0]} set chat <chatID>
\tAdd Telegram ChatID for notifications.
{sys.argv[0]} set token <Token>
\tAdd Telegram Token for notifications.
{sys.argv[0]} set log <new log file path>
\tAdd Telegram Token for notifications.
{sys.argv[0]} user add <login> <password> <realname>
\tAdd new user with its password and default permissions for all cache pathes.
{sys.argv[0]} user setpwd <user> <new password>
\tSet new password for existing user.
{sys.argv[0]} user del <user>
\tDelete existing user by its login
{sys.argv[0]} set ngx-folder <nginx_root_folder>
\tSets root folder for Nginx. /etc/nginx for example.
{sys.argv[0]} set ngx-add-conf <path to nginx additional settings folder>
\tSets path to the folder with additional nginx files with redirects
Info: full script should be launched via UWSGI server. In CLI mode use can only use commands above.
""")

