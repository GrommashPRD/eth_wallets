from web3 import Web3
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.models import Wallet
from wallet.serializers import TransactionSerializer, WalletSerializer, TransactionValuesErr

from . import repository
from .services import new_account, create_transaction, superuser_required, addressToAndFrom

from prometheus_client import Counter

import logging

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
            return Response({
                "message": "Currency must be ETH.", "code": "invalid_currency"
            }, status=400)

        wallet = new_account(request)

        return Response({
            'wallet': {
                'id': wallet.wallet_id,
                'currency': wallet.currency,
                'public_key': wallet.public_key,
            }
        }, status=201)


    @method_decorator(superuser_required)
    def get(self, request):
        """
        Только superuser может \
        воспользоваться данным методом \
        который отображает кошельки.
        """
        REQUEST_COUNTER.labels(method='GET', path=request.path).inc()
        wallets = Wallet.objects.all()

        if not wallets:
            logger.warning('No wallets found')
            return Response({"message": "No wallets found", "code": "no_wallets_found"}, status=400)

        prepare_wallets = repository.WalletInformation()

        all_wallets = prepare_wallets.each_wallet_info()

        return Response({"data": all_wallets}, status=200)



class WalletTransactionsView(APIView):
    """
    Выполнение транзакций \
    между кошельками \
    нашей системы
    """
    serializer_class = TransactionSerializer

    def post(self, request):

        REQUEST_COUNTER.labels(method='POST', path=request.path).inc()

        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid()
        except TransactionValuesErr as err:
            logger.warning("Serializer validation error %s", err)
            return Response({"message": "Serializer validation error", "code": "validation_error"}, status=400)

        from_public_key = serializer.validated_data['from_wallet']
        to_public_key = serializer.validated_data['to_wallet']
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data['currency']

        address_to, address_from = addressToAndFrom(to_public_key, from_public_key)
        amount_to_wei = w3.to_wei(amount, 'ether')

        if address_from is None or address_to is None:
            logger.error("Wallet not found - From wallet: %s, To wallet: %s",from_public_key, to_public_key)
            return Response({"detail": "Wallet not founded", "code": "no_wallet_yet_in_system"}, status=404)

        if amount_to_wei > address_from.balance:
            logger.warning(
                "Insufficient funds for wallet %s. Available balance: %s, Requested amount: %s",
                from_public_key,
                address_from.balance,
                 amount_to_wei
            )
            return Response({"detail": "Not enough balance.", "code": "amount_>_balance"}, status=400)

        transaction = create_transaction(address_from, address_to, amount_to_wei)

        logger.info("Transaction successful - Transaction ID: %s", transaction.id)
        return Response({"hash": hash(str(transaction.id))}, status=201)











