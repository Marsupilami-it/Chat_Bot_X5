from typing import List, Dict, Any
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

BASE_URL = '62.68.146.67'
ip = BASE_URL


def remove_role_messages(history, role="assistant", n=2):
    """
    Удаляет все сообщения указанной роли, кроме последних N.
    
    :param history: список сообщений, содержащих "role" и "content"
    :param role: роль, сообщения которой нужно удалить (например, "assistant")
    :param n: количество последних сообщений этой роли, которые нужно оставить
    :return: список сообщений с удалёнными сообщениями указанной роли
    """
    # Собираем все индексы сообщений указанной роли
    role_indices = [i for i, message in enumerate(
        history) if message['role'] == role]

    # Оставляем последние N индексов для сохранения
    indices_to_keep = role_indices[-n:]

    # Формируем новый список, удаляя все сообщения роли, кроме последних N
    new_history = [message for i, message in enumerate(
        history) if message['role'] != role or i in indices_to_keep]

    return new_history


# Пример использования
dialogue_history = [
    {"role": "assistant", "content": "Привет! Чат-бот компании Х5. Чем я могу помочь?"},
    {"role": "user", "content": "123"},
    {"role": "assistant", "content": "Ответ!!!"},
    {"role": "user", "content": "578"},
    {"role": "assistant", "content": "Ответ!!!"},
    {"role": "user", "content": "9087"},
    {"role": "assistant", "content": "Ответ!!!"}
]

# Удалим все ответы ассистента, кроме последних 2
result_history = remove_role_messages(dialogue_history, 'assistant', 2)

# Вывод обновленной истории
print(result_history)


def process_history(history: List[Dict[str, str]], ip: str, N: int = 2, M: int = 3) -> List[Dict[str, str]]:
    # Получаем последние N сообщений пользователя
    user_messages = [msg["content"]
                     for msg in history if msg["role"] == "user"][-N:]

    # Получаем конкатенацию последних M сообщений (всех ролей)
    all_messages = " ".join([msg["content"] for msg in history[-M:]])

    # Формируем список запросов для RAG
    queries = user_messages + [all_messages]

    # Выполняем запрос к RAG
    rag_results = rag_query(ip, queries, n_results=5)

    # Обрабатываем результаты RAG
    processed_results = []
    seen_pairs = set()  # Для отслеживания уникальных пар вопрос-ответ

    for query_result in rag_results['results']:
        for result in query_result['results']:
            qa_pair = (result['question'], result['answer'])
            if qa_pair not in seen_pairs:
                processed_results.append({
                    'question': result['question'],
                    'answer': result['answer']
                })
                seen_pairs.add(qa_pair)

    return processed_results


def create_condensed_qa_prompt(user_question: str, qa_pairs: List[Dict[str, str]]) -> str:
    """
    Create a condensed prompt from a list of question-answer dictionaries,
    grouping questions with identical answers, and including the latest user question.
    """
    prompt = f'Вопрос от пользователя: "{user_question}"\n\nРелевантные вопросы и ответы из базы знаний:\n'

    # Group questions by their answers
    answer_to_questions = defaultdict(list)
    for pair in qa_pairs:
        answer_to_questions[pair['answer']].append(pair['question'])

    # Create condensed Q&A pairs
    for i, (answer, questions) in enumerate(answer_to_questions.items(), 1):
        if len(questions) > 1:
            formatted_questions = ', '.join(f'"{q}"' for q in questions)
            prompt += f"#{i}. Для вопросов: {formatted_questions}\n   Ответ: {answer}\n\n"
        else:
            prompt += f"#{i}. \"{questions[0]}\"\n   Ответ: {answer}\n\n"

    prompt += '''
Задача: Основываясь на вспомогательных материалах корпоративной базы знаний компании x5 retail group, развёрнуто и чётко ответить на вопрос пользователя. 
Важно, что вспомогательные данные не всегда ранжированы по релевантности. 
Среди примеров может не быть верного ответа! 
Если ты считаешь, вопрос пользователя релевантен вопросу из базы знаний, дай соответствующий ответ. 
Тебе необходимо ответить на вопрос. Объяснять, почему ты выбрал именно это вариант из базы не нужно. 
Если ты считаешь, что в предоставленных данных не содержится ответа на вопрос, то нужно ответить, что тебе дали слишком мало конкретики. Попроси описать проблему подробнее. 
Если в вспомогательных данных есть несколько вопросов, которые релевантны данному, задай уточняющий вопрос, чтобы понять, какой из вопросов больше подходит.
При ответе на вопрос ничего лишнего не пиши. Только сам ответ или уточняющее предложение.
Ответ должен быть полным, как в базе знаний. Из базы знаний нужно выбрать лишь один ответ!
Отвечай только на русском языке.'''

    return prompt


