установка зависимостей: '''pip install req.txt'''

перед началом работы: python '''manage.py createsuperuser'''

запуск миграций '''python manage.py migrate'''

запуск сервера: '''python manage.py runserver'''

1. POST http://127.0.0.1:8000/api/v1/wallets/ - создать кошелек
2. GET http://127.0.0.1:8000/api/v1/wallets/ - получить список кошельков(только superuser)
3. POST http://127.0.0.1:8000/api/v1/transactions/ - совершить транзакцию между кошельками системы
4. http://127.0.0.1:8000/api/docs/ - документация

