from wallet.models import Wallet
from wallet.tasks import update_wallet_balances

class WalletsAddressErrors(Exception):
    pass

class ActionsWithWallets:
    model = Wallet

    def __init__(self):
        self.WalletManager = self.model


    def get_all_wallets(self):
        wallets = self.WalletManager.objects.all()
        return wallets

    def get_wallet_by_id(self, wallet_id: int):
        try:
            wallet = self.WalletManager.objects.get(wallet_id=wallet_id)
            return wallet
        except WalletsAddressErrors:
            return None

    def new_wallet_create(self, public_key:str, private_key:str):

        new_wallet = self.WalletManager.objects.create(
            public_key=public_key,
            private_key=private_key,
        )
        new_wallet.save()

        return new_wallet

    def wallets_address_find(self, from_address:str, to_address:str):
        address_from = self.WalletManager.objects.filter(public_key=from_address).first()
        address_to = self.WalletManager.objects.filter(public_key=to_address).first()

        if address_from is None:
            raise WalletsAddressErrors({"message": "Address FROM not found", "code": "from_address_not_found"})

        if address_to is None:
            raise WalletsAddressErrors({"message": "Address TO not found", "code": "to_address_not_found"})

        if address_from is None and address_to is None:
            raise WalletsAddressErrors({"message": "Address FROM and address TO not found", "code": "from_and_to_address_not_found"})

        return address_from, address_to

    def each_wallet_info(self):
        all_wallets = self.get_all_wallets()

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