def remove_role_messages(history, role="assistant", n=2):
    """
    Удаляет все сообщения указанной роли, кроме последних N.
    
    :param history: список сообщений, содержащих "role" и "content"
    :param role: роль, сообщения которой нужно удалить (например, "assistant")
    :param n: количество последних сообщений этой роли, которые нужно оставить
    :return: список сообщений с удалёнными сообщениями указанной роли
    """
    # Собираем все индексы сообщений указанной роли
    role_indices = [i for i, message in enumerate(
        history) if message['role'] == role]

    # Оставляем последние N индексов для сохранения
    indices_to_keep = role_indices[-n:]

    # Формируем новый список, удаляя все сообщения роли, кроме последних N
    new_history = [message for i, message in enumerate(
        history) if message['role'] != role or i in indices_to_keep]

    return new_history

@app.post("/api/v1/get_answer/")
async def query(chat_history):
    # Нахождение релевантной информации
    result = process_history(chat_history, ip)
    # Создание сообщения пользователя
    res = create_condensed_qa_prompt(chat_history[-1]['content'], result)
    # Формирование истории
    result_history = remove_role_messages(chat_history, 'assistant', 2)
    result_history = result_history[:-1]
    result_history.append({'role': 'user', 'content': res})
    return result_history


def create_condensed_qa_prompt(user_question: str, qa_pairs: List[Dict[str, str]]) -> str:
    """
    Create a condensed prompt from a list of question-answer dictionaries,
    grouping questions with identical answers, and including the latest user question.
    """
    prompt = f'Вопрос от пользователя: "{user_question}"\n\nРелевантные вопросы и ответы из базы знаний:\n'

    # Group questions by their answers
    answer_to_questions = defaultdict(list)
    for pair in qa_pairs:
        answer_to_questions[pair['answer']].append(pair['question'])

    # Create condensed Q&A pairs
    for i, (answer, questions) in enumerate(answer_to_questions.items(), 1):
        if len(questions) > 1:
            formatted_questions = ', '.join(f'"{q}"' for q in questions)
            prompt += f"#{i}. Для вопросов: {formatted_questions}\n   Ответ: {answer}\n\n"
        else:
            prompt += f"#{i}. \"{questions[0]}\"\n   Ответ: {answer}\n\n"

    prompt += '''
Задача: Основываясь на вспомогательных материалах корпоративной базы знаний компании x5 retail group, развёрнуто и чётко ответить на вопрос пользователя. 
Важно, что вспомогательные данные не всегда ранжированы по релевантности. 
Среди примеров может не быть верного ответа! 
Если ты считаешь, вопрос пользователя релевантен вопросу из базы знаний, дай соответствующий ответ. 
Тебе необходимо ответить на вопрос. Объяснять, почему ты выбрал именно это вариант из базы не нужно. 
Если ты считаешь, что в предоставленных данных не содержится ответа на вопрос, то нужно ответить, что тебе дали слишком мало конкретики. Попроси описать проблему подробнее. 
Если в вспомогательных данных есть несколько вопросов, которые релевантны данному, задай уточняющий вопрос, чтобы понять, какой из вопросов больше подходит.
При ответе на вопрос ничего лишнего не пиши. Только сам ответ или уточняющее предложение.
Ответ должен быть полным, как в базе знаний. Из базы знаний нужно выбрать лишь один ответ!
Отвечай только на русском языке.'''

    return prompt


