from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from wallet.models import Wallet, Transaction
from wallet.serializers import TransactionSerializer, WalletSerializer
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from web3 import Web3
from .metrics import record_request, record_duration

from .tasks import update_wallet_balances

import time
import logging

w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
logger = logging.getLogger('django')

# Create your views here.


def superuser_required(function=None):
    return user_passes_test(lambda u: u.is_superuser, login_url='/') (function)


class WalletViewSet(APIView):

    serializer_class = WalletSerializer

    def post(self, request):

        start_time = time.time()

        serializer = WalletSerializer(data=request.data)
        currency = request.data.get('currency')

        if currency != 'ETH':
            logger.warning('Currency is not ETH')
            return JsonResponse({'error': 'Только ETH разрешен для создания кошелька'}, status=400)

        w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
        account = w3.eth.account.create()
        public_key = account.address
        private_key = w3.to_hex(account.key)

        new_wallet = Wallet.objects.create(
            public_key=public_key,
            private_key=private_key,
        )
        new_wallet.save()

        duration = time.time() - start_time
        record_request(request.method, request.path)
        record_duration(request.method, request.path, duration)

        return JsonResponse({
            'success': True,
            'wallet': {
                'id': new_wallet.wallet_id,
                'currency': new_wallet.currency,
                'public_key': new_wallet.public_key,
            }
        }, status=201)


    @method_decorator(superuser_required)
    def get(self, request):
        """
        Только superuser сможет \
        воспользоваться данным методом
        """
        start_time = time.time()

        update_wallet_balances.delay()
        try:
            wallets = Wallet.objects.all()
            if not wallets:
                logging.warning("No wallets found")
                return JsonResponse({
                    'success': False,
                    'error': 'No wallets found',
                }, status=404)

            wallets_list = []
            for wallet in wallets:
                    wallets_list.append({
                        'id': wallet.wallet_id,
                        'currency': wallet.currency,
                        'public_key': wallet.public_key,
                        'balance': str(wallet.balance),
                    })

            duration = time.time() - start_time
            record_request(request.method, request.path)
            record_duration(request.method, request.path, duration)

            return JsonResponse({
                'success': True,
                'wallets': wallets_list,
            }, status=200)

        except Exception as e:
            logging.critical(f'An unexpected error occurred: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)


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


            if currency != 'ETH':
                logger.warning("Invalid currency provided: %s. Only ETH is allowed.", currency)
                return Response({"detail": "Допустима только валюта ETH."}, status=400)

            from_wallet = Wallet.objects.filter(public_key=from_public_key).first()
            to_wallet = Wallet.objects.filter(public_key=to_public_key).first()

            if from_wallet is None or to_wallet is None:
                logger.error("Wallet not found - From wallet: %s, To wallet: %s", from_public_key, to_public_key)
                return Response({"detail": "Кошелек не найден."}, status=404)


            if amount > from_wallet.balance:
                logger.warning("Insufficient funds for wallet %s. Available balance: %s, Requested amount: %s",
                               from_public_key, from_wallet.balance, amount)
                return Response({"detail": "Недостаточно средств."}, status=400)

            from_wallet.balance -= amount
            to_wallet.balance += amount
            from_wallet.save()
            to_wallet.save()

            transaction = Transaction.objects.create(
                from_wallet=from_wallet,
                to_wallet=to_wallet,
                amount=amount,
            )

            logger.info("Transaction successful - Transaction ID: %s", transaction.id)
            duration = time.time() - start_time
            record_request(request.method, request.path)
            record_duration(request.method, request.path, duration)
            return Response({"hash": hash(str(transaction.id))}, status=201)

        logger.error("Invalid serializer data: %s", serializer.errors)
        return Response(serializer.errors, status=400)









