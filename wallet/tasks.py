from celery import shared_task
from django.conf import settings
from web3 import Web3

from django.db import IntegrityError, DatabaseError
from prometheus_client import Counter
from wallet.models import Wallet

import logging

DB_ERRORS_TOTAL = Counter('db_errors_total', 'Total number of database errors')
DB_SPECIFIC_ERRORS_TOTAL = Counter('db_specific_errors_total', 'Total number of specific DatabaseErrors')

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
        logger.error('Ошибка при преобразовании баланса для кошелька: %(ve)s', ve)
    except IntegrityError as ie:
        logger.error('Ошибка целостности данных при обновлении кошелька: %(ie)s', ie)
        DB_SPECIFIC_ERRORS_TOTAL.inc()
        DB_ERRORS_TOTAL.inc()
    except DatabaseError as de:
        logger.error('Ошибка базы данных при обновлении кошелька: %(de)s', de)
        DB_SPECIFIC_ERRORS_TOTAL.inc()
        DB_ERRORS_TOTAL.inc()


