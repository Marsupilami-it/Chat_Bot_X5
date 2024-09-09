import streamlit as st



# Функция для генерации ответа
def chatbot_response(user_input):
    if "привет" in user_input.lower():
        return "Привет! Чем могу помочь?"
    elif "как дела" in user_input.lower():
        return "У меня все отлично! А у вас?"
    elif "пока" in user_input.lower():
        return "До свидания! Хорошего дня!"
    else:
        return "Извините, я пока не понимаю этот запрос."

# Настройка страницы
st.title("Чат-бот на Streamlit")

# Добавление блока FAQ
with st.expander("Часто задаваемые вопросы (FAQ)"):
    st.write("1. **Как начать разговор?**")
    st.write("Напишите 'Привет', чтобы начать разговор.")
    st.write("2. **Как узнать, как дела у бота?**")
    st.write("Вы можете спросить: 'Как дела?'.")
    st.write("3. **Как закончить диалог?**")
    st.write("Напишите 'Пока', чтобы завершить разговор.")

# Инициализация истории чата
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Поле ввода пользователя
user_input = st.text_input("Введите ваше сообщение:", "")

# Если сообщение не пустое, добавляем его в историю
if user_input:
    # Добавляем в историю сообщение пользователя и ответ бота
    response = chatbot_response(user_input)
    st.session_state['history'].append({"role": "user", "message": user_input})
    st.session_state['history'].append({"role": "bot", "message": response})

# Отображение истории диалога
for chat in st.session_state['history']:
    if chat["role"] == "user":
        st.text(f"Вы: {chat['message']}")
    else:
        st.text(f"Бот: {chat['message']}")
