from flask import flash
from flask_login import current_user
import logging
from db.database import db,User,Settings
from werkzeug.security import generate_password_hash
from functions.rights_required import rights_required

@rights_required(255)
def handler_settings(form):
  """Handler for saving global settings to DB, received from admin panel"""
  logging.info(f"---------------------------Processing global settings from admin panel by {current_user.realname}---------------------------")
  try:
    for db_field in form:
      #skip processing of the button
      if db_field == "buttonSaveSettings":
        continue
      data = {"id": 1, db_field: form.get(db_field)}
      t = Settings(**data)
      db.session.merge(t)
    db.session.commit()
    logging.info(f"Admin {current_user.realname}>Saving global settings done---------------------------")
    flash('Нові параметри збережено та застосовано!','alert alert-success')
  except Exception as err:
    logging.error(f"Admin {current_user.realname}>handler_settings() global error: {err}")
    flash('Помилка збереження параметрів программи!','alert alert-danger')
    return

@rights_required(255)
def handler_users(form):
  """Handler for adding/editing/deleting users to DB, received from admin panel"""
  logging.info(f"---------------------------Processing user management from admin panel by {current_user.realname}---------------------------")
  try:
    #processing delete user request
    if "buttonDeleteUser" in form:
      id = int(form.get('buttonDeleteUser').strip())
      if id == current_user.id:
        logging.warning(f"Admin {current_user.realname}>Attempted to delete his own account!")
        flash('Ви не можете видалити самого себе!','alert alert-warning')
        return
      user = User.query.filter_by(id=id).first()
      if user:
        db.session.delete(user)
        db.session.commit()
        logging.info(f"Admin {current_user.realname}>User {user.username} with ID {id} deleted successfully!")
        flash(f'Користувач {user.username} з ID {id} успішно видален!','alert alert-success')
      else:
        logging.error(f"Admin {current_user.realname}>User with ID {id} deletion error - no such user!")
        flash(f'Помилка видалення користувача з ID {id} - такого не існує!','alert alert-warning')
      return
    #processing add user request
    elif "buttonAddUser" in form:
      username = form.get("new-username", "").strip()
      realname = form.get("new-realname", "").strip()
      password = form.get("new-password", "").strip()
      if not username or not realname or not password:
        logging.error(f"Admin {current_user.realname}>Some of important parameters for user add procedure has not been received!")
        flash('Один або декілька важливих параметрів для створення користувача не були отримані сервером!','alert alert-warning')
        return
      if User.query.filter_by(username=username).first():
        logging.error(f"Admin {current_user.realname}>User {username} creation error - already exists!")
        flash(f'Користувач {username} вже існує!','alert alert-danger')
        return
      rights = 255 if "new-is-admin" in form else 1
      data = {"username": username, "realname": realname, "password_hash": generate_password_hash(password), "rights": rights}
      new_user = User(**data)
      db.session.add(new_user)
      db.session.commit()
      logging.info(f"Admin {current_user.realname}>User {username} created successfully! Rights: {rights}")
      flash(f'Користувач {username} успішно створен!','alert alert-success')
      return
    #processing edit user request - realname, password and admin rights, all optional except keeping at least one admin
    elif "buttonEditUser" in form:
      id = int(form.get('buttonEditUser').strip())
      user = User.query.filter_by(id=id).first()
      if not user:
        logging.error(f"Admin {current_user.realname}>User with ID {id} edit error - no such user!")
        flash(f'Помилка редагування користувача з ID {id} - такого не існує!','alert alert-warning')
        return
      new_realname = form.get("edit-realname", "").strip()
      new_password = form.get("edit-password", "").strip()
      new_is_admin = "edit-is-admin" in form
      if user.id == current_user.id and not new_is_admin:
        logging.warning(f"Admin {current_user.realname}>Attempted to remove admin rights from his own account!")
        flash('Ви не можете зняти адмін права із самого себе!','alert alert-warning')
        return
      if new_realname:
        user.realname = new_realname
      if new_password:
        user.password_hash = generate_password_hash(new_password)
      user.rights = 255 if new_is_admin else 1
      db.session.commit()
      logging.info(f"Admin {current_user.realname}>User {user.username} with ID {id} updated successfully!")
      flash(f'Користувач {user.username} успішно оновлений!','alert alert-success')
      return
  except Exception as err:
    logging.error(f"Admin {current_user.realname}>handler_users() global error: {err}")
    flash('Помилка обробки функцій користувачів!','alert alert-danger')
    return
