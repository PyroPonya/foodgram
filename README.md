# Foodgram

![Foodgram Workflow](https://github.com/PyroPonya/foodgram/actions/workflows/main.yml/badge.svg)
<br>
[Foodgram Web App](https://project-letsie.bounceme.net)

## Описание

«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек Технологий

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
<br>

- **Python**
- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **Gunicorn**
- **Docker**
- **Nginx**

## Как развернеть контейнеры в Docker:

1. Клонируйте репозиторий на свой компьютер:
   ```bash
   git clone https://github.com/PyroPonya/foodgram.git
   ```
2. Перейдите в дирректорию foodgram проекта.
   ```bash
   cd foodgram
   ```
3. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```
4. Создайте файл .env и заполните его по шаблону .env.example.
5. Запустите аркестрацию Docker контейнеров, соберите статику и выполните миграции.
   ```bash
   sudo docker compose -f docker-compose.yml up -d
   sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
   sudo docker compose -f docker-compose.yml exec backend python manage.py import_ingredients
   sudo docker compose -f docker-compose.yml exec backend python manage.py import_tags
   sudo docker compose -f docker-compose.yml exec backend python manage.py init_admin
   sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic --no-input
   ```

## Развертывание локального проекта без использования Docker:

1. Клонируйте репозиторий на свой компьютер:
2. Создайте файл .env и заполните его по шаблону .env.example.
3. Установите Python на вашу ОС.
4. Установите зависимости, описанные в requirements.txt:
5. Перейдите в корневую дирректорию проекта, создайте и активируйте виртуальное окружение.
6. Выполните миграции, импортируйте данные и запустите проект:
   ```bash
   python manage.py migrate
   python manage.py import_ingredients
   python manage.py import_tags
   python manage.py init_admin
   python manage.py runserver
   ```

## Спецификация API

После локального запуска проекта спецификация API доступна по адресу:
[http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

## Эндпоинты API

- Получение токена: `/api/auth/token/login/`
- Удаление токена: `/api/auth/token/logout/`

- Регистрация: `/api/users/`
- Список пользователей: `/api/users/`
- Информация о текущем пользователе: `/api/users/me/`
- Подписка на пользователя: `/api/users/{id}/subscribe/`
- Отписка от пользователя: `/api/users/{id}/subscribe/`

- Список и создание рецептов: `/api/recipes/`
- Детали рецепта: `/api/recipes/{recipe_id}/`
- Добавление рецепта в избранное: `/api/recipes/{recipe_id}/favorite/`
- Удаление рецепта из избранного: `/api/recipes/{recipe_id}/favorite/`
- Добавление рецепта в корзину покупок: `/api/recipes/{recipe_id}/shopping_cart/`
- Удаление рецепта из корзины покупок: `/api/recipes/{recipe_id}/shopping_cart/`
- Скачивание списка покупок: `/api/recipes/download_shopping_cart/`

## Автор

Летсие Алексис [https://github.com/PyroPonya](https://github.com/PyroPonya)
