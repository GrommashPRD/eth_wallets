from celery import shared_task
from django.conf import settings
from web3 import Web3
from .models import Wallet
import logging

# Установите соединение с сетью
w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
logger = logging.getLogger('django')


@shared_task
def update_wallet_balances():
    wallets = Wallet.objects.all()
    for wallet in wallets:
        try:
            balance_wei = w3.eth.get_balance(wallet.public_key)
            balance_ether = w3.from_wei(balance_wei, 'ether')
            wallet.balance = balance_ether
            wallet.save()
            logging.info(f'Updated balance for wallet {wallet.wallet_id}: {balance_ether} ETH')
        except Exception as inner_error:
            logging.error(f'Error retrieving balance for wallet {wallet.wallet_id}: {str(inner_error)}')