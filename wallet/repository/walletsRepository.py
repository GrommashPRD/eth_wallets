from wallet.models import Wallet
from wallet.exceptions import DatabaseOperationError, ObjectAlreadyExistsError, WalletsAddressErrors, \
    WalletsNotExistError, AddressFromNotFound, AddressToNotFound
from wallet.serializers import WalletSerializer
from wallet.tasks import update_wallet_balances
from django.db import OperationalError, IntegrityError

import logging

logger = logging.getLogger('django')

class ActionsWithWallets:
    model = Wallet

    def __init__(self):
        self.WalletManager = self.model

    def get_all_wallets(self):
        try:
            wallets = self.WalletManager.objects.all()
        except OperationalError:
            raise DatabaseOperationError({
                "message": "Database connection error.",
                "code": "error_while_adding_record"
            })
        if not wallets:
            raise WalletsNotExistError({
                "message": "Wallets does not exist.",
                "code": "wallet_not_found"
            })

        return wallets

    def get_wallet_by_id(self, wallet_id: int):
        wallet = self.WalletManager.objects.get(wallet_id=wallet_id)
        if not wallet:
            logger.warning("Wallet %s does not exist.", wallet_id)
            raise WalletsNotExistError({
                "message": "Wallet does not exist.",
                "code": "wallet_not_found"
            })
        return wallet

    def new_wallet_create(self, public_key:str, private_key:str):
        try:
            new_wallet = self.WalletManager.objects.create(
                public_key=public_key,
                private_key=private_key,
            )
        except OperationalError:
            raise DatabaseOperationError({
                "message": "Database connection error.",
                "code": "error_while_adding_record"
            })
        except IntegrityError:
            raise ObjectAlreadyExistsError({
                "message": "Wallet object already exists.",
                "code": "wallet_already_exists"
            })
        return new_wallet


    def wallets_address_find(self, from_address:str, to_address:str):
        address_from = self.WalletManager.objects.filter(public_key=from_address).first()
        address_to = self.WalletManager.objects.filter(public_key=to_address).first()

        if address_from is None:
            raise AddressFromNotFound({
                "message": "Address FROM not found %s." % from_address,
                "code": "from_address_not_found"
            })
        if address_to is None:
            raise AddressToNotFound({
                "message": "Address TO not found %s." % to_address,
                "code": "to_address_not_found"
            })
        if address_from is None and address_to is None:
            raise WalletsAddressErrors({
                "message": "Addresses not found",
                "code": "from_and_to_address_not_found"
            })

        return address_from, address_to

    def each_wallet_info(self):
        wallet_list = []
        try:
            all_wallets = self.get_all_wallets()
        except DatabaseOperationError:
            raise
        except WalletsNotExistError:
            raise

        for wallet in all_wallets:
            wallet_data = WalletSerializer(wallet).data
            task = update_wallet_balances.delay(wallet_data)
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