# Пример использования
history = [
    {"role": "user", "content": "Как мне взять отпуск?"},
    {"role": "assistant", "content": "Какой тип отпуска вас интересует?"},
    {"role": "user", "content": "Ежегодный оплачиваемый"},
    {"role": "assistant", "content": "Сколько дней отпуска вы хотите взять?"},
    {"role": "user", "content": "14 дней"}
]

result = process_history(history, ip)
result




def rag_query(ip: str, queries: List[str], n_results: int) -> Dict[str, Any]:
    """
    Perform a RAG query to retrieve relevant information.
    """
    url = f"http://{ip}:8000/api/v1/get_answer/"
    data = {
        "queries": queries,
        "n_results": n_results
    }
    response = requests.post(url, json=data)
    result = response.json()
    # print("RAG Response:", json.dumps(result, indent=2, ensure_ascii=False))
    return result


def llm_query(history: str, model: str = "gemma2:9b") -> Dict[str, Any]:
    """
    Perform an LLM query using the given prompt.
    """
    url = f"http://{ip}:11434/api/chat/"
    payload = {
        "model": model,
        "messages": history,
        "stream": False,
        "options": {
            "temperature": 0
        },
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()


def create_llm_prompt(user_question: str, rag_response: Dict[str, Any]) -> str:
    """
    Create a prompt for the LLM based on the user question and RAG results,
    with question grouping for identical answers.
    """
    prompt = f'Вопрос от пользователя: "{user_question}"\n\nРелевантные вопросы и ответы из базы знаний:\n'


    # Extract results from the RAG response
    rag_results = rag_response['results'][0]['results']

    # Group questions by their answers
    answer_to_questions = defaultdict(list)
    for result in rag_results:
        answer_to_questions[result['answer']].append(result['question'])

    # Create condensed Q&A pairs
    for i, (answer, questions) in enumerate(answer_to_questions.items(), 1):
        if len(questions) > 1:
            formatted_questions = ', '.join(f'"{q}"' for q in questions)
            prompt += f"#{i}. Для вопросов: {formatted_questions}\n   Ответ: {answer}\n\n"
        else:
            prompt += f"#{i}. \"{questions[0]}\"\n   Ответ: {answer}\n\n"

    prompt += '''
Задача: Основываясь на вспомогательных материалах корпоративной базы знаний компании x5 retail group, развёрнуто и чётко ответить на вопрос пользователя. 
Важно, что вспомогательные данные не всегда ранжированы по релевантности. 
Среди примеров может не быть верного ответа! 
Если ты считаешь, вопрос пользователя релевантен вопросу из базы знаний, дай соответствующий ответ. 
Можно перефразировать его немного для разнообразия, но не в ущерб смыслу! 
Тебе необходимо ответить на вопрос. Объяснять, почему ты выбрал именно это вариант из базы не нужно. 
Если ты считаешь, что в предоставленных данных не содержится ответа на вопрос, то нужно ответить, что тебе дали слишком мало конкретики. Попроси описать проблему подробнее. 
Если в вспомогательных данных есть несколько вопросов, которые релевантны данному, задай уточняющий вопрос, чтобы понять, какой из вопросов больше подходит.
При ответе на вопрос ничего лишнего не пиши. Только сам ответ или уточняющее предложение.
Ответ должен быть полным, как в базе знаний. Допускаются лишь незначительные отвклонения. Из базы знаний нужно выбрать лишь один ответ!
Отвечай только на русском языке.'''

    return prompt


def rag_llm_pipeline(ip: str, user_question: str, n_results: int = 5) -> Dict[str, Any]:
    """
    Perform the full RAG-LLM pipeline for a given user question.
    """
    # 1. Perform RAG query
    rag_response = rag_query(ip, [user_question], n_results)

    # 2. Create LLM prompt
    llm_prompt = create_llm_prompt(user_question, rag_response)

    # 3. Perform LLM query
    llm_response = llm_query(llm_prompt)

    return {
        "user_question": user_question,
        "rag_results": rag_response,
        "llm_prompt": llm_prompt,
        "llm_response": llm_response
    }


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
