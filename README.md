# Yatube

Проект Yatube - блог платформа

Благодаря этому проекту можно:

  - создавать свои группы-сообщества
  - писать посты по теме сообщества
  - комментировать посты других пользователей
  - подписываться на интересных авторов
***


### Технологии
Yatube open-source технологии:

Python 3.7
Django 3.2
***

### Установка
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/NikAfraim/yatube.git
```
```
cd yatube
```
---
Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
```
python3 -m pip install --upgrade pip
```
---
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
---
Автор проекта: [NikAfraim](https://github.com/NikAfraim)
