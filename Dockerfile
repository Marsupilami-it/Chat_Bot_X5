FROM huggingface/transformers-torch-light

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY app.py .

# Создание директории для ChromaDB
RUN mkdir -p /app/data/chroma

# Указание порта
EXPOSE 8000

# Команда запуска приложения
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]