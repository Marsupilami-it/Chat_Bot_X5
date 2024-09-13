# AI-система с RAG

Эта система представляет собой комплексное решение, объединяющее искусственный интеллект (ИИ) и Retrieval-Augmented Generation (RAG) для обработки и генерации ответов на запросы пользователей.

## Компоненты системы

1. Сервис Ollama для работы с языковыми моделями
2. RAG сервис для улучшенной обработки запросов с использованием базы знаний
3. API для взаимодействия с системой

## API запросы

### 1. Сброс базы данных

```python
import requests

url = "http://localhost:8000/reset_database"
response = requests.post(url)
print(response.json())
```

Эта команда отправляет POST-запрос для сброса базы данных. После выполнения все коллекции в базе данных будут очищены.

### 2. Добавление данных из Google Sheets

```python
import requests

url = "http://localhost:8000/add_from_sheet"
sheet_data = {
    "sheet_id": "1qEormopG5VJDg9BfG4-d5kRBTdMPksRcN2sXar9Xepo",
    "gid": "0"
}
response = requests.post(url, json=sheet_data)
print(response.json())
```

Эта команда добавляет данные из указанной Google Sheets таблицы в базу данных. Ответ содержит информацию о количестве добавленных пар вопрос-ответ, пропущенных дубликатах и общем количестве строк в таблице.

### 3. Просмотр top N записей

```python
import requests

url = "http://localhost:8000/view_top_n"
params = {
    "n": 5  # Количество записей, которое вы хотите получить
}
response = requests.get(url, params=params)
print(response.json())
```

Эта команда позволяет просмотреть заданное количество (n) записей из базы данных.

### 4. Подсчет количества элементов в коллекции

```python
import requests

url = "http://localhost:8000/count_items"
response = requests.get(url)
print(response.json())
```

Эта команда возвращает количество элементов в коллекции базы данных.

### 5. Получение ответа с использованием RAG

```python
import requests

url = "http://localhost:8000/api/v1/get_answer/"
data = {
    "queries": ["как оформить материальную помощь родственникам мёртвого работника"],
    "n_results": 3
}
response = requests.post(url, json=data)
print(response.json())
```

Эта команда отправляет запрос в систему RAG и получает ответ на заданный вопрос, используя информацию из базы знаний.

### 6. Общение с моделью Gemma

```python
import requests
import json

def chat_with_gemma(prompt):
    url = "http://localhost:11434/api/chat/"
    payload = {
        "model": "gemma2:2b-instruct-q8_0",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

prompt = "Привет!"
response = chat_with_gemma(prompt)
print(f"Question: {prompt}")
print(f"Answer: {response}")
```

Эта функция позволяет отправлять запросы непосредственно модели Gemma через API Ollama. 

## Примечания

- Система использует модель gemma2:2b-instruct-q8_0 для Ollama.
- База данных (предположительно ChromaDB) используется для хранения и поиска документов в RAG компоненте.
- Все API-запросы в примерах направлены на localhost, что предполагает локальное развертывание сервисов.
- В случае ошибок при работе с Gemma (например, "модель не найдена"), убедитесь, что модель корректно установлена и настроена в вашем локальном окружении Ollama.

Для получения дополнительной информации о работе с Ollama, посетите [официальный репозиторий Ollama](https://github.com/ollama/ollama).