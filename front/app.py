import streamlit as st
from neo4j import GraphDatabase
import json
import requests

# Initialize Neo4j driver
#uri = "bolt://localhost:7687"  # URL вашего Neo4j сервера
#driver = GraphDatabase.driver(uri, auth=("username", "password"))


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


def extract_documents(json_response):
    """
    Извлекает массив документов из JSON-ответа.

    :param json_response: JSON-ответ в виде строки
    :return: Список документов
    """
    # Проверяем, является ли json_response словарем
    if isinstance(json_response, dict):
        response_dict = json_response
    else:
        # Если это строка JSON, преобразуем её в словарь
        response_dict = json.loads(json_response)

    # Извлекаем массив документов
    documents = response_dict['answer']['documents'][0][0]

    return documents

# Page Config
st.set_page_config("Ebert", page_icon=":movie_camera:")

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
            "content": "Привет! Чат-бот компании Х5. Чем я могу помочь?"}
    ]

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Submit handler


def handle_submit(message):
    """
    Submit handler to generate a response from the bot.
    """
    with st.spinner('Thinking...'):
        # Simulate processing time
        query_data = {
            "queries": [message],
            "n_results": 3
        }
        result = call_api("/api/v1/get_answer/", query_data)

        documents = extract_documents(result)
        write_message('assistant', documents)


# Handle any user input
if question := st.chat_input("Введите ваш вопрос..."):
    # Display user message in chat message container
    write_message('user', question)

    # Generate a response
    handle_submit(question)
