from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.serializers import TransactionSerializer, WalletSerializer
from .exceptions import *

from .repository import transactionsRepository, walletsRepository
from . import accounts
from .usecase import usecase

from prometheus_client import Counter

import logging

w3 = settings.W3
REQUEST_COUNTER = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'path'])

wallet_currency = settings.WALLET_CURRENCY

logger = logging.getLogger('django')

class WalletCreateView(APIView):
    serializer_class = WalletSerializer
    wallets_repo = walletsRepository.ActionsWithWallets()

    def post(self, request):
        REQUEST_COUNTER.labels(method='POST', path=request.path).inc()
        try:
            wallet = usecase.create_new_wallet(request, repo=self.wallets_repo)
        except DatabaseOperationError as err:
            logger.warning('Database operation error %s', err)
            return Response({
                "message": "An error occurred when adding an entry"
            },status=500)
        except ObjectAlreadyExistsError as err:
            logger.warning('Object already exists error %s', err)
            return Response({
                "message": "Adding object already exists.",
            },status=400)
        except InvalidCurrencyError as err:
            logger.warning('Invalid currency error %s', err)
            return Response({
                "message": "Invalid currency. Only ETH currencies are supported.",
            }, status=400)

        return Response({
            "message": "OK",
            "wallet": {
                'id': wallet.wallet_id,
                'currency': wallet.currency,
                'public_key': wallet.public_key,
            },
        }, status=201)

    @method_decorator(accounts.superuser_required)
    def get(self, request):
        REQUEST_COUNTER.labels(method='GET', path=request.path).inc()
        try:
            wallets = usecase.get_all_wallets_info(repo=self.wallets_repo)
        except DatabaseOperationError as err:
            logger.warning('Database operation error %s', err)
            return Response({
                "message": "An error occurred when adding an entry"
            }, status=500)
        except WalletsNotExistError as err:
            logger.warning("Wallets doesn't exist %s", err)
            return Response({
                "message": "Wallets doesn't exist",
            }, status=404)

        return Response({
                "message": "OK",
                "wallets": wallets,
        },status=200)

class WalletTransactionsView(APIView):
    serializer_class = TransactionSerializer
    transaction_repo = transactionsRepository.TransactionCreator()

    def post(self, request):
        REQUEST_COUNTER.labels(method='POST', path=request.path).inc()
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid()
        except ZeroAmountError as err:
            logger.warning("Serializer validation error %s",err)
            return Response({
                "message": "Amount must be greater than zero.",
            },status=400)
        except TransactionAddressErr as err:
            logger.warning("Serializer validation error %s",err)
            return Response({
                "message": "Address cant be empty",
            }, status=404)
        except SendPaymentToYourselfError as err:
            logger.warning("Serializer validation error %s",err)
            return Response({
                "message": "You can't send transfers to yourself.",
            })

        try:
            payment = usecase.send_payment(serializer, repo=self.transaction_repo)
        except InsufficientFundsError as e:
            logger.warning("Transaction failed - %s", str(e))
            return Response({
                "message": "Insufficient funds in the balance",
            }, status=400)
        except AddressToNotFound as err:
            logger.warning("Transaction failed - Address 'TO' not found %s", str(err))
            return Response({
                "message": "Address 'TO' not found",
            }, status=404)
        except AddressFromNotFound as err:
            logger.warning("Transaction failed - Address 'FROM' not found %s", str(err))
            return Response({
                "message": "Address 'FROM' not found",
            }, status=404)
        except WalletsAddressErrors as er:
            logger.warning("Address not found %s", er)
            return Response({
                "message": "Address not found ",
            }, status=400)

        logger.info(
            "Transaction successful - Transaction ID: %s",
            payment.id
        )
        return Response(
            {
                "message": "OK",
                "transaction ID": hash(str(payment.id))
            },status=201)