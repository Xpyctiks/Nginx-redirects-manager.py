from flask import render_template,request,redirect,flash,Blueprint,session,make_response
import logging
from flask_login import login_user, current_user
from db.database import User
from functions.send_to_telegram import send_to_telegram
from datetime import timedelta

login_bp = Blueprint("login", __name__)
@login_bp.route("/login", methods=['POST'])
def do_login():
  """POST request processor: logging in the user."""
  if current_user.is_authenticated:
    logging.info(f"POST: User {current_user.username} IP:{request.remote_addr} is already logged in. Redirecting to the main page.")
    return redirect('/',301)
  username = request.form["username"]
  password = request.form["password"]
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    session.clear()
    session.permanent = True
    session.permanent_session_lifetime = timedelta(hours=8)
    login_user(user, remember=True, duration=timedelta(hours=8))
    logging.info(f"User:{user.realname} IP:{request.remote_addr} logged in successfully")
    response = make_response(redirect("/",301))
    return response
  else:
    logging.error(f"Login: Wrong password \"{password}\" for user \"{username}\", IP:{request.remote_addr}")
    send_to_telegram(f"Login error.Wrong password for user {username}, IP:{request.remote_addr}","🚷Nginx-redirects-manager:",)
    flash('Wrong username or password!', 'alert alert-danger')
    return render_template("template-login.html")
 
@login_bp.route("/login", methods=['GET','POST'])
def show_login():
  """GET request: shows /login page"""
  if current_user.is_authenticated:
    logging.info(f"not POST: User {current_user.username} IP:{request.remote_addr} is already logged in. Redirecting to the main page.")
    return redirect('/',301)
  return render_template("template-login.html")
