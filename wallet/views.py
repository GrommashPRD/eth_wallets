from web3 import Web3
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.serializers import TransactionSerializer, WalletSerializer, TransactionValuesErr

from . import walletsRepository, transactionsRepository
from .accounts import superuser_required, new_account

from prometheus_client import Counter

import logging

from .transactionsRepository import InsufficientFundsError
from .walletsRepository import WalletsAddressErros

# Create your views here.
REQUEST_COUNTER = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'path'])

wallet_currency = settings.WALLET_CURRENCY

w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))

logger = logging.getLogger('django')


class WalletCreateView(APIView):
    serializer_class = WalletSerializer

    def post(self, request):
        """
        Создание кошелька
        """
        REQUEST_COUNTER.labels(method='POST', path=request.path).inc()
        currency = request.data.get('currency')

        if currency != wallet_currency:
            logger.warning('Currency is not ETH')
            return Response(
                {
                "message": "Currency must be ETH.",
                "code": "invalid_currency"
                },
                status=400
            )

        wallet = new_account(request)

        return Response({
            'wallet': {
                'id': wallet.wallet_id,
                'currency': wallet.currency,
                'public_key': wallet.public_key,
            }
        },
            status=201
        )


    @method_decorator(superuser_required)
    def get(self, request):
        """
        Только superuser может \
        воспользоваться данным методом \
        который отображает кошельки.
        """

        REQUEST_COUNTER.labels(method='GET', path=request.path).inc()

        wallets_repo = walletsRepository.ActionsWithWallets()

        wallets = wallets_repo.get_all_wallets()

        if not wallets:
            logger.warning('No wallets found')
            return Response(
                {
                    "message": "No wallets found",
                    "code": "no_wallets_found"
                },
                status=400
            )

        all_wallets = wallets_repo.each_wallet_info()

        return Response(
            {
                "data": all_wallets
            },
            status=200
        )



class WalletTransactionsView(APIView):
    """
    Выполнение транзакций \
    между кошельками \
    нашей системы
    """
    serializer_class = TransactionSerializer


    def post(self, request):

        transaction_repo = transactionsRepository.TransactionCreator()

        REQUEST_COUNTER.labels(method='POST', path=request.path).inc()

        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid()
        except TransactionValuesErr as err:
            logger.warning(
                "Serializer validation error %s",
                err
            )
            return Response({
                "message": "Serializer validation error",
                "code": "validation_error"
            },
                status=400
            )

        amount = serializer.validated_data['amount']
        from_public_key = serializer.validated_data['from_wallet']
        to_public_key = serializer.validated_data['to_wallet']


        amount_to_wei = w3.to_wei(amount, 'ether')

        try:

            transaction = transaction_repo.process_transaction(
                from_address=from_public_key,
                to_address=to_public_key,
                amount=amount_to_wei,
            )

            logger.info(
                "Transaction successful - Transaction ID: %s",
                transaction.id
            )
            return Response(
                {
                    "hash": hash(str(transaction.id))
                },
                status=201
            )
        except InsufficientFundsError as e:
            logger.warning("Transaction failed - %s", str(e))
            return Response({
                "message": "Insufficient funds in the balance",
                "code": "insufficient_balance"
            }, status=400)
        except WalletsAddressErros as er:
            logger.warning("Address not found %s", er)
            return Response({
                "message": "Address not found ",
                "code": "address_not_found"
            }, status=400)


