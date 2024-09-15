import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import requests

# Настройка страницы
st.set_page_config(page_title="X5 Group Chatbot", page_icon="🤖", layout="wide")

# Применение пользовательских стилей CSS
st.markdown("""
<style>
    .stChat message {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChat .user-message {
        background-color: #e6f3ff;
        text-align: right;
    }
    .stChat .bot-message {
        background-color: #f0f0f0;
    }
    .stChat .message-content {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Конфигурация API
API_URL = "http://localhost:9003/api/v1/get_answer/"

# Боковая панель
with st.sidebar:
    st.title('🤖 X5 Group Chatbot')
    st.markdown('''
    ## About
    Этот чат-бот создан для помощи сотрудникам X5 Group.
    Он может ответить на вопросы о:
    - Корпоративных политиках
    - Процедурах HR
    - Общей информации о компании
    
    Разработано с использованием:
    - [Streamlit](https://streamlit.io/)
    - [LangChain](https://www.langchain.com/)
    ''')
    add_vertical_space(5)
    st.write('Made with ❤️ by X5 Tech Team')

# Основная область чата
st.title("💬 X5 Group Assistant")
colored_header(label='Чат с AI помощником', description='Задайте вопрос, и я постараюсь помочь', color_name='blue-70')

# Инициализация истории чата
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Я AI-ассистент X5 Group. Чем я могу вам помочь сегодня?"}
    ]

# Отображение истории чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Функция для отправки запроса к API
def query_api(messages):
    try:
        response = requests.post(API_URL, json={"history": messages})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при обращении к API: {str(e)}")
        return None

# Функция для обработки ввода пользователя
def handle_user_input(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner('AI думает...'):
        api_response = query_api(st.session_state.messages)

    if api_response and 'message' in api_response and 'content' in api_response['message']:
        bot_response = api_response['message']['content']
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
    else:
        st.error("Не удалось получить корректный ответ от API.")

# Ввод пользователя
user_input = st.chat_input("Введите ваш вопрос здесь...")
if user_input:
    handle_user_input(user_input)

# Кнопка для очистки истории чата
if st.button('Очистить историю чата'):
    st.session_state.messages = [
        {"role": "assistant", "content": "История чата очищена. Чем я могу вам помочь?"}
    ]
    st.rerun()  # Заменено st.experimental_rerun() на st.rerun()

# Отображение статуса подключения к API
st.sidebar.markdown("---")
if st.sidebar.button("Проверить подключение к API"):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            st.sidebar.success("✅ API подключено и работает")
        else:
            st.sidebar.error(f"❌ API вернуло код состояния: {response.status_code}")
    except requests.exceptions.RequestException:
        st.sidebar.error("❌ Не удалось подключиться к API")