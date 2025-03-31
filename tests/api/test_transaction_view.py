import pytest
from django.urls import reverse
from rest_framework import status
from wallet.models import Wallet, Transaction
import uuid
import logging

logger = logging.getLogger('tests')


@pytest.mark.django_db
def test_successful_transaction(client):
    from_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()), balance=100)
    to_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()), balance=50)

    url = '/api/v1/transactions/'

    data = {
        'from_wallet': from_wallet.public_key,
        'to_wallet': to_wallet.public_key,
        'amount': 30,
        'currency': 'ETH'
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert 'hash' in response.data

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()
    assert from_wallet.balance == 70
    assert to_wallet.balance == 80

    assert Transaction.objects.count() == 1


@pytest.mark.django_db
def test_insufficient_funds(client):
    from_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()), balance=10)
    to_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()), balance=50)

    url = '/api/v1/transactions/'

    data = {
        'from_wallet': from_wallet.public_key,
        'to_wallet': to_wallet.public_key,
        'amount': 30,
        'currency': 'ETH'
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Недостаточно средств.'


@pytest.mark.django_db
def test_wallet_not_found(client):
    url = '/api/v1/transactions/'

    data = {
        'from_wallet': '0xnonexistentfrom...',
        'to_wallet': '0xnonexistentto...',
        'amount': 10,
        'currency': 'ETH'
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Кошелек не найден.'


@pytest.mark.django_db
def test_invalid_currency(client):
    from_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()), balance=100)
    to_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()), balance=50)

    url = '/api/v1/transactions/'

    data = {
        'from_wallet': from_wallet.public_key,
        'to_wallet': to_wallet.public_key,
        'amount': 30,
        'currency': 'BTC'
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Допустима только валюта ETH.'


@pytest.mark.django_db
def test_invalid_data(client):
    url = '/api/v1/transactions/'

    data = {
        'from_wallet': '',
        'to_wallet': '',
        'amount': 'not_a_number',
        'currency': 'ETH'
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'from_wallet' in response.data
    assert 'to_wallet' in response.data
    assert 'amount' in response.data