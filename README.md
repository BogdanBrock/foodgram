## 💻 Технологии:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)

## Описание проекта Foodgram
"Foodgram" - это сайт, где каждый пользователь может выкладывать свой рецепт, 
а так же все пользователи могут смотреть этот рецепт. Так же пользователи 
могут фильтровать записи по тегам. Помимо этого любой польльзователь 
может подписаться на другого пользователя и просматривать только его рецепты.

## Ссылка по которой доступен сам сайт

https://foodgram.viewdns.net/

## Инструкция как развернуть проект в докере

- Нужно склонировать проект из репозитория командой:
```bash
git clone git@github.com:BogdanBrock/foodgram.git
```
- Чтобы сайт заработал в дальнейшем, нужно создать файл ".env" пример 
для его создания лежит в корне под названием ".env.example"

- Находясь в проекте, перейти в папку под названием infra:
```bash
cd infra
```

- Выполнить команду с включенным докером:
```bash
docker compose up
```

- После того как докер запустился, то нужно 
создать базу данных в контейнере командой:
```bash
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

- Так же по желанию можно создать суперпользователя:
```bash
docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```

- Так же можно наполнить базу данных командой:
```bash
docker compose -f docker-compose.yml exec backend python manage.py load_data ingredients.json
```

- Собрать статику бэкенда:
```bash
docker compose -f docker-compose.yml exec backend python manage.py collectstatic --no-input
```

- Необходимо скопировать всю статику бэкенда для nginx, чтобы отображалась статика на сайте:
```bash
docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
## Список адресов доступных после создания контейнеров

| Адрес                 | Описание |
|:----------------------|:---------|
| localhost:8000/       | Главная страница |
| 127.0.0.1/admin/      | Для входа в админ-зону |
| 127.0.0.1/api/docs/   | Спецификация API |

## Примеры запросов 

- Можно сделать запрос по адресу "localhost:8000/",
по этой ссылке мы получим главную страницу, она доступна для всех пользователей

- Так же по этому запросу можно пройти авторизацию пользователя
"localhost:8000/signin/", при условии,
что этот пользователь зарегистрирован

### Автор:
_Богдан Брок_<br>