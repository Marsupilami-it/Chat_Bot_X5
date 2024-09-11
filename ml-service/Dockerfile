FROM huggingface/transformers-torch-light

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY src/ml_service/ .
#COPY src/ml_service/app.py .

# Создание директории для ChromaDB
RUN mkdir -p /app/data/chroma

# Создание директории для кэша моделей
RUN mkdir -p /root/.cache/huggingface

# Установка переменной окружения для кэша моделей
ENV HF_HOME=/root/.cache/huggingface

# Указание порта
EXPOSE 7000

# Команда запуска приложения
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]