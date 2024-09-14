import logging
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import json
from collections import defaultdict
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI()
ip = '62.68.146.67'  # IP адрес для LLM и RAG сервисов

class Message(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    history: List[Message]

def rag_query(ip: str, queries: List[str], n_results: int) -> Dict[str, Any]:
    url = f"http://{ip}:8000/api/v1/get_answer/"
    data = {
        "queries": queries,
        "n_results": n_results
    }
    response = requests.post(url, json=data)
    return response.json()

def llm_query(msgs: List[Dict[str, str]], model: str = "gemma2:9b") -> Dict[str, Any]:
    url = f"http://{ip}:11434/api/chat/"
    payload = {
        "model": model,
        "messages": msgs,
        "stream": False,
        "options": {"temperature": 0.0},
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def process_history(history: List[Message], ip: str, N: int = 2, M: int = 3) -> List[Dict[str, Any]]:
    user_messages = [msg.content for msg in history if msg.role == "user"][-N:]
    all_messages = " ".join([msg.content for msg in history[-M:]])
    queries = user_messages + [all_messages]
    
    rag_results = rag_query(ip, queries, n_results=5)
    
    answer_to_questions = defaultdict(list)
    for query_result in rag_results['results']:
        for result in query_result['results']:
            answer_to_questions[result['answer']].append(result['question'])
    
    processed_results = [
        {
            "questions": questions,
            "answer": answer
        }
        for answer, questions in answer_to_questions.items()
    ]
    
    return processed_results

def create_condensed_qa_prompt(user_question: str, qa_pairs: List[Dict[str, Any]]) -> str:
    prompt = f'Вопрос от пользователя: "{user_question}"\n\nРелевантные вопросы и ответы из базы знаний:\n'

    for i, pair in enumerate(qa_pairs, 1):
        questions = ', '.join(f'"{q}"' for q in pair['questions'])
        prompt += f"#{i}. Вопросы: {questions}\n   Ответ: {pair['answer']}\n\n"
    
    prompt += '''
Задача: Основываясь на вспомогательных материалах корпоративной базы знаний компании x5 retail group, развёрнуто и чётко ответить на вопрос пользователя. 
Важно, что вспомогательные данные не всегда ранжированы по релевантности. 
Если ты считаешь, вопрос пользователя релевантен вопросам из базы знаний, дай соответствующий ответ. 
Общайся с пользователем непринужденно, как с другом, но оставайся профессиональным.
Если ты считаешь, что в предоставленных данных не содержится ответа на вопрос, то нужно ответить, что тебе дали слишком мало конкретики. Попроси описать проблему подробнее. 
Если в вспомогательных данных есть несколько вопросов, которые релевантны данному, задай уточняющий вопрос, чтобы понять, какой из вопросов больше подходит.
Ответ должен быть полным, как в базе знаний. Из базы знаний нужно выбрать лишь один ответ!
Отвечай только на русском языке.'''
    
    return prompt

@app.post("/api/v1/get_answer/")
async def get_answer(history: ChatHistory):
    logging.info(f"Received chat history: {history}")

    qa_pairs = process_history(history.history, ip)
    logging.info(f"Processed QA pairs: {qa_pairs}")

    user_question = history.history[-1].content
    prompt = create_condensed_qa_prompt(user_question, qa_pairs)
    
    llm_history = [{"role": "system", "content": prompt}]
    for msg in history.history:
        llm_history.append({"role": msg.role, "content": msg.content})

    llm_response = llm_query(llm_history)
    logging.info(f"LLM response: {llm_response}")

    if 'message' in llm_response and 'content' in llm_response['message']:
        response_content = llm_response['message']['content']
    else:
        response_content = "Извините, произошла ошибка при обработке вашего запроса."

    response = {
        "model": "gemma2:9b",
        "message": {
            "role": "assistant",
            "content": response_content
        }
    }

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9003)