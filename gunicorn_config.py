command = '/home/n1kko777/code/moneycontrol-app-api/env/bin/gunicorn'
pythonpath = '/home/n1kko777/code/moneycontrol-app-api/app'
bind = '127.0.0.1:8001'
workers = 3
user = 'n1kko777'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=app.settings'
