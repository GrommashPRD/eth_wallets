from typing import Union

from django.conf import settings
from wallet.models import Transaction
from web3 import Web3
from django.db import transaction as django_transaction

from wallet.repository.walletsRepository import ActionsWithWallets, WalletsAddressErrors

w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))


class InsufficientFundsError(Exception):
    pass


class TransactionCreator:
    model = Transaction

    def __init__(self):
        self.transaction = Transaction
        self.wallet_repo = ActionsWithWallets()

    @django_transaction.atomic
    def process_transaction(self, from_address:str, to_address:str, amount:Union[int, float]):
        try:
            address_from, address_to = self.wallet_repo.wallets_address_find(
                from_address,
                to_address
            )
        except WalletsAddressErrors:
            raise WalletsAddressErrors({
                "message": "Some address is None",
                "code": "some_address_is_none"
            })

        if address_from.balance < amount:
            raise InsufficientFundsError({"message": "Not enough balance", "code": "insufficient_funds"})

        address_from.balance -= amount
        address_to.balance += amount
        address_from.save()
        address_to.save()

        transaction = self.transaction.objects.create(
            from_wallet=address_from,
            to_wallet=address_to,
            amount=amount,
        )

        return transaction
