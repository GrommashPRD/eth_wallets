import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from wallet.models import Wallet

@pytest.mark.django_db
def test_get_wallets_success(client):
    # Создаем суперпользователя для выполнения теста
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    # Создаем тестовый кошелек
    wallet = Wallet.objects.create(
        wallet_id=1,
        currency='ETH',
        public_key='0xabc123...'
    )

    # Мокируем функцию получения баланса
    with patch('wallet.views.w3.eth.get_balance') as mock_get_balance:
        mock_get_balance.return_value = 1000000000000000000  # 1 ETH в Wei
        with patch('wallet.views.w3.from_wei') as mock_from_wei:
            mock_from_wei.return_value = 1  # Возвращаем 1 Ether

            # Делаем GET запрос
            response = client.get("/api/v1/wallets/")

            # Проверяем, что ответ успешный
            assert response.status_code == 200
            assert response.json() == {
                'success': True,
                'wallets': [{
                    'id': 1,
                    'currency': 'ETH',
                    'public_key': '0xabc123...',
                    'balance': '1',
                }]
            }


@pytest.mark.django_db
def test_get_wallets_no_wallets(client):
    # Создаем суперпользователя для выполнения теста
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    # Делаем GET запрос, когда нет кошельков
    response = client.get("/api/v1/wallets/")

    # Проверяем, что ответ с ошибкой 404
    assert response.status_code == 404
    assert response.json() == {
        'success': False,
        'error': 'No wallets found',
    }


@pytest.mark.django_db
def test_get_wallets_balance_error(client):
    # Создаем суперпользователя для выполнения теста
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    # Создаем тестовый кошелек
    wallet = Wallet.objects.create(
        wallet_id='1',
        currency='ETH',
        public_key='0xabc123...'
    )

    # Мокируем функцию получения баланса, чтобы вызвать ошибку
    with patch('wallet.views.w3.eth.get_balance') as mock_get_balance:
        mock_get_balance.side_effect = Exception("Balance retrieval error")

        # Делаем GET запрос
        response = client.get("/api/v1/wallets/")

        # Проверяем, что ответ успешный и содержит сообщение об ошибке
        assert response.status_code == 200
        assert response.json() == {
            'success': True,
            'wallets': []
        }

        # Здесь можно также проверить, что в логах содержится нужное сообщение об ошибке


@pytest.mark.django_db
def test_get_wallets_unexpected_error(client):
    # Создаем суперпользователя для выполнения теста
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    # Искусственно вызываем ошибку в методе
    with patch('wallet.views.Wallet.objects.all') as mock_all:
        mock_all.side_effect = Exception("Unexpected error")

        # Делаем GET запрос
        response = client.get("/api/v1/wallets/")

        # Проверяем, что ответ 500 с информацией об ошибке
        assert response.status_code == 500
        assert response.json() == {
            'success': False,
            'error': "Unexpected error"
        }