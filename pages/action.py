from flask import redirect,Blueprint,request
from flask_login import login_required
from functions.site_actions import del_redirect, del_selected_redirects, applyChanges

action_bp = Blueprint("action", __name__)
@action_bp.route("/action", methods=['POST'])
@login_required
def do_action():
    if (request.form.get('selected')):
        array = request.form.getlist("selected")
        del_selected_redirects(array,request.form['sitename'].strip(),request.form['redir_type'].strip())
        return redirect(f"/?domain={request.form['sitename'].strip()}&type={request.form['redir_type'].strip()}",301)
    elif (request.form.get('del_redir')):
        del_redirect(request.form['del_redir'].strip(),request.form['sitename'].strip(),request.form['redir_type'].strip())
        return redirect(f"/?domain={request.form['sitename'].strip()}&type={request.form['redir_type'].strip()}",301)
    elif (request.form.get('applyChanges')):
        applyChanges(request.form['sitename'].strip(),request.form['redir_type'].strip())
        return redirect(f"/?domain={request.form['sitename'].strip()}&type={request.form['redir_type'].strip()}",301)
    else:
        return redirect("/",301)
