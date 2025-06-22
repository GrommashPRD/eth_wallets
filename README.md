**_Приложения для создания кошельков валюты ETH, и выполнения транзакций._**

**_Все пункты КЛИКАБЕЛЬНЫЕ._**

# Начало работы:
Прежде чем запускать `make test`, выполните команды `make venv`, активируйте venv `source venv/bin/activate`, `make install`.
1. `make start`
2. `make stop`
3. `make test`
4. `make migrate`

[**Metrics**](http://127.0.0.1:8000/prometheus/metrics)

[**_DOCS_**](http://127.0.0.1:8000/api/docs/)

# 1. Создание кошелька:

http://127.0.0.1:8000/api/v1/wallets/

```
curl --location --request POST 'http://127.0.0.1:8000/api/v1/wallets/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=cguiLxO9Tw1YJ1tBlIUy8sV7UdG7hTkc' \
--data '{
    "currency": "ETH"
}'
```

# 2. Получить список кошельков созданных в системе 

http://127.0.0.1:8000/api/v1/wallets/

_**Только superuser (root, root) может просматривать списки кошельков.**_

**_При запуске контейнера автоматически создается superuser(root, root)._**

Войти в систему - http://127.0.0.1:8000/api/v1/drf-auth/login


# 3. Cовершить транзакцию между кошельками системы 

http://127.0.0.1:8000/api/v1/transactions/

```
curl --location --request POST 'http://127.0.0.1:8000/api/v1/transactions/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=cguiLxO9Tw1YJ1tBlIUy8sV7UdG7hTkc' \
--data '{
    "from_wallet": "<ИЗ ПУНКТА 2 БЕРЕТЕ АДРЕС КОШЕЛЬКА>",
    "to_wallet": "<ИЗ ПУНКТА 2 БЕРЕТЕ АДРЕС КОШЕЛЬКА>",
    "amount": 0.24
}'
```

