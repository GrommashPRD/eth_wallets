from wallet.models import Wallet
from wallet.tasks import update_wallet_balances
from django.core.exceptions import ObjectDoesNotExist

import logging

logger = logging.getLogger('django')

class WalletsAddressErros(Exception):
    pass


class ActionsWithWallets:

    @staticmethod
    def get_all_wallets():
        """
        Возвращает все кошельки из базы данных.
        """
        return Wallet.objects.all()

    @staticmethod
    def get_wallet_by_id(wallet_id):
        try:
            wallet = Wallet.objects.get(wallet_id=wallet_id)
            return wallet
        except WalletsAddressErros:
            logger.warning('Wallet %s not found' % wallet_id)
            return None

    @staticmethod
    def new_wallet_create(public_key, private_key):

        new_wallet = Wallet.objects.create(
            public_key=public_key,
            private_key=private_key,
        )
        new_wallet.save()

        return new_wallet

    @staticmethod
    def wallets_address_find(from_address, to_address):
        address_from = Wallet.objects.filter(public_key=from_address).first()
        address_to = Wallet.objects.filter(public_key=to_address).first()

        if address_from is None:
            logger.warning("Address FROM not found")
            raise WalletsAddressErros({"message": "Address FROM not found", "code": "from_address_not_found"})

        if address_to is None:
            logger.warning("Address TO not found")
            raise WalletsAddressErros({"message": "Address TO not found", "code": "to_address_not_found"})

        if address_from is None and address_to is None:
            raise WalletsAddressErros({"message": "Address FROM and address TO not found", "code": "from_and_to_address_not_found"})

        return address_from, address_to

    @staticmethod
    def each_wallet_info():

        all_wallets = Wallet.objects.all()

        wallet_list = []

        for wallet in all_wallets:
            task = update_wallet_balances.delay(wallet.wallet_id)
            balance = task.get(timeout=10)
            wallet_list.append(
                {
                    'id': wallet.wallet_id,
                    'currency': wallet.currency,
                    'public_key': wallet.public_key,
                    'balance': balance,
                }
            )
        return wallet_list
