import logging,os,subprocess,asyncio,re
from flask import current_app,flash
from functions.send_to_telegram import send_to_telegram
from flask_login import current_user
from datetime import datetime

def del_redirect(location: str,currDomain: str,redir_type: str) -> None:
    """Redirect-manager page: deletes one redirect,selected by Delete button on it.Don't applies changes immediately. Requires redirect "from location" and "sitename" as a parameter"""
    logging.info(f"-----------------------Deleting a single redirect for {currDomain} by {current_user.realname}-----------------")
    try:
        file301 = os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR'],redir_type+"-"+currDomain+".conf")
        #get into the site's config and uncomment one string        
        with open(file301, "r", encoding="utf-8") as f:
            content = f.read()
        escaped_path = re.escape(location.strip())
        pattern = re.compile(rf'location\s+.\s+{escaped_path}\s*{{.*?}}[\r\n]*',re.DOTALL)
        new_content, count = pattern.subn('', content)
        if count == 0:
            logging.error(f"Path {location} was not found in {file301} for site {currDomain}")
            flash(f"Path {location} was not found in {file301} for site {currDomain}",'alert alert-danger')
        else:
            with open(file301, "w", encoding="utf-8") as f:
                f.write(new_content)
            logging.info(f"Redirect path {location} of {currDomain} was deleted successfully")
    except Exception as msg:
        logging.error(f"Global Error:", "{msg}")
        asyncio.run(send_to_telegram(f"Global Error: {msg}",f"🚒Nginx Redirects Manager, Global Error:"))
    #here we create a marker file which makes "Apply changes" button to glow yellow
    if not os.path.exists("/tmp/ngx_redirects.marker"):
        with open("/tmp/ngx_redirects.marker", 'w',encoding='utf8') as file3:
            file3.write("")
            logging.info("Marker file for Apply button created")
    logging.info(f"-----------------------a single redirect for {currDomain} deleted---------------------------")

def del_selected_redirects(array: str,currDomain: str, redir_type: str) -> None:
    """Redirect-manager page: deletes array of selected by checkboxes redirects.Don't applies changes immediately. Requires redirect locations array and "sitename" as a parameter"""
    logging.info(f"-----------------------Deleting selected bulk redirects for {currDomain} by {current_user.realname}-----------------")
    try:
        file301 = os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR'],redir_type+"-"+currDomain+".conf")
        #start of parsing array() and remove selected routes
        for location in array:
            logging.info(f"Starting delete operation for {location}...")
            with open(file301, "r", encoding="utf-8") as f:
                content = f.read()
            escaped_path = re.escape(location.strip())
            pattern = re.compile(rf'location\s+.\s+{escaped_path}\s*{{.*?}}[\r\n]*',re.DOTALL)
            new_content, count = pattern.subn('', content)
            if count == 0:
                logging.error(f"Path {location} was not found in {file301} for site {currDomain}")
                flash(f"Path {location} was not found in {file301} for site {currDomain}",'alert alert-danger')
            else:
                with open(file301, "w", encoding="utf-8") as f:
                    f.write(new_content)
                logging.info(f"Redirect path {location} of {currDomain} was deleted successfully")
    except Exception as msg:
        logging.error(f"Global Error:", "{msg}")
        asyncio.run(send_to_telegram(f"Global Error: {msg}",f"🚒Nginx Redirects Manager, Global Error:"))
    #here we create a marker file which makes "Apply changes" button to glow yellow
    if not os.path.exists("/tmp/ngx_redirects.marker"):
        with open("/tmp/ngx_redirects.marker", 'w',encoding='utf8') as file3:
            file3.write("")
            logging.info("Marker file for Apply button created")
    logging.info(f"-----------------------Selected bulk redirects deleted---------------------------")

def applyChanges() -> None:
    """Redirect-manager page: applies all changes, made to redirect config files"""
    logging.info(f"-----------------------Applying changes in Nginx by {current_user.realname}-----------------")
    result1 = subprocess.run(["sudo","nginx","-t"], capture_output=True, text=True)
    if  re.search(r".*test is successful.*",result1.stderr) and re.search(r".*syntax is ok.*",result1.stderr):
        result2 = subprocess.run(["sudo","nginx","-s", "reload"], text=True, capture_output=True)
        if  re.search(r".*started.*",result2.stderr):
            logging.info(f"Nginx reloaded successfully. Result: {result2.stderr.strip()}")
            flash(f"Нові зміни успішно протестовано та застосовано на сервері!.",'alert alert-success')
        os.chdir(os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR']))
        #start of parsing array() and remove selected routes
        result2 = subprocess.run(["sudo","git","add","."], capture_output=True, text=True)
        if result2.returncode == 0:
            logging.info(f"Git add command successfull: {result2.stdout}")
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%d.%m.%Y %H:%M:%S")
            result2 = subprocess.run(["sudo","git","commit","-m", f"{formatted_datetime} by {current_user.realname}"], capture_output=True, text=True)
            if result2.returncode == 0:
                logging.info(f"Git commit command successfull: {result2.stdout}")
                if os.path.exists("/tmp/ngx_redirects.marker"):
                    os.unlink("/tmp/ngx_redirects.marker")
                logging.info(f"-----------------------Applying changes in Nginx finished-----------------")
            else:
                logging.error("Git commit failed!")
                asyncio.run(send_to_telegram(f"{current_user.realname}: Git commit error!",f"🚒Nginx Redirects Manager:"))
                logging.info(f"-----------------------Applying changes in Nginx finished-----------------")
        else:
            logging.error("Git add failed!")
            asyncio.run(send_to_telegram(f"Git add error!",f"🚒Nginx Redirects Manager:"))
            logging.info(f"-----------------------Applying changes in Nginx finished-----------------")
    else:
        logging.error(f"Error reloading Nginx: {result1.stderr.strip()}")
        asyncio.run(send_to_telegram(f"Changes apply error: Nginx has bad configuration",f"🚒Nginx Redirects Manager Error:"))
        flash(f"Помилка перевірки конфігурації!\n{result1.stderr.strip()}",'alert alert-danger')
        logging.info(f"-----------------------Applying changes in Nginx finished-----------------")

def rollBack() -> None:
    """Redirect-manager page: rollback all changes to the last Git commit"""
    logging.info(f"-----------------------Rolling back changes by {current_user.realname}-----------------")
    os.chdir(os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR']))
    result1 = subprocess.run(["sudo","git","restore","."], capture_output=True, text=True)
    if result1.returncode == 0:
        logging.info(f"--------------------Rollback command successfull!----------------------------------")
        flash(f"Всі зміни повернені на останній комміт!.",'alert alert-success')
        if os.path.exists("/tmp/ngx_redirects.marker"):
            os.unlink("/tmp/ngx_redirects.marker")
    else:
        logging.error(f"---------------------Git rollback failed!----------------------------------------")
        asyncio.run(send_to_telegram(f"{current_user.realname}: Git rollback error!",f"🚒Nginx Redirects Manager:"))
