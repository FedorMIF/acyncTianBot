# Используйте официальный образ Python
FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Укажите команду для запуска вашего приложения
CMD ["python", "./main_asinc.py"]