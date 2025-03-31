from web3 import Web3

from django.http import JsonResponse
from django.db import DatabaseError
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.models import Wallet, Transaction
from wallet.serializers import TransactionSerializer, WalletSerializer

from .metrics import record_request, record_duration
from .services import new_account, from_and_to_address, create_transaction
from .tasks import update_wallet_balances

import time
import logging


# Create your views here.
wallet_currency = settings.WALLET_CURRENCY

w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
logger = logging.getLogger('django')


def superuser_required(function=None):
    return user_passes_test(lambda u: u.is_superuser, login_url='/') (function)


class WalletViewSet(APIView):
    serializer_class = WalletSerializer

    def post(self, request):
        start_time = time.time()
        currency = request.data.get('currency')
        if currency != wallet_currency:
            logger.warning('Currency is not ETH')
            return JsonResponse({
                'error': 'Только ETH разрешен для создания кошелька'
            }, status=400)

        wallet = new_account(request)

        duration = time.time() - start_time
        record_request(request.method, request.path)
        record_duration(request.method, request.path, duration)


        return JsonResponse({
            'success': True,
            'wallet': {
                'id': wallet.wallet_id,
                'currency': wallet.currency,
                'public_key': wallet.public_key,
            }
        }, status=201)


    @method_decorator(superuser_required)
    def get(self, request):
        """
        Только superuser сможет \
        воспользоваться данным методом
        """
        start_time = time.time()
        wallets_list = []

        update_wallet_balances.delay()

        wallets = Wallet.objects.all()
        if not wallets:
            logging.warning("No wallets found")
            return JsonResponse({
                'success': False,
                'error': 'No wallets found',
            }, status=404)

        #
        #
        #
        # try:
        #     wallets = Wallet.objects.all()
        #     if not wallets:
        #         logging.warning("No wallets found")
        #         return JsonResponse({
        #             'success': False,
        #             'error': 'No wallets found',
        #         }, status=404)

        for wallet in wallets:
            try:
                balance_wei = wallet.balance
                balance_ether = w3.from_wei(balance_wei, 'ether')
                wallets_list.append({
                    'id': wallet.wallet_id,
                    'currency': wallet.currency,
                    'public_key': wallet.public_key,
                    'balance': balance_ether,
                })
            except ValueError as ve:
                logging.error('Ошибка при конвертации баланса для кошелька %s:', wallet.wallet_id)

        duration = time.time() - start_time
        record_request(request.method, request.path)
        record_duration(request.method, request.path, duration)

        return JsonResponse({
            'success': True,
            'wallets': wallets_list,
        }, status=200)
        # return JsonResponse({
        #     'success': True,
        #     'wallets': wallets_list,
        # }, status=200)


        #
        #
        # except DatabaseError as db_error:
        #     logging.error(f'Ошибка базы данных: %(db_error)s')
        #     return JsonResponse({
        #         'success': False,
        #         'error': 'Database error occurred',
        #     }, status=500)


class TransactionView(APIView):

    serializer_class = TransactionSerializer

    def post(self, request):
        start_time = time.time()

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            from_public_key = serializer.validated_data['from_wallet']
            to_public_key = serializer.validated_data['to_wallet']
            amount = serializer.validated_data['amount']
            currency = serializer.validated_data['currency']

            address_to, address_from = from_and_to_address(to_public_key, from_public_key)

            if currency != wallet_currency:
                logger.warning("Invalid currency provided: %s. Only ETH is allowed.",currency)
                return Response({"detail": "Допустима только валюта ETH."}, status=400)

            if address_from is None or address_to is None:
                logger.error("Wallet not found - From wallet: %s, To wallet: %s",from_public_key, to_public_key)
                return Response({"detail": "Кошелек не найден."}, status=404)

            if amount > address_from.balance:
                logger.warning(
                    "Insufficient funds for wallet %s. Available balance: %s, Requested amount: %s",
                    from_public_key,
                    address_from.balance,
                    amount
                )
                return Response({"detail": "Недостаточно средств."}, status=400)

            transaction = create_transaction(address_from, address_to, amount)

            logger.info("Transaction successful - Transaction ID: %s", transaction.id)
            
            duration = time.time() - start_time
            record_request(request.method, request.path)
            record_duration(request.method, request.path, duration)

            return Response({"hash": hash(str(transaction.id))}, status=201)

        logger.error("Invalid serializer data: %s", serializer.errors)
        return Response(serializer.errors, status=400)









