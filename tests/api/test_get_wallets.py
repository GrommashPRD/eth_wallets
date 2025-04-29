from django.contrib.auth.models import User
from unittest.mock import patch
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import pytest
import logging

from wallet.models import Wallet
from wallet.repository.walletsRepository import ActionsWithWallets

logger = logging.getLogger('tests')

@pytest.mark.django_db
def test_get_wallets_success(client):
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    wallet = Wallet.objects.create(
        public_key='0xabc123...'
    )

    with patch('wallet.views.w3.eth.get_balance') as mock_get_balance:
        mock_get_balance.return_value = 1000000000000000000  # 1 ETH в Wei
        with patch('wallet.views.w3.from_wei') as mock_from_wei:
            mock_from_wei.return_value = 1  # Возвращаем 1 Ether

            response = client.get("/api/v1/wallets/", format='json')

            assert response.status_code == 200


@pytest.mark.django_db
def test_get_wallets_no_wallets(client):
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    response = client.get("/api/v1/wallets/", format='json')

    assert response.status_code == 400
    assert response.data == {"message": "No wallets found", "code": "no_wallets_found"}


@pytest.mark.django_db
def test_create_wallet_with_invalid_balance(client):
    superuser = User.objects.create_superuser(
        username='superuser',
        password='password'
    )
    client.login(username='superuser', password='password')

    with pytest.raises(ValidationError):
        wallet = Wallet(
            wallet_id=1,
            currency='ETH',
            public_key='0xabc123...',
            balance='balance'
        )
        wallet.full_clean()  # Проверяем валидатор модели перед сохранением

    assert Wallet.objects.count() == 0  # Объект не должен быть создан

