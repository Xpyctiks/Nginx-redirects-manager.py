import os, logging,string,random
from db.db import db
from db.database import Settings

def load_config(application):
    """Important function - loads all configuration values from Sqlite3 database when an application starts"""
    with application.app_context():
        try:
            config = db.session.get(Settings, 1)
            application.config.update({
                "TELEGRAM_TOKEN": f"{config.telegramToken}",
                "TELEGRAM_CHATID": f"{config.telegramChat}",
                "LOG_FILE": f"{config.logFile}",
                "SECRET_KEY": f"{config.sessionKey}",
                "NGX_FOLDER": f"{config.nginxFolder}",
                "NGX_ADD_CONF_DIR": f"{config.nginxAddConfigsFolder}",
            })
            logging.basicConfig(filename=config.logFile,level=logging.INFO,format='%(asctime)s - Ngx_Redir_Manager - %(levelname)s - %(message)s',datefmt='%d-%m-%Y %H:%M:%S')
            logging.getLogger('werkzeug').setLevel(logging.WARNING)
            logging.info("Programm started succesfully. Configuration loaded.")
        except Exception as msg:
            print(f"Load-config error: {msg}")
            quit(1)

def generate_default_config(application,CONFIG_DIR: str,DB_FILE: str):
    """Checks every application loads if the app's configuration exists. If not - creates DB file with default values.Takes application as app context, CONFIG_DIR as value where config DB located and DB_FILE as config DB name"""
    with application.app_context():
        if not os.path.isfile(DB_FILE):
            length = 32
            characters = string.ascii_letters + string.digits
            session_key = ''.join(random.choice(characters) for _ in range(length))
            default_settings = Settings(id=1, 
                telegramChat = "",
                telegramToken = "",
                logFile = "/var/log/nginx-redirects-manager.log",
                sessionKey = session_key,
                nginxFolder = "/etc/nginx/",
                nginxAddConfigsFolder = "/etc/nginx/additional-configs/"
                )
            try:
                if not os.path.exists(CONFIG_DIR):
                    os.mkdir(CONFIG_DIR)
                db.create_all()
                db.session.add(default_settings)
                db.session.commit()
                print(f"First launch. Default database created in {DB_FILE}. You need to add telegram ChatID and Token if you want to get notifications")
            except Exception as msg:
                print(f"Generate-default-config error: {msg}")
                quit(1)
