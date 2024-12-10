# Используем базовый образ Python
FROM python:3.10-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y build-essential libpq-dev --no-install-recommends

# Указываем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . /app/

# Устанавливаем переменные окружения по умолчанию
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
