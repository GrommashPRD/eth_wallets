from celery import shared_task
from django.conf import settings
from prometheus_client import Counter

import logging

DB_ERRORS_TOTAL = Counter('db_errors_total', 'Total number of database errors')
DB_SPECIFIC_ERRORS_TOTAL = Counter('db_specific_errors_total', 'Total number of specific DatabaseErrors')

w3 = settings.W3
logger = logging.getLogger('django')


@shared_task
def update_wallet_balances(wallet_data):
    balance_wei = wallet_data["balance"]
    balance_ether = w3.from_wei(balance_wei, 'ether')
    return balance_ether


