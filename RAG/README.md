# RAG System - Инструкция по запуску и использованию

## Запуск сервиса
1. Загрузите контейнер, используя команду `docker pull an6rewus/rag_system`
2. Создайте файл `docker-compose.yml` с содержимым:
   ```
   services:
     rag_service:
      build:
        context: .
        dockerfile: Dockerfile
      image: rag_system:latest
      volumes:
        - chroma_data:/app/db
      ports:
        - "8000:8000"
      environment:
        - CHROMA_DB_PATH=/app/db
      restart: unless-stopped

   volumes:
     chroma_data:
       driver: local
   ```

3. В папке с файлом `docker-compose.yml` выполните:
   ```
   docker compose up
   ```

4. Сервис будет доступен по адресу `http://localhost:8000`.

## Использование API

### Добавление данных

Чтобы добавить данные из Google Sheets:

```python
import requests

url = "http://localhost:8000/add_from_sheet"
data = {
    "sheet_id": "your_google_sheet_id",
    "gid": "your_sheet_gid"
}

response = requests.post(url, json=data)
print(response.json())
```

### Выполнение запроса

Для выполнения запроса к базе данных:

```python
import requests

url = "http://localhost:8000/api/v1/get_answer/"
data = {
    "queries": ["запрос 1", "запрос 2"],
    "n_results": 3
}

response = requests.post(url, json=data)
print(response.json())
```

### Удаление всех данных

Для удаления всех данных из базы:

```python
import requests

url = "http://localhost:8000/reset_database"

response = requests.post(url)
print(response.json())
```

## Примечания

- Убедитесь, что у вас есть доступ к указанной Google Sheet.
- При первом запуске может потребоваться некоторое время для загрузки модели.
- Данные сохраняются в Docker volume, поэтому они будут доступны после перезапуска контейнера.