FROM python:3.13.7-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем проект
COPY . .

# Экспорт переменной окружения для Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ingestion.settings

# Запуск сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]