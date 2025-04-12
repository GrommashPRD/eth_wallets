from wallet.serializers import WalletSerializer
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from wallet.models import Wallet, Transaction
from web3 import Web3
from django.db import transaction as django_transaction
import logging


logger = logging.getLogger('django')

def new_account(request):

    w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))

    account = w3.eth.account.create()
    public_key = account.address
    private_key = w3.to_hex(account.key)

    new_wallet = Wallet.objects.create(
        public_key=public_key,
        private_key=private_key,
    )
    new_wallet.save()

    return new_wallet


def addressToAndFrom(address_to, address_from):
    address_to = Wallet.objects.filter(public_key=address_to).first()
    address_from = Wallet.objects.filter(public_key=address_from).first()

    return address_to, address_from


@django_transaction.atomic
def create_transaction(from_address, to_address, amount):
    from_address.balance -= amount
    to_address.balance += amount
    from_address.save()
    to_address.save()

    transaction = Transaction.objects.create(
        from_wallet=from_address,
        to_wallet=to_address,
        amount=amount,
    )
    return transaction


def superuser_required(function=None):
    """
    :param function:
    :return:
    """
    return user_passes_test(lambda u: u.is_superuser, login_url='/') (function)

