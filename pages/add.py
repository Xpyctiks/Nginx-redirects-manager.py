from flask import render_template,request,redirect,flash,Blueprint,current_app
from flask_login import current_user, login_required
import logging,os
from werkzeug.utils import secure_filename

add_bp = Blueprint("add", __name__)
@add_bp.route("/add", methods=['GET','POST'])
@login_required
def uploadredir_file():
    if request.method == 'POST':
        currDomain = request.form.get('domain').strip()
        type = request.form.get('type').strip()
        logging.info(f"-----------------------Adding new redirects for {currDomain} by {current_user.realname}-----------------")
        #name of the redirect config file
        file301 = os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR'],type+"-"+currDomain+".conf")
        logging.info(f"Redirect config file: {file301}")
        #if this is submitted form and fileUpload[] exists in the request
        if request.form.get('addnewSubmit') and 'fileUpload' in request.files and not request.form.get('RedirectFromField') and not request.form.get('RedirectToField'):
            #get the list of files. saving them to the current folder. Redirect to /
            if request.form.get('templateField') == "strict":
                typeRedir = "="
            else:
                typeRedir = "~"
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
                    template = f"""location {typeRedir} {redirFrom} {{
rewrite ^(.*)$ https://{currDomain}{redirTo} permanent;
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
        elif request.form.get('addnewSubmit') and request.form.get('RedirectFromField') and request.form.get('RedirectToField') and request.form.get('templateField'):
            logging.info(f"-----------------------Adding new single redirect for {currDomain} by {current_user.realname}-----------------")
            logging.info(f"Redirect config file: {file301}")
            if request.form.get('templateField') == "strict":
                typeRedir = "="
            else:
                typeRedir = "~"
            logging.info(f"Type of redirect: {typeRedir}")
            logging.info(f"Redirect: From: {request.form.get('RedirectFromField').strip()} to {request.form.get('RedirectToField')}")
            template = f"""location {typeRedir} {request.form.get('RedirectFromField').strip()} {{
    rewrite ^(.*)$ https://{currDomain}{request.form.get('RedirectToField')} permanent;
}}
"""
            with open(file301, "a", encoding="utf-8") as f:
                f.write(template)
            #here we create a marker file which makes "Apply changes" button to glow yellow
            if not os.path.exists("/tmp/currDomain.marker"):
                with open("/tmp/currDomain.marker", 'w',encoding='utf8') as file3:
                    file3.write("")
                logging.info("Marker file for Apply button created")
            logging.info(f"-----------------------New redirect added successfully for {currDomain}-----------------")
            return redirect(f"/?domain={currDomain}&type={type}",301)
        else:
            logging.error("Some unknown error - not a file was uploaded and not single redirect was added. Looks like some fields are not set or messed.")
            flash("Some unknown error - not a file was uploaded and not single redirect was added. Looks like some fields are not set or messed.",'alert alert-danger')
            return redirect(f"/add?domain={currDomain}&type={type}",301)
    #if this is GET request - show page
    if request.method == 'GET':
        args = request.args
        currDomain = args.get('domain')
        type = args.get('type')
        return render_template("template-add.html",current_domain=currDomain,redirect_type=type)