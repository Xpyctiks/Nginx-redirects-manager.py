from flask import render_template,Blueprint
from flask_login import login_required
from flask import render_template,request,redirect,flash,Blueprint,current_app
from functions.site_actions import enable_allredirects, disable_allredirects
import re,os

root_bp = Blueprint("root", __name__)
@root_bp.route("/", methods=['GET'])
@login_required
def root():
    if request.method == 'POST':
        if not request.form.get('manager') and request.form.get('redirect_checkbox'):
            #parsing list of "redirect_checkbox" values because there can be 2 at the same time
            values = request.form.getlist("redirect_checkbox")
            checkbox_enabled = "1" in values
            if checkbox_enabled:
                enable_allredirects(request.form.get("sitename").strip())
                return redirect("/",301)
            else:
                disable_allredirects(request.form.get("sitename").strip())
                return redirect("/",301)
        else:
            return redirect("/",301)
    #if this is GET request - show page
    if request.method == 'GET':
        table = currDomain = type = ""
        domainsList = set()
        redirectsList = set()
        args = request.args
        currDomain = args.get('domain')
        type = args.get('type')
        #First of all parsing content of NGX_ADD_CONF_DIR for files - format <redirect_type>-<domain>.conf. For example, 301-site.com.conf
        configs = os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR'])
        pattern = re.compile(r"^(\d+)-(.+)\.conf$")
        for filename in os.listdir(configs):
            match = pattern.match(filename)
            if match:
                domain = match.group(2)
                domainsList.add(domain)
        domainsList = sorted(domainsList)
        html_domains = "".join(f'<li><a class="dropdown-item" href="?domain={d}">{d}</a></li>' for d in domainsList)
        #Get info about current Git commit
        current_commit = ""
        gitFile = os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR'],".git/COMMIT_EDITMSG")
        try:
            with open(gitFile, "r", encoding="utf-8") as f:
                current_commit = f.readline()
        except Exception:
            current_commit = "ERROR!"
        #if no Domain and Type set
        if (not args.get('domain') and not args.get('type')):
            table +="""<tr class="alert alert-info" role="info"><td colspan="7">Будьласка, спочатку оберіть домен</td></tr>"""
            currDomain = "Оберіть домен"
            type = "Оберіть тип"
            html_redirect_types = ""
            total_lines = total_redirects = "0"
        #if Domain set but Type is not
        elif (args.get('domain') and not args.get('type')):
            table +="""<tr class="alert alert-info" role="info"><td colspan="7">Будьласка, оберіть тип редіректу</td></tr>"""
            currDomain = args.get('domain')
            type = "Оберіть тип"
            total_lines = total_redirects = "0"
            for filename in os.listdir(configs):
                match = pattern.match(filename)
                if match:
                    r_type = int(match.group(1))
                    domain_name = match.group(2)
                    if domain_name == currDomain:
                        redirectsList.add(r_type)
                html_redirect_types = "".join(f'<li><a class="dropdown-item" href="?domain={currDomain}&type={t}">{t}</a></li>' for t in redirectsList)
        #if all are set and we can proceed
        elif (args.get('domain') and args.get('type')):
            currDomain = args.get('domain')
            type = args.get('type')
            #once again parsing available redirects list for the current domain
            for filename in os.listdir(configs):
                match = pattern.match(filename)
                if match:
                    r_type = int(match.group(1))
                    domain_name = match.group(2)
                    if domain_name == currDomain:
                        redirectsList.add(r_type)
                html_redirect_types = "".join(f'<li><a class="dropdown-item" href="?domain={currDomain}&type={t}">{t}</a></li>' for t in redirectsList)
            i = 1
            currFile=os.path.join(current_app.config['NGX_FOLDER'],current_app.config['NGX_ADD_CONF_DIR'],type+"-"+currDomain+".conf")
            with open(currFile, "r", encoding="utf-8") as f:
                content = f.read()
            #check if the config file has any records
            if len(content) == 0:
                table +="""<tr class="alert alert-info" role="info"><td colspan="7">В цьому файлі ще нема редіректів...</td></tr>"""
                total_lines = total_redirects = "0"
            else:
                pattern = re.compile(r'location\s+(?P<typ>=|~|\~\*)\s+(?P<path>/[^\s{]+)\s*{[^}]*?rewrite\s+\^\(\.\*\)\$\s+(?P<target>https?://[^\s]+)\s+permanent;',re.MULTILINE | re.DOTALL)
                for match in pattern.finditer(content):
                    start_index = match.start()
                    line_number = content.count('\n', 0, start_index) + 1
                    if (match.group("typ")) == "=":
                        typ = "Точна одна сторінка (=)"
                    elif (match.group("typ")) == "~":
                        typ = "Захват усього (~)"
                    table += f"""\n<tr>\n
                    <th scope="row" class="table-success">{i}</th>
                    <td class="table-success">{match.group("path")}</td>
                    <td class="table-success"><input class="form-check-input chk" type="checkbox" name="selected" value="{match.group("path")}"></td>
                    <td class="table-success">{match.group("target")}</td>
                    <td class="table-success">{typ}</td>
                    <td class="table-success">
                        <button class="btn btn-danger" type="submit" name="del_redir" value="{match.group("path")}">Видалити</button>
                        <input type="hidden" name="sitename" value="{domain}">
                    </td>
                    <td class="table-success">{line_number}</td>
                    \n</tr>"""
                    i = i+1
                total_redirects = i-1
                total_lines = 0
                #Counts total number of strings processed in the file
                with open(currFile, "r", encoding="utf-8") as f:
                    for line in f:
                        total_lines = total_lines+1
        #here we check file marker to make Apply button glow yellow if there is something to apply
        if os.path.exists("/tmp/provision.marker"):
            applyButton = "btn btn-success"
            applyButtonDisabled = ""
        else:
            applyButton = "btn btn-outline-warning"
            applyButtonDisabled = "disabled"
        return render_template("template-root.html",table=table,current_domain=currDomain,redirect_type=type,redirectsList=html_redirect_types,domainsList=html_domains,applyButton=applyButton,
                               total_lines=total_lines,total_redirects=total_redirects,current_commit=current_commit,applyButtonDisabled=applyButtonDisabled)
