


[![api_yamdb workflow](https://github.com/Invictus-7/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/Invictus-7/yamdb_final/actions/workflows/yamdb_workflow.yml)

### Описание проекта  

API для проекта Yamdb на Django Rest Framework, документация Redoc, JWT-токены.
Доступ к работе с категориями, жанрами, произведениями, отзывами и комментариями.  

### Создатели

[Диана Корсак](https://github.com/onemi) <br>
[Артем Ултанов](https://github.com/WayBro-54) <br>
[Кирилл Резник](https://github.com/Invictus-7) <br>

### Список технологий
- Python
- Django
- Django Rest Framework
- JWT


### Документация проекта

Документация проекта доступна [вот здесь.](http://127.0.0.1:8000/redoc/) <br>
(для получения доступа к ней запустите<br>
отладочный сервер с адресом 127.0.0.1:8000)


### Как запустить проект  

Для запуска проект необходимо:<br>
- определиться, в какой директории на компьютере будет храниться проект<br>
- открыть командную строку и перейти в данную директорию<br>
- клонировать репозиторий командной git clone 'адрес репозитория на GitHub'<br>
- перейти в рабочую директорию или открыть проект в IDLE<br>

Создать и активировать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate (для IDLE - venv/Scripts/activate)
```
  
Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
  
Выполнить миграции:

```bash
python3 manage.py migrate
```
  
Запустить сервер:

```bash
python3 manage.py runserver
```

## Запуск проекта в Docker
Для запуска приложения в контейнерах установите Docker на ваш компьютер (сервер). 

### Наполнение .env
Файл `.env` должен находится в директории в директории infra.<br>
Пример наполнения данного файла:<br>

```bash
DB_ENGINE=django.db.backends.postgresql - # указываем, что работаем с postgresql
DB_NAME=postgres # указываем имя базы данных
POSTGRES_USER=postgres # задаем логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # устанавливаем пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
После наполнения файла `.env` необходило изменить константу DATABASE файла settings.py<br>
следующим образом:
```bash
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}
```

### Последовательность запуска приложения
1. *Сборка контейнера*.
Перейдите в папку `infra` и выполните команду docker-compose для сборки и запуска контейнера:
```bash
docker-compose up -d --build
```
2. *Запуск приложения api_yamdb*.
После сборки контейнеров необходимо выполнить следующие команды в терминале:
```bash
# Миграции
docker-compose exec web python manage.py migrate
# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
# Сбор статики
docker-compose exec web python manage.py collectstatic --no-input
# Резервное копирование данных из БД
docker-compose exec web python manage.py dumpdata > dump.json
# Наполнение БД демонстрационными данными (из таблиц .csv)
docker-compose exec web python manage.py data_transfer
```
### Наполнение базы данных из фикстур
```bash
docker-compose exec web bash
python3 manage.py shell

from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
quit()

python manage.py loaddata fixtures.json
```

### Информация о том, как посмотреть развернутый проект
В связи с тем, что проект основан исключительно на API<br>
и не имеет html-страниц, его невозможно увидеть в браузере<br>
в "красивом виде". Вместо этого, для взаимодействия с сервисом<br>
необходимо пользоваться запросами к API. Формат запрос должен <br>
быть следующий: http://<IP-адрес сервера>/api/v1/<название ресурса> <br>
(примеры ресурсов и запросы к ним приведены ниже)

### Пример запросов к API
- Получение списка всех категорий

```python
/api/v1/categories/
```

```json
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "name": "string",
        "slug": "string"
      }
    ]
  }
]
```

- Добавление комментария к отзыву 

```python
api/v1/titles/{title_id}/reviews/{review_id}/comments/
```

```json
{
  "text": "string"
}
```

- Регистрация нового пользователя

```python
api/v1/auth/signup/
```

```json
{
  "email": "string",
  "username": "string"
}
```