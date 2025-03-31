from celery import shared_task
from django.conf import settings
from web3 import Web3
from .models import Wallet
from django.db import IntegrityError, DatabaseError
import logging


w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
logger = logging.getLogger('django')

@shared_task
def update_wallet_balances():
    try:
        wallets = Wallet.objects.all()
        for wallet in wallets:
            try:
                balance_wei = wallet.balance
                balance_ether = w3.from_wei(balance_wei, 'ether')
                wallet.balance = balance_ether
                wallet.save()
                logging.info(f'Updated balance for wallet {wallet.wallet_id}: {balance_ether} ETH')
            except ValueError as ve:
                logger.error('Ошибка при преобразовании баланса для кошелька {wallet.address}: %(ve)s')
            except IntegrityError as ie:
                logger.error('Ошибка целостности данных при обновлении кошелька {wallet.address}: %(ie)s')
            except DatabaseError as de:
                logger.error('Ошибка базы данных при обновлении кошелька: %(de)s')
            except Exception as e:
                logger.exception('Неизвестная ошибка при обновлении кошелька: %(e)s')
    except DatabaseError as db_error:
        logger.error(f'Ошибка базы данных при получении списка кошельков: %(db_error)s')
