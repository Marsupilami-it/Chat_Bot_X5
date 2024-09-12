import requests
from fastapi import (
    FastAPI,
)
from .schemas import (
    GoogleSheetInfo,
    BatchAddition,
    VersionModel,
    Query
)
import uvicorn
import json
from .settings import ml_config
from cache.cache_service import CacheServer

ML_URL = f"{ml_config.ml_service_protocol}://{ml_config.ml_service_host}:{ml_config.ml_service_port}"

cache = CacheServer()

app = FastAPI(
    title='API Service',
    version='0.1',
    description="API для взаимодействия с чат-ботом",
    root_path="/api/v1"
)


@app.get(
    '/version',
    description='Возвращает версию API',
    responses={
        200: {'description': 'Версия API', 'content': {'application/json': {'example': '0.1.0'}}}
    }
)
async def get_version() -> VersionModel:
    return VersionModel(
        version=app.version
    )


@app.post(
    '/get_answer/',
    description='Возвращает ответ от модели на заданный вопрос'
)
async def get_answer(query: Query):
    cache_key = " ".join(str(q) for q in query.queries)
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response

    url = f"{ML_URL}/get_answer/"
    response = requests.post(url, json=query.dict())
    answer = response.json()

    # Сохраняем ответ в кэш
    # FIXME ответ лучше сохранять не строкой
    cache.set(cache_key, f"{answer}", expire=3600)  # час

    return answer


@app.post(
    '/add_from_sheet/',
    description='добавляет данные из Google Sheets'

)
async def add_from_sheet(data_sheet: GoogleSheetInfo):
    url = f"{ML_URL}/add_from_sheet/"
    response = requests.post(url, json=data_sheet.dict())
    return response.json()


@app.post(
    '/batch_add/',
    description=''

)
async def batch_add(batch: BatchAddition):
    url = f"{ML_URL}/batch_add/"
    response = requests.post(url, json=batch.dict())
    return response.json()


@app.post(
    '/clear_collection/',
    description='Очищает коллекцию'
)
async def clear_collection():
    url = f"{ML_URL}/clear_collection/"
    response = requests.post(url)
    return response.json()


@app.post(
    '/drop_collection/',
    description='Удаляет коллекцию'
)
async def drop_collection():
    url = f"{ML_URL}/drop_collection/"
    response = requests.post(url)
    return response.json()


@app.post(
    '/reset_database/',
    description=''
)
async def reset_database():
    url = f"{ML_URL}/reset_database/"
    response = requests.post(url)
    return response.json()


@app.post(
    '/test_ollama/',
    description=''
)
async def test_ollama(content: str):
    url = "http://ollama:11434/api/chat"
    payload = {
        "model": "gemma2:2b-instruct-q8_0",
        "messages": [
            {
                "role": "user",
                "content": f"{content}"
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


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8020)
