# Используем базовый образ Python
FROM python:3.10-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y libpq-dev gcc

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения
COPY . /app

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Выполняем миграции базы данных
RUN python manage.py migrate

# Указываем команду для запуска приложения
CMD ["gunicorn", "--workers", "5", "--timeout", "1200", "app.wsgi"]
