import pytest
from rest_framework import status
from wallet.models import Wallet, Transaction
import uuid
import logging

logger = logging.getLogger('tests')


@pytest.mark.django_db
def test_successful_transaction(client):
    from_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()))
    to_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()))

    url = '/api/v1/transactions/'

    data = {
        'from_wallet': from_wallet.public_key,
        'to_wallet': to_wallet.public_key,
        'amount': "0.25",
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert 'message' in response.data
    assert response.data['message'] == 'OK'

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()

    assert Transaction.objects.count() == 1


@pytest.mark.django_db
def test_insufficient_funds(client):
    from_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()))
    to_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()))

    url = '/api/v1/transactions/'

    data = {
        'from_wallet': from_wallet.public_key,
        'to_wallet': to_wallet.public_key,
        'amount': "30",
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "message": "Insufficient funds in the balance"
    }


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
    assert response.data == {"message": "Address 'FROM' not found"}


@pytest.mark.django_db
def test_invalid_currency(client):
    from_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()))
    to_wallet = Wallet.objects.create(public_key=str(uuid.uuid4()), private_key=str(uuid.uuid4()))

    url = '/api/v1/transactions/'

    data = {
        'from_wallet': from_wallet.public_key,
        'to_wallet': to_wallet.public_key,
        'amount': 30,
        'currency': 'BTC'
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"message": "Insufficient funds in the balance"}



@pytest.mark.django_db
def test_invalid_data(client):
    url = '/api/v1/transactions/'

    data = {
        "from_wallet": "0x4fB3aC27D015f146965d1AaE7fhbBb80220BEA1a506",
        "to_wallet": "0x858e3A2414fe77A7C4eBbE4A836C8dfgF1600caEFf9",
        "amount": 0.24
    }

    response = client.post(url, data=data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {"message": "Address 'FROM' not found"}