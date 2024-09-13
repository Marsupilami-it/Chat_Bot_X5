import logging
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import json
from collections import defaultdict
import uvicorn
from fastapi import FastAPI

# Настройка базового логирования
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s")

app = FastAPI()
ip = '62.68.146.67'

# Модель для описания структуры данных запроса
class Message(BaseModel):
    role: str
    content: str


class ChatHistory(BaseModel):
    history: List[Message]


def process_history(history: List[Message], ip: str, N: int = 2, M: int = 3) -> List[Dict[str, str]]:
    logging.info("Processing history to retrieve user messages and generate RAG queries.")

    # Получаем последние N сообщений пользователя
    user_messages = [msg.content for msg in history if msg.role == "user"][-N:]

    logging.info(f"User messages extracted: {user_messages}")

    # Получаем конкатенацию последних M сообщений (всех ролей)
    all_messages = " ".join([msg.content for msg in history[-M:]])

    # Формируем список запросов для RAG
    queries = user_messages + [all_messages]
    logging.info(f"Generated queries: {queries}")

    # Выполняем запрос к RAG
    rag_results = rag_query(ip, queries, n_results=5)
    logging.info(f"RAG results received: {rag_results}")

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

    logging.info(f"Processed RAG results: {processed_results}")
    return processed_results


def create_condensed_qa_prompt(user_question: str, qa_pairs: List[Dict[str, str]]) -> str:
    logging.info("Creating condensed QA prompt.")
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
    logging.info("QA prompt created.")
    return prompt


def rag_query(ip: str, queries: List[str], n_results: int) -> Dict[str, Any]:
    """
    Perform a RAG query to retrieve relevant information.
    """
    logging.info(f"Performing RAG query with IP: {ip} and queries: {queries}")
    url = f"http://{ip}:8000/api/v1/get_answer/"
    data = {
        "queries": queries,
        "n_results": n_results
    }
    response = requests.post(url, json=data)
    result = response.json()
    logging.info("RAG query response received.")
    return result


def remove_role_messages(history: List[Message], role="assistant", n=2):
    """
    Удаляет все сообщения указанной роли, кроме последних N.
    
    :param history: список сообщений, содержащих "role" и "content"
    :param role: роль, сообщения которой нужно удалить (например, "assistant")
    :param n: количество последних сообщений этой роли, которые нужно оставить
    :return: список сообщений с удалёнными сообщениями указанной роли
    """
    # Собираем все индексы сообщений указанной роли
    role_indices = [i for i, message in enumerate(history) if message.role == role]

    # Оставляем последние N индексов для сохранения
    indices_to_keep = role_indices[-n:]

    # Формируем новый список, удаляя все сообщения роли, кроме последних N
    new_history = [message for i, message in enumerate(history) if message.role != role or i in indices_to_keep]

    return new_history

def llm_query(msgs: list, model: str = "gemma2:9b") -> Dict[str, Any]:
    """
    Perform an LLM query using the given prompt.
    """
    url = f"http://{ip}:11434/api/chat/"
    
    # Преобразуем сообщения в список словарей перед сериализацией
    payload = {
        "model": model,
        "messages": [msg.dict() if isinstance(msg, Message) else msg for msg in msgs],
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



@app.post("/api/v1/get_answer/")
def query(history: ChatHistory):
    #logging.info(f"Received history for processing: {history}")
    chat_history = history.history

    # Нахождение релевантной информации
    result = process_history(chat_history, ip)

    # Создание сообщения пользователя
    res = create_condensed_qa_prompt(chat_history[-1].content, result)

    # Формирование истории
    result_history = remove_role_messages(chat_history, 'assistant', 2)
    result_history = result_history[:-1]
    result_history.append({'role': 'user', 'content': res})

    logging.info(result_history)
    answer = llm_query(result_history)
    return answer


if __name__ == "__main__":
    logging.info("Starting FastAPI server.")
    uvicorn.run(app, host="0.0.0.0", port=8003)
