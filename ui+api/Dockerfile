# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код API и UI
COPY outter_api.py .
COPY ui.py .

# Создаем скрипт для запуска обоих сервисов
RUN echo '#!/bin/bash\n\
python outter_api.py &\n\
streamlit run ui.py --server.port=8501 --server.address=0.0.0.0\n\
' > start_services.sh && chmod +x start_services.sh

# Открываем порты для API и UI
EXPOSE 8003 8501

# Запускаем оба сервиса при старте контейнера
CMD ["./start_services.sh"]