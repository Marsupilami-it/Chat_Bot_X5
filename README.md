# DeltaBot - Чат-бот для технической поддержки X5 Retail Group
Чат-бот для консультаций сотрудников орагнизации X5 Retail Group по интересующим вопросам.

Цель бота - снизить нагрузку на сотрудников 1-й линии технической поддержки (1ЛТП)

## Cодержание
- [Технологии](#технологии)
- [Архитектура сервиса](#архитектура-сервиса)
- [Запуск сервиса](#запуск-сервиса)
- [Сценарии использования](#сценарии-использования)
- [Команда проекта](#команда-проекта)

## Технологии
- Бэкенд

  API - FastApi
  
  Библиотека для работы с БД - SQLAlchemy
  
  Сервис кэширования - Redis
  
  Брокер сообщений - RabbitMQ (в развитие)
  
  Балансировщик - Nginx
  
- Модель
  
  RAG - ruBERTtiny v.2
  
  LLM - Gemma2 9B
  
  Векторная БД - ChromaDB
  
- Интерфейс
  
  UI - Streamlit

## Архитектура сервиса

![](project_docs/ComponentDiagram.png)

## Запуск сервиса

   ```
   docker compose up -d --build
   ```

## Cценарии использования

Описание сценариев использования чат-бота со стороны пользователя

#### Первый сценарий - бот корректно ответил на вопрос пользователя:
   1. Пользователь начинает общение с ботом, пишет "Привет"
   2. Бот отвечает, задавая вопрос "Чем я могу помочь?"
   3. Пользователь отправляет вопрос пользователю
   4. Бот предоставляет ответ
   5. Ответ удовлетворяет пользователя, пользователь нажимает кнопку "Ответ удовлетворительный"
   6. Бот отвечает "Рад помочь"

#### Второй сценарий - бот с 1 раза не смог корректно ответить на вопрос пользователя:
   1. Пользователь начинает общение с ботом, пишет "Привет"
   2. Бот отвечает, задавая вопрос "Чем я могу помочь?"
   3. Пользователь отправляет вопрос пользователю
   4. Бот предоставляет ответ
   5. Ответ является некорректным, пользователь нажимает кнопку
   6. Бот приносит извинения за некорретный ответ и просит задать вопрос иначе
   7. Повторяется процесс по пунктам 4-6 не более 2 раз до момента получения пользователем корректного ответа
   8. Ответ удовлетворяет пользователя, пользователь нажимает кнопку "Ответ удовлетворительный"
   9. Бот отвечает "Рад помочь"

#### Третий сценарий - бот не смог дать ответ и передал вопрос специалисту:
   1. Пользователь начинает общение с ботом, пишет "Привет"
   2. Бот отвечает, задавая вопрос "Чем я могу помочь?"
   3. Пользователь отправляет вопрос пользователю
   4. Бот предоставляет ответ
   5. Ответ является некорректным, пользователь нажимает кнопку
   6. Бот приносит извинения за некорретный ответ и просит задать вопрос иначе
   7. Повторяется процесс по пунктам 4-6, при предоставлении 3-х ответов, не удовлетворяющих пользователя, бот приносит извинения "Приношу извинения, что не смог помочь, передаю ваш вопрос специалисту"
   8. Дальнейшую работу по обращению ведет специалист

## Команда проекта
- Жиров Андрей - Product Manager
- Ларина Нина - System Architect
- Устинов Андрей - Data Science
- Бокарев Степан - Backend Developer
- Григорьев Игорь - Backend Developer
