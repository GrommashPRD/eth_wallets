import logging

from decimal import Decimal
from django.conf import settings
from wallet.models import Wallet, Transaction
from web3 import Web3
from django.db import transaction as django_transaction
from rest_framework.response import Response

from wallet.walletsRepository import ActionsWithWallets, WalletsAddressErros

w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))

logger = logging.getLogger('django')

class InsufficientFundsError(Exception):
    pass



class TransactionCreator:

    @django_transaction.atomic
    def process_transaction(self, from_address, to_address, amount):
        try:
            address_from, address_to = ActionsWithWallets.wallets_address_find(
                from_address,
                to_address
            )
        except WalletsAddressErros as e:
            logger.warning("Address not found %s", e)
            raise WalletsAddressErros({
                "message": "Some address is None",
                "code": "some_address_is_none"
            })


        if address_from.balance < amount:
            logger.warning("Not enough balance")
            raise InsufficientFundsError({"message": "Not enough balance", "code": "insufficient_funds"})

        address_from.balance -= amount
        address_to.balance += amount
        address_from.save()
        address_to.save()

        transaction = Transaction.objects.create(
            from_wallet=address_from,
            to_wallet=address_to,
            amount=amount,
        )

        return transaction
