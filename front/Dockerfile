FROM python:3.9

WORKDIR /app

COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы в рабочую директорию контейнера
COPY . .

EXPOSE 8500

# Команда для запуска Streamlit на выбранном порту
CMD ["streamlit", "run", "app.py", "--server.port=8500", "--server.address=0.0.0.0"]
