# Запуск

1) Клонируйте репозиторий проекта:

``` bash
git clone -b api https://github.com/Marsupilami-it/Chat_Bot_X5.git
```

2. Перейдите в директорию проекта:

``` bash
cd Chat_Bot_X5
```

3. Выполните команду ls и убедитесь, что вывод соответствует:
```
Dockerfile.api          docker-compose.yml      requirements.txt
Dockerfile.ui           outter_api.py           ui.py
```

4. Постройте и запустите контейнеры с помощью Docker Compose:
``` bash
docker-compose up --build -d
```
5. Проверьте статус запущенных контейнеров:

``` bash
docker-compose ps
```

6. Откройте браузер и перейдите по адресу:
```
http://localhost:8501
```

Если вы запускаете приложение на удаленном сервере, замените localhost на IP-адрес вашего сервера.



Контакты:

Авторы команда DeltaX