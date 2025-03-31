from rest_framework import status
from wallet.models import Wallet

import pytest
import logging

logger = logging.getLogger('tests')

@pytest.mark.django_db
class TestCreateWalletView:
    def test_create_wallet_success(self, client):
        response = client.post("/api/v1/wallets/", data={'currency': 'ETH'}, content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        assert 'id' in response_data['wallet']
        assert 'currency' in response_data['wallet']
        assert 'public_key' in response_data['wallet']

        wallet_exists = Wallet.objects.filter(wallet_id=response_data["wallet"].get("id")).exists()
        assert wallet_exists

    def test_create_wallet_invalid_currency_type(self, client):
        response = client.post("/api/v1/wallets/", data={'currency': 'BTC'}, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert 'error' in response_data
        assert response_data['error'] == 'Только ETH разрешен для создания кошелька'

        wallets = Wallet.objects.all()
        assert wallets.count() == 0

    def test_create_wallet_missing_currency_type(self, client):
        response = client.post("/api/v1/wallets/", data={}, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_data = response.json()
        assert 'error' in response_data
        assert response_data['error'] == 'Только ETH разрешен для создания кошелька'

        wallets = Wallet.objects.all()
        assert wallets.count() == 0