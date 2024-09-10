import requests
import json

BASE_URL = "http://84.252.136.229:8000"

def call_api(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if data:
            response = requests.post(url, json=data)
        else:
            response = requests.post(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при вызове API {endpoint}: {str(e)}")
        if response:
            print(f"Ответ сервера: {response.text}")
        return None

# 3. Отправка запроса
query_data = {
    "queries": ["не корректно проставлен день"],
               # "мне нужно указать другие дни в расписании работника",
               # "не корректно проставлен день. мне нужно указать другие дни в расписании работника"],
    "n_results": 3
}
result = call_api("/api/v1/get_answer/", query_data)
print(result)