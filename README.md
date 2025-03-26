**_Приложения для создания кошельков валюты ETH, и выполнения транзакций._**

**_Все пункты КЛИКАБЕЛЬНЫЕ._**

Начало работы:
1. make start
2. make stop
3. make test
4. make migrate

[**_Metrics (**клик**)_**](http://127.0.0.1:8000/metrics)

[**_DOCS_**](http://127.0.0.1:8000/api/docs/)

1. [Создание кошелька по POST запросу](http://127.0.0.1:8000/api/v1/wallets/)

```
curl --location 'http://127.0.0.1:8000/api/v1/wallets/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=cguiLxO9Tw1YJ1tBlIUy8sV7UdG7hTkc' \
--data '{
    "currency": "ETH"
}'
```
2. [Получить список кошельков созданных в системе](http://127.0.0.1:8000/api/v1/wallets/)

_**Только superuser (root, root) может просматривать списки кошельков.**_

**_При запуске контейнера автоматически создается superuser._**

3. [Cовершить транзакцию между кошельками системы](http://127.0.0.1:8000/api/v1/transactions/)

```
curl --location 'http://127.0.0.1:8000/api/v1/transactions/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=cguiLxO9Tw1YJ1tBlIUy8sV7UdG7hTkc' \
--data '{
    "from_wallet": "<Адрес кошелька с которого исходит платёж>",
    "to_wallet": "<Адрес кошелька на который придёт платёж>",
    "amount": 1.0(float)
}'
```

