import requests
import json

BASE_URL = "http://localhost:8000"

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
print("\n2. Добавление данных из Google Sheets...")
sheet_data = {
    "sheet_id": "1qEormopG5VJDg9BfG4-d5kRBTdMPksRcN2sXar9Xepo",
    "gid": "0"
}
result = call_api("/add_from_sheet", sheet_data)
if result:
    print(f"Добавлено документов: {result['new_docs_count']}")
    print(f"Пропущено дубликатов: {result['duplicates_skipped']}")
    print(f"Всего строк в таблице: {result['total_rows_in_sheet']}")
    
query_data = {
    "queries": ["сотрудник не запланироавал отпуск"],
    
    "n_results": 8
}
result = call_api("/api/v1/get_answer/", query_data)
print(result)