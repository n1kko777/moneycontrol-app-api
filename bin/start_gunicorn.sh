#!bin/bash
source /root/code/moneycontrol-app-api/env/bin/activate 
exec gunicorn -c "/root/code/moneycontrol-app-api/app/gunicorn_config.py" app.wsgi 

