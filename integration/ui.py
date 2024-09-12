import streamlit as st
import requests


BASE_URL = "http://localhost:8003/"
# api-service

def write_message(role, content, save=True):
    """
    Function to write messages to the session state and display them.
    """
    if save:
        st.session_state.messages.append({"role": role, "content": content})
    if role == 'user':
        st.markdown(f"**Вы:** {content}")
    else:
        st.markdown(f"**Чат-бот:** {content}")


st.set_page_config("X5 Group", page_icon=":ai:")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
            "content": "Привет! Чат-бот компании Х5. Чем я могу помочь?"}
    ]

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
    with st.spinner('Обрабатываю...'):
        result = submit_dialogue()
        #
        print(result)
        write_message('assistant', result['message']['content'])

        print(len(st.session_state.messages))
        print(st.session_state.messages)


def submit_dialogue():
    dialogue_history = st.session_state.messages

    data = {
        "history": dialogue_history
    }

    api_response = call_api("/api/v1/get_answer/", data)

    if api_response:
        return api_response


if question := st.chat_input("Введите ваш вопрос..."):
    write_message('user', question)

    handle_submit(question)
