#!/bin/bash
source /home/www/code/moneycontrol-app-api/env/bin/activate
source /home/www/code/moneycontrol-app-api/env/bin/postactivate
exec gunicorn  -c "/home/www/code/moneycontrol-app-api/gunicorn_config.py" app.wsgi
