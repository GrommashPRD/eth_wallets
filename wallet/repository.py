from .models import Wallet
from .tasks import update_wallet_balances

allWallets = Wallet.objects.all()

class WalletInformation:

    def __init__(self):
        self.wallets = Wallet.objects.all()

    def each_wallet_info(self):

        wallet_list = []

        for wallet in self.wallets:
            task = update_wallet_balances.delay(wallet.wallet_id)
            balance = task.get(timeout=10)
            wallet_list.append({
                    'id': wallet.wallet_id,
                    'currency': wallet.currency,
                    'public_key': wallet.public_key,
                    'balance': balance,
            })
        return wallet_list