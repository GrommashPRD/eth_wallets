from celery import shared_task
from django.conf import settings
from web3 import Web3

from django.db import IntegrityError, DatabaseError
import logging

from .models import Wallet

w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
logger = logging.getLogger('django')


@shared_task
def update_wallet_balances(wallet_id):
    try:
        wallet = Wallet.objects.get(wallet_id=wallet_id)
        balance_wei = wallet.balance
        balance_ether = w3.from_wei(balance_wei, 'ether')
        logging.info(f'Updated balance for wallet {wallet_id}: {balance_ether} ETH')
        return balance_ether
    except ValueError as ve:
        logger.error('Ошибка при преобразовании баланса для кошелька {wallet.address}: %(ve)s')
    except IntegrityError as ie:
        logger.error('Ошибка целостности данных при обновлении кошелька {wallet.address}: %(ie)s')
    except DatabaseError as de:
        logger.error('Ошибка базы данных при обновлении кошелька: %(de)s')
    except Exception as e:
        logger.exception('Неизвестная ошибка при обновлении кошелька: %(e)s')


