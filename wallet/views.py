from web3 import Web3
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.serializers import TransactionSerializer, WalletSerializer, TransactionValuesErr
from wallet.repository.transactionsRepository import InsufficientFundsError
from wallet.repository.walletsRepository import WalletsAddressErrors

from .repository import transactionsRepository, walletsRepository
from . import accounts

from prometheus_client import Counter

import logging


REQUEST_COUNTER = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'path'])

wallet_currency = settings.WALLET_CURRENCY

w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))

wallets_repo = walletsRepository.ActionsWithWallets()
transaction_repo = transactionsRepository.TransactionCreator()

logger = logging.getLogger('django')


class WalletCreateView(APIView):
    serializer_class = WalletSerializer


    def post(self, request):

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

        wallet = accounts.new_account(request)

        return Response({
            'wallet': {
                'id': wallet.wallet_id,
                'currency': wallet.currency,
                'public_key': wallet.public_key,
            }
        },
            status=201
        )


    @method_decorator(accounts.superuser_required)
    def get(self, request, repo=wallets_repo):
        REQUEST_COUNTER.labels(method='GET', path=request.path).inc()
        wallets = repo.get_all_wallets()

        if not wallets:
            logger.warning('No wallets found')
            return Response(
                {
                    "message": "No wallets found",
                    "code": "no_wallets_found"
                },
                status=400
            )

        all_wallets = repo.each_wallet_info()

        return Response(
            {
                "data": all_wallets
            },
            status=200
        )


class WalletTransactionsView(APIView):

    serializer_class = TransactionSerializer

    def post(self, request, repo=transaction_repo):
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
            transaction = repo.process_transaction(
                from_address=from_public_key,
                to_address=to_public_key,
                amount=amount_to_wei,
            )

        except InsufficientFundsError as e:
            logger.warning("Transaction failed - %s", str(e))
            return Response({
                "message": "Insufficient funds in the balance",
                "code": "insufficient_balance"
            }, status=400)
        except WalletsAddressErrors as er:
            logger.warning("Address not found %s", er)
            return Response({
                "message": "Address not found ",
                "code": "address_not_found"
            }, status=400)

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


