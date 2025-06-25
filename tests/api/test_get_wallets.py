from django.contrib.auth.models import User
from unittest.mock import patch
from django.core.exceptions import ValidationError
import pytest
import logging

from wallet.models import Wallet

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

    assert response.status_code == 404
    assert response.data == {"message": "Wallets doesn't exist"}


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
        wallet.full_clean()

    assert Wallet.objects.count() == 0

