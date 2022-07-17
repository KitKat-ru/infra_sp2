## YaMDB
### Описание: ###

Проект YaMDb (REST API) собирает отзывы пользователей на различные произведения.  
Реализовано на `Djangorestframework 3.12.4` Аутентификация на основе `JWT`. Читать контент могут все, вносить и изменять только аутентифицированные пользователи.  
Предоставляет ответы от сервера в формате JSON для последующей сериалиализации на стороне фронта.  
Это первый совместный проект, было сложно но интересно. 

## Установка: ##

### Клонируйте репозиторий: ###

    git clone git@github.com:KitKat-ru/infra_sp2.git


### Пример файла `.env`. Должен находится в папке `./infra_sp2/infra/`: ###

    SECRET_KEY=... (ключ к Джанго проекту)
    DB_ENGINE=django.db.backends.postgresql (указываем, что работаем с postgresql)
    DB_NAME=postgres (имя базы данных)
    POSTGRES_USER=... (логин для подключения к базе данных)
    POSTGRES_PASSWORD=... (пароль для подключения к БД (установите свой)
    DB_HOST=db (название сервиса (контейнера)
    DB_PORT=5432 (порт для подключения к БД)

### Перейдите в репозиторий к директории с файлом docker-compose.yaml с помощью командной строки: ###

    cd infra_sp2/infra/
  
### Установите [Docker и Docker-compose](https://docs.docker.com/engine/install/ubuntu/). Запустите сборку образов: ###

    sudo docker-compose up

### или

    sudo docker-compose up -d --build
  
### После развертывания проекта создайте миграции и заполнените базу данных: ###

    sudo docker-compose exec python manage.py makemigrates
    sudo docker-compose exec python manage.py migrate
    sudo docker-compose exec python manage.py createsuperuser
    sudo docker-compose exec python manage.py collectstatic

#### Перейдите в папку с файлом `fixtures.json` и введите команду:

    sudo docker cp fixtures.json <CONTAINER ID - infra_web>:/app
    sudo docker exec -it <CONTAINER ID - infra_web> bash 

#### Перейдите в директорию с файлом `manage.py`и выполните следующий код:

    python3 manage.py shell
    # выполнить в открывшемся терминале:
    >>> from django.contrib.contenttypes.models import ContentType
    >>> ContentType.objects.all().delete()
    >>> quit()
    python manage.py loaddata fixtures.json

## Алгоритм регистрации пользователей ##
  
1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.  
2. YaMDB отправляет письмо с кодом подтверждения `confirmation_code` на адрес `email`. В проекте реализован бэкенд почтового сервиса, папка - `sent_emails`.  

#### - Получаем ключ авторизации для получения токена:

    sudo docker-compose exec web bash
    cd send_emails
    cat "файл с почтой" - копируем confirmation_code

4. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит token (JWT-токен).  
5. При желании пользователь отправляет PATCH-запрос на эндпоинт `/api/v1/users/me/` и заполняет поля в своём профайле.  

### ReDoc:

    http://127.0.0.1:8000/redoc/

### Автор:

- #### [Фабриков Артем](https://github.com/KitKat-ru)

### Лицензия:
- Этот проект лицензируется в соответствии с лицензией MIT ![](https://miro.medium.com/max/156/1*A0rVKDO9tEFamc-Gqt7oEA.png "1")

## Образ выложен на DockerHub, что бы его скачать введите:
    sudo docker pull taeray/infra_web:v.1.2
