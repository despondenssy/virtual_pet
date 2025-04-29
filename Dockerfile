# Используем официальный Python-образ
FROM python:3.13

# Устанавливаем рабочую директорию (создаём рабочую папку внутри контейнера)
WORKDIR /app

# Отключаем кеширование .pyc файлов и буферизацию вывода (для удобства разработки)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Обновляем pip
RUN pip install --upgrade pip

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект внутрь контейнера
COPY . /app/

# Открываем порт 8080
EXPOSE 8080

# Запускаем сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
