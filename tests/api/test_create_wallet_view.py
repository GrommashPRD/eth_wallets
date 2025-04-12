from rest_framework import status
from wallet.models import Wallet

import pytest
import logging

logger = logging.getLogger('tests')

@pytest.mark.django_db
class TestCreateWalletView:
    def test_create_wallet_success(self, client):
        response = client.post("/api/v1/wallets/", data={'currency': 'ETH'}, format='json')

        assert response.status_code == status.HTTP_201_CREATED

        assert 'id' in response.data['wallet']
        assert 'currency' in response.data['wallet']
        assert 'public_key' in response.data['wallet']

        wallet_exists = Wallet.objects.filter(wallet_id=response.data["wallet"].get("id")).exists()
        assert wallet_exists

    def test_create_wallet_invalid_currency_type(self, client):
        response = client.post("/api/v1/wallets/", data={'currency': 'BTC'}, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'message': 'Currency must be ETH.', 'code': 'invalid_currency'}


        wallets = Wallet.objects.all()
        assert wallets.count() == 0

    def test_create_wallet_missing_currency_type(self, client):
        response = client.post("/api/v1/wallets/", data={}, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert response.data == {'message': 'Currency must be ETH.', 'code': 'invalid_currency'}

        wallets = Wallet.objects.all()
        assert wallets.count() == 0