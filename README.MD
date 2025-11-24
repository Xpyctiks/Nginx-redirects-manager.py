-Python web application with CLI functions allows to manage Nginx redirects in config files.
-Uses sqlite3 DB to store options.  
-User management and cache path management via CLI.  
-Sending important alerts or notoification to Telegram if ChatID and Token are set.  

# Gunicorn settings  
-Systemd unit (for example: /etc/systemd/system/gunicorn-ngx-redir-mgr.service). Change to yours:
```
[Unit]
Description=Gunicorn instance for main.py
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/Nginx-redirects-manager.py
Environment="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/bin/gunicorn -c /opt/Nginx-redirects-manager.py/gunicorn_config.py main:application
StandardOutput=append:/var/log/gunicorn/ngx-redir-mgr.log
StandardError=append:/var/log/gunicorn/ngx-redir-mgr-error.log

[Install]
WantedBy=multi-user.target
```
-Gunicorn file(gunicorn_config.py).Change to yours if anything:  
```
import sys
import os

#change to yours
venv_path = "/usr/local/"
sys.path.insert(0, os.path.join(venv_path, "lib/python3.11/site-packages"))
#change to yours
sys.path.insert(0, "/opt/Nginx-redirects-manager.py")

bind = "127.0.0.1:8882"
workers = 3
timeout = 30
loglevel = "info"
wsgi_app = "main:application"

```