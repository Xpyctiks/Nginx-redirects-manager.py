from flask import render_template,request,redirect,flash,Blueprint,current_app
from flask_login import current_user, login_required
import logging,os,re
from werkzeug.utils import secure_filename

add_bp = Blueprint("add", __name__)
@add_bp.route("/add", methods=['POST'])
@login_required
def uploadredir_file():
  """POST request processor: getting uploaded CSV file and takes redirects from it."""
  currDomain = request.form.get('domain').strip()
  type = request.form.get('type').strip()
  redirectFrom = request.form.get("RedirectFromField","").strip()
  redirectTo = request.form.get("RedirectToField","").strip()
  logging.info(f"-----------------------Adding new redirects for {currDomain} by {current_user.realname}-----------------")
  #name of the redirect config file
  file301 = os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR'],type+"-"+currDomain+".conf")
  logging.info(f"Redirect config file: {file301}")
  #if this is submitted form and fileUpload[] exists in the request
  if request.form.get('addnewSubmit') and 'fileUpload' in request.files and not redirectFrom and not redirectTo:
    #get the list of files. saving them to the current folder. Redirect to /
    if request.form.get("templateField","") == "strict":
      typeRedir = "="
    elif request.form.get("templateField","") == "catch_all":
      typeRedir = "~"
    else:
      logging.error(f"uploadredir_file(): templateField is empty or contains something strange")
      flash("Помилка! Дивіться логи!",'alert alert-danger')
      return redirect(f"/add?domain={currDomain}&type={type}",301)
    logging.info(f"CSV file with redirects uploaded. Type of redirects: {typeRedir}")
    redirectsCount = 0
    file = request.files["fileUpload"]
    filename = os.path.join("/tmp/",secure_filename(file.filename))
    file.save(filename)
    logging.info(f"Uploaded file: {filename}")
    totalData = ""
    with open(filename, "r", encoding="utf-8") as redirectsFile:
      for line in redirectsFile:
        redirFrom, redirTo = line.strip().split(",")
        if re.match("https:",redirTo):
          template = f"""location {typeRedir} {redirFrom} {{
  return 301 {redirTo};
}}
"""
        else:
          template = f"""location {typeRedir} {redirFrom} {{
  return 301 https://{currDomain}{redirTo};
}}
"""            
        totalData += template
        redirectsCount = redirectsCount + 1
    #now write down all redirects to the file
    with open(file301, "a", encoding="utf-8") as f:
      f.write(totalData)
    logging.info(f"New redirects were saved to {file301}")
    os.unlink(filename)
    logging.info(f"Uploaded CSV file {filename} was deleted")
    #here we create a marker file which makes "Apply changes" button to glow yellow
    if not os.path.exists("/tmp/ngx_redirects.marker"):
        with open("/tmp/ngx_redirects.marker", 'w',encoding='utf8') as file3:
          file3.write("")
        logging.info("Marker file for Apply button created")
    flash(f"{redirectsCount} redirects added successfully!", 'alert alert-success')
    logging.info(f"-----------------------New redirects added successfully for {currDomain}-----------------")
    return redirect(f"/?domain={currDomain}&type={type}",301)
  #if this is submitted form and single redirect lines exist there
  elif request.form.get('addnewSubmit') and redirectFrom and redirectTo and request.form.get('templateField'):
    logging.info(f"-----------------------Adding new single redirect for {currDomain} by {current_user.realname}-----------------")
    logging.info(f"Redirect config file: {file301}")
    if request.form.get("templateField","") == "strict":
      typeRedir = "="
    elif request.form.get("templateField","") == "catch_all":
      typeRedir = "~"
    else:
      logging.error(f"uploadredir_file(): templateField is empty or contains something strange")
      flash("Помилка! Дивіться логи!",'alert alert-danger')
      return redirect(f"/add?domain={currDomain}&type={type}",301)
    logging.info(f"Type of redirect: {typeRedir}")
    logging.info(f"Redirect: From: {redirectFrom} to {redirectTo}")
    if re.match("https:",redirectTo):
      logging.info(f"uploadredir_file(): Redirect filed To: contains full FQDN address")
      template = f"""location {typeRedir} {redirectFrom} {{
  return 301 {redirectTo};
}}
"""
    else:
      logging.info(f"uploadredir_file(): Redirect filed To: contains relative path for the source domain")
      template = f"""location {typeRedir} {redirectFrom.strip()} {{
  return 301 https://{currDomain}{redirectTo};
}}
"""        
    with open(file301, "a", encoding="utf-8") as f:
      f.write(template)
    #here we create a marker file which makes "Apply changes" button to glow yellow
    if not os.path.exists("/tmp/ngx_redirects.marker"):
      with open("/tmp/ngx_redirects.marker", 'w',encoding='utf8') as file3:
        file3.write("")
      logging.info("Marker file for Apply button created")
    logging.info(f"-----------------------New redirect added successfully for {currDomain}-----------------")
    return redirect(f"/?domain={currDomain}&type={type}",301)

@add_bp.route("/add", methods=['GET'])
@login_required
def show_uploadredir_file():
  """GET request: show /upload_redirects page."""
  args = request.args
  currDomain = args.get('domain')
  type = args.get('type')
  return render_template("template-add.html",current_domain=currDomain,redirect_type=type)
