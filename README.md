# Yatube
##### _Made by the one and only [Sasha Smirnov][github_link]_
# 

## Что такое Yatube

### Yatube - это блог, реализованный на Django

API Yatube позволяет Вам:

- Ведение текстовых блогов в разрезе групп, с поддержкой изображений и комментариев к постам
- Регистрация пользователей
- Подписки

## Stack

- [Python3.7]
- [Django 2.2.16]
- [Django REST framework][drf]

## Запуск проекта
- Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone https://github.com/crush-on-anechka/hw05_final
cd hw05_final
``` 
- Установите и запустите виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
``` 
- Установите зависимости:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
``` 
- Выполните миграции и запустите проект:
```
python3 manage.py migrate
python3 manage.py runserver
```

Замечания и пожелания направляйте напрямую [Владимиру Путину][vp]

[github_link]: <http://github.com/crush-on-anechka>
[python3.7]: <https://docs.python.org/3.7/whatsnew/3.7.html>
[Django 2.2.16]: <https://docs.djangoproject.com/en/4.0/releases/2.2.16/>
[drf]: <https://www.django-rest-framework.org>
[vp]: <http://www.kremlin.ru>
