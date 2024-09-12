from collections import defaultdict
from typing import List, Dict, Any
import streamlit as st
import json
import requests

# Глобальная переменная для хранения истории диалога
BASE_URL = "http://localhost:8888/"
#api-service

ip = '62.68.146.67'


def write_message(role, content, save=True):
    """
    Function to write messages to the session state and display them.
    """
    # Parse the JSON content if it is a string
    if isinstance(content, str) and content.startswith('{'):
        try:
            content_dict = json.loads(content)
            if 'answer' in content_dict and 'documents' in content_dict['answer']:
                documents = content_dict['answer']['documents']
                if documents and len(documents) > 0:
                    content = documents[0][0]  # Take the first document
        except json.JSONDecodeError:
            st.error("Failed to decode JSON content")

    if save:
        st.session_state.messages.append({"role": role, "content": content})

    if role == 'user':
        st.markdown(f"**Вы:** {content}")
    else:
        st.markdown(f"**Чат-бот:** {content}")


# Page Config
st.set_page_config("X5 Group", page_icon=":ai:")

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
            "content": "Привет! Чат-бот компании Х5. Чем я могу помочь?"}
    ]

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)


def call_api(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    response = None
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


def handle_submit(message):
    """
    Submit handler to generate a response from the bot.
    """
    with st.spinner('Thinking...'):
        result = submit_dialogue()
        #
        print(result)
        write_message('assistant', result['message']['content'])

        print(len(st.session_state.messages))
        print(st.session_state.messages)

# Пример структуры данных


def submit_dialogue():
    # Подготовка данных для отправки
    dialogue_history = st.session_state.messages

    # Упаковка данных в JSON-формат
    data = {
        "history": dialogue_history
    }

    # Вызов API
    api_response = call_api("/api/v1/get_answer/", data)

    # Обработка ответа API
    if api_response:
        return api_response

# Handle any user input
if question := st.chat_input("Введите ваш вопрос..."):
    # Display user message in chat message container
    write_message('user', question)

    # Generate a response
    handle_submit(question)
