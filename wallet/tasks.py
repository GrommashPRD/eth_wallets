from celery import shared_task
from django.conf import settings
from web3 import Web3

from django.db import IntegrityError, DatabaseError
from prometheus_client import Counter
import logging

from wallet.repository import walletsRepository
from .models import Wallet


DB_ERRORS_TOTAL = Counter('db_errors_total', 'Total number of database errors')
DB_SPECIFIC_ERRORS_TOTAL = Counter('db_specific_errors_total', 'Total number of specific DatabaseErrors')


w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
logger = logging.getLogger('django')


@shared_task
def update_wallet_balances(wallet_id):
    wallet_repo = walletsRepository.ActionsWithWallets()
    try:
        wallet = wallet_repo.get_wallet_by_id(wallet_id=wallet_id)
        balance_wei = wallet.balance
        balance_ether = w3.from_wei(balance_wei, 'ether')
        logging.info(f'Updated balance for wallet {wallet_id}: {balance_ether} ETH')
        return balance_ether
    except ValueError as ve:
        logger.error('Ошибка при преобразовании баланса для кошелька {wallet.address}: %(ve)s')
    except IntegrityError as ie:
        logger.error('Ошибка целостности данных при обновлении кошелька {wallet.address}: %(ie)s')
        DB_SPECIFIC_ERRORS_TOTAL.inc()
        DB_ERRORS_TOTAL.inc()
    except DatabaseError as de:
        logger.error('Ошибка базы данных при обновлении кошелька: %(de)s')
        DB_SPECIFIC_ERRORS_TOTAL.inc()
        DB_ERRORS_TOTAL.inc()


