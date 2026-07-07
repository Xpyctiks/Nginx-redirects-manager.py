import logging
from flask import redirect,Blueprint,request,render_template,flash
from flask_login import login_required, current_user
from db.database import Settings,User
from functions.admin_panel_func import handler_settings,handler_users
from functions.rights_required import rights_required
from functions.site_actions import is_admin
from datetime import datetime

admin_panel_bp = Blueprint("admin_panel", __name__)

@admin_panel_bp.route("/admin_panel", methods=['POST'])
@login_required
@rights_required(255)
def catch_admin_panel():
  """POST request processor: process all requests to /admin_panel page and takes one of the chosen action."""
  try:
    if "buttonSaveSettings" in request.form:
      handler_settings(request.form)
      return redirect("/admin_panel/settings",302)
    elif "buttonAddUser" in request.form or "buttonDeleteUser" in request.form or "buttonEditUser" in request.form:
      handler_users(request.form)
      return redirect("/admin_panel/users",302)
    else:
      logging.error("Something strange was received by /admin_panel via POST request and we can't process that.")
      flash('Помилка! Ні один з можливих параметрів не був переданий сторінці /admin_panel в POST запиті!','alert alert-danger')
      return redirect("/admin_panel",302)
  except Exception as err:
    logging.error(f"catch_admin_panel(): global error {err}")
    flash('Загальна помилка адмін панелі! Дивіться логи.', 'alert alert-danger')
    return redirect("/",302)

@admin_panel_bp.route("/admin_panel", methods=['GET'])
@login_required
@rights_required(255)
def admin_panel():
  return redirect("/admin_panel/settings",302)

@admin_panel_bp.route("/admin_panel/settings", methods=['GET'])
@login_required
@rights_required(255)
def admin_panel_settings():
  try:
    html_data = """
<div class="card mx-auto" style="max-width: 80vw;" id="SettingsBlock">
  <form action="/admin_panel" method="POST" id="postform" novalidate>"""
    settings = Settings.query.all()
    i = 0
    for setting in settings:
      for column in setting.__table__.columns:
        if column.name == "id":
          continue
        value = getattr(setting, column.name) or ""
        html_data += f"""
<div class="input-group mb-2">
  <span class="input-group-text settings-label">{column.name}:</span>
  <input type="text" class="form-control" id="settings-{i}" value="{value}">
  <input type="hidden" id="value-{i}" name="{column.name}" value="">
</div>"""
        i = i + 1
    html_data += """
  <div class="d-grid mt-2 col-12 col-md-4 mx-auto">
    <button type="submit" class="btn form-control SaveSettings-btn w-100" style="background-color: palegreen;" name="buttonSaveSettings" onclick="syncSettings()">Зберегти налаштування</button>
  </div>
 </form>
</div>"""
    return render_template("template-admin_panel.html",active1="active",data=html_data,admin_panel=is_admin())
  except Exception as err:
    logging.error(f"admin_panel_settings(): global error {err}")
    flash('Загальна помилка відображення даних! Дивіться логи.', 'alert alert-danger')
    return redirect("/",302)

@admin_panel_bp.route("/admin_panel/users", methods=['GET'])
@login_required
@rights_required(255)
def admin_panel_users():
  try:
    html_data = """
<div class="card mx-auto" style="max-width: 80vw;" id="SettingsBlock">
  <table class="table table-bordered">
  <thead>
  <tr class="table-warning">
    <th scope="col" style="width: 45px;">ID:</th>
    <th scope="col" style="width: 150px;">Логін:</th>
    <th scope="col" style="width: 200px;">Ім'я:</th>
    <th scope="col" style="width: 200px;">Новий пароль:</th>
    <th scope="col" style="width: 90px;">Адмін:</th>
    <th scope="col" style="width: 150px;">Створен:</th>
    <th scope="col" style="width: 110px;">Дії:</th>
  </tr>
  </thead>
  <tbody>"""
    users = User.query.order_by(User.username).all()
    for s in users:
      checked = "checked" if s.rights == 255 else ""
      html_data += f"""
  <tr class="table-success">
    <form action="/admin_panel" method="POST" id="postform" novalidate>
    <td class="table-success cname-cell">{s.id}</td>
    <td class="table-success cname-cell">{s.username}</td>
    <td class="table-success cname-cell"><input type="text" class="form-control" name="edit-realname" value="{s.realname}"></td>
    <td class="table-success cname-cell"><input type="password" class="form-control" name="edit-password" placeholder="залиште пустим, щоб не міняти" value=""></td>
    <td class="table-success cname-cell text-center"><input class="form-check-input" type="checkbox" name="edit-is-admin" {checked}></td>
    <td class="table-success cname-cell">{datetime.strftime(s.created,"%d.%m.%Y %H:%M:%S")}</td>
    <td class="table-success cname-cell">
      <button type="submit" class="btn btn-outline-warning EditUser-btn" name="buttonEditUser" onclick="showLoading()" value="{s.id}" title="Зберегти зміни">💾</button>
      <button type="submit" class="btn btn-outline-warning DeleteUser-btn" name="buttonDeleteUser" onclick="showLoading()" value="{s.id}" title="Видалити даного користувача із бази.">❌</button>
    </td>
    </form>
  </tr>"""
    html_data += """
  </tbody>
  </table>
  <form action="/admin_panel" method="POST" id="postform2" class="needs-validation" novalidate>
  <div class="input-group mb-2">
  <span class="input-group-text">Логін:</span>
  <input type="text" class="form-control" id="new-username" name="new-username" value="">
  <span class="input-group-text">Пароль:</span>
  <input type="text" class="form-control" id="new-password" name="new-password" value="">
  <span class="input-group-text">І'мя</span>
  <input type="text" class="form-control" id="new-realname" name="new-realname" value="">
  <span class="input-group-text">Адмін права&nbsp;<input class="form-check-input" type="checkbox" value="" name="new-is-admin"></span>
  <button type="submit" class="btn form-control" style="background-color: palegreen;" name="buttonAddUser" onclick="showLoading()">Створити користувача</button>
   </div>
  </form>
 </div>
</div>"""
    return render_template("template-admin_panel.html",active2="active",data=html_data,admin_panel=is_admin())
  except Exception as err:
    logging.error(f"admin_panel_users(): global error {err}")
    flash('Загальна помилка відображення даних! Дивіться логи.', 'alert alert-danger')
    return redirect("/",302)
