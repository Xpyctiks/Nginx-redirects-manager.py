import logging
import click
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

def register_user(username: str,password: str,realname: str,rights: str = "1") -> None:
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
        rights=int(rights)
      )
      db.session.add(new_user)
      db.session.commit()
      load_config(current_app)
      print(f"New user \"{username}\" - \"{realname}\" created successfully!")
      logging.info(f"New user \"{username}\" - \"{realname}\" created successfully!")
  except Exception as err:
    logging.error(f"User \"{username}\" - \"{realname}\" creation error: {err}")
    print(f"User \"{username}\" - \"{realname}\" creation error: {err}")

def make_admin_user(username: str) -> None:
  """CLI only function: grants admin rights (255) to the given user"""
  try:
    user = User.query.filter_by(username=username).first()
    if user:
      user.rights = 255
      db.session.commit()
      print(f"User \"{username}\" successfully set as admin!")
      logging.info(f"User \"{username}\" successfully set as admin!")
    else:
      print(f"User \"{username}\" set admin rights error - no such user!")
      logging.error(f"User \"{username}\" set admin rights error - no such user!")
      quit(1)
  except Exception as err:
    logging.error(f"User \"{username}\" set admin rights error: {err}")
    print(f"User \"{username}\" set admin rights error: {err}")

def remove_admin_user(username: str) -> None:
  """CLI only function: demotes the given user back to regular rights (1)"""
  try:
    user = User.query.filter_by(username=username).first()
    if user:
      user.rights = 1
      db.session.commit()
      print(f"User \"{username}\" successfully set as the regular user!")
      logging.info(f"User \"{username}\" successfully set as the regular user!")
    else:
      print(f"User \"{username}\" unset admin rights error - no such user!")
      logging.error(f"User \"{username}\" unset admin rights error - no such user!")
      quit(1)
  except Exception as err:
    logging.error(f"User \"{username}\" unset admin rights error: {err}")
    print(f"User \"{username}\" unset admin rights error: {err}")

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
  """CLI only function: Shows all users in database"""
  try:
    users = User.query.order_by(User.username).all()
    if len(users) == 0:
      print("No users found in DB!")
      quit()
    for i, s in enumerate(users, 1):
      print(f"ID: {s.id}, Login: {s.username}, RealName: {s.realname}, Rights: {s.rights}, Created: {s.created}")
  except Exception as err:
    logging.error(f"CLI show users function error: {err}")
    print(f"CLI show users function error: {err}")

def show_config() -> None:
  """CLI only function: shows all current config from the database"""
  print(f"""
Telegram ChatID:       {current_app.config["TELEGRAM_CHATID"]}
Telegram Token:        {current_app.config["TELEGRAM_TOKEN"]}
Log file:              {current_app.config["LOG_FILE"]}
SessionKey:            {current_app.config["SECRET_KEY"]}
Nginx folder:          {current_app.config["NGX_FOLDER"]}
Nginx add. config dir: {current_app.config["NGX_ADD_CONF_DIR"]}
Authelia logout URL:   {current_app.config["AUTHELIA_LOGOUT_URL"]}
Session secret key:    {current_app.secret_key}
  """)

def with_app_context(func):
  """Decorator to run a CLI command inside the Flask app context"""
  def wrapper(*args, **kwargs):
    from main import application
    with application.app_context():
      return func(*args, **kwargs)
  return wrapper

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def show_cli():
  """Nginx redirects manager CLI"""
  pass

# SET
@show_cli.group()
def set():
  """Set configuration values"""
  pass

@set.command()
@click.argument("chatid")
@with_app_context
def chat(chatid):
  """Set Telegram Chat ID"""
  set_telegramChat(chatid)

@set.command()
@click.argument("token")
@with_app_context
def token(token):
  """Set Telegram bot token"""
  set_telegramToken(token)

@set.command()
@click.argument("path")
@with_app_context
def log(path):
  """Set log file path"""
  set_logpath(path)

@set.command("ngx-folder")
@click.argument("path")
@with_app_context
def ngx_folder(path):
  """Set root folder for Nginx, e.g. /etc/nginx"""
  set_ngxFolder(path)

@set.command("ngx-add-conf")
@click.argument("path")
@with_app_context
def ngx_add_conf(path):
  """Set path to the folder with additional nginx redirect config files"""
  set_ngxAddConfDir(path)

# USER
@show_cli.group()
def user():
  """User management"""
  pass

@user.command("add")
@click.argument("username")
@click.argument("password")
@click.argument("realname")
@click.argument("rights", required=False, default="1")
@with_app_context
def user_add(username, password, realname, rights):
  """Add new user. Rights defaults to 1 (regular user), use 255 for admin."""
  register_user(username, password, realname, rights)

@user.command("del")
@click.argument("username")
@with_app_context
def user_del(username):
  """Delete an existing user"""
  delete_user(username)

@user.command("setpwd")
@click.argument("username")
@click.argument("password")
@with_app_context
def user_setpwd(username, password):
  """Change an existing user's password"""
  update_user(username, password)

@user.command("setadmin")
@click.argument("username")
@with_app_context
def user_setadmin(username):
  """Grant admin rights (255) to an existing user"""
  make_admin_user(username)

@user.command("unsetadmin")
@click.argument("username")
@with_app_context
def user_unsetadmin(username):
  """Remove admin rights from an existing user, back to regular (1)"""
  remove_admin_user(username)

# SHOW
@show_cli.group("show")
def show():
  """Show information"""
  pass

@show.command("users")
@with_app_context
def show_users_cmd():
  """Show all users"""
  show_users()

@show.command("config")
@with_app_context
def show_config_cmd():
  """Show current application configuration"""
  show_config()

# VERSION
@show_cli.command("version")
def show_version():
  """Show application version"""
  from main import VERSION
  click.echo(VERSION)
