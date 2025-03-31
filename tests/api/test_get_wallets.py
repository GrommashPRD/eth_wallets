from django.contrib.auth.models import User
from unittest.mock import patch
from wallet.models import Wallet
from django.db import IntegrityError
import pytest
import logging


logger = logging.getLogger('tests')

@pytest.mark.django_db
def test_get_wallets_success(client):
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    wallet = Wallet.objects.create(
        wallet_id=1,
        currency='ETH',
        public_key='0xabc123...'
    )

    with patch('wallet.views.w3.eth.get_balance') as mock_get_balance:
        mock_get_balance.return_value = 1000000000000000000  # 1 ETH в Wei
        with patch('wallet.views.w3.from_wei') as mock_from_wei:
            mock_from_wei.return_value = 1  # Возвращаем 1 Ether

            response = client.get("/api/v1/wallets/")

            assert response.status_code == 200
            assert response.json() == {
                'success': True,
                'wallets': [{
                    'id': 1,
                    'currency': 'ETH',
                    'public_key': '0xabc123...',
                    'balance': 1,
                }]
            }


@pytest.mark.django_db
def test_get_wallets_no_wallets(client):
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    response = client.get("/api/v1/wallets/")

    assert response.status_code == 404
    assert response.json() == {
        'success': False,
        'error': 'No wallets found',
    }


@pytest.mark.django_db
def test_create_wallet_with_invalid_balance(client):
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    with pytest.raises(IntegrityError):
        Wallet.objects.create(wallet_id=1, currency='ETH', public_key='0xabc123...', balance='invalid balance')

    assert Wallet.objects.count() == 0  # Проверяем, что в базе данных нет ни одного кошелька

