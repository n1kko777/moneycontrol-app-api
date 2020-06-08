#!/bin/bash
source /home/n1kko777/code/moneycontrol-app-api/env/bin/activate
exec gunicorn  -c "/home/n1kko777/code/moneycontrol-app-api/gunicorn_config.py" app.wsgi
