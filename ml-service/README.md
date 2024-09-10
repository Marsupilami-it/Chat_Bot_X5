# AI-система с RAG

Эта система представляет собой комплексное решение, объединяющее искусственный интеллект (ИИ) и Retrieval-Augmented Generation (RAG) для обработки и генерации ответов на запросы пользователей.

## Компоненты системы

1. Сервис Ollama для работы с языковыми моделями
2. RAG сервис для улучшенной обработки запросов с использованием базы знаний
3. API для взаимодействия с системой

## Запуск сервиса

### Подготовка

1. Убедитесь, что у вас установлен Docker и Docker Compose.
2. Клонируйте репозиторий и перейдите в директорию проекта.

### Запуск без GPU

Для запуска сервиса без использования GPU выполните следующую команду:

```bash
docker-compose -f ml-service/docker-compose_no_gpu.yml up -d
```

### Запуск с GPU (NVIDIA)

Для запуска сервиса с использованием GPU NVIDIA:

1. Установите NVIDIA Container Toolkit (инструкции в предыдущей версии README).
2. Настройте Docker для использования NVIDIA драйвера.
3. Запустите сервис:

```bash
docker-compose -f ml-service/docker-compose.yml up -d
```

## API запросы

### 1. Сброс базы данных

```python
import requests

url = "http://51.250.106.51:8000/reset_database"
response = requests.post(url)
print(response.json())
```

### 2. Добавление данных из Google Sheets

```python
import requests

url = "http://51.250.106.51:8000/add_from_sheet"
data = {
    "sheet_id": "1qEormopG5VJDg9BfG4-d5kRBTdMPksRcN2sXar9Xepo",
    "gid": "0"
}
response = requests.post(url, json=data)
result = response.json()
print(f"Добавлено документов: {result['new_docs_count']}")
print(f"Пропущено дубликатов: {result['duplicates_skipped']}")
print(f"Всего строк в таблице: {result['total_rows_in_sheet']}")
```

### 3. Получение ответа с использованием RAG

```python
import requests

url = "http://51.250.106.51:8000/api/v1/get_answer/"
data = {
    "queries": ["как оформить материальную помощь родственникам мёртвого работника"],
    "n_results": 3
}
response = requests.post(url, json=data)
print(response.json())
```

### 4. Общение с моделью Gemma

```python
import requests
import json

url = "http://51.250.106.51:11434/api/chat"
payload = {
    "model": "gemma2:2b-instruct-q8_0",
    "messages": [
        {
            "role": "user",
            "content": "Привет!"
        }
    ],
    "stream": False
}
headers = {
    "Content-Type": "application/json"
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
if response.status_code == 200:
    print(response.json()["message"]["content"])
else:
    print(f"Error: {response.status_code}, {response.text}")
```

## Примечания

- Система использует модель gemma2:2b-instruct-q8_0 для Ollama.
- База данных ChromaDB используется для хранения и поиска документов в RAG компоненте.
- Модели Hugging Face кэшируются в отдельном томе Docker для ускорения загрузки.

Для получения дополнительной информации о работе с Ollama, посетите [официальный репозиторий Ollama](https://github.com/ollama/ollama).