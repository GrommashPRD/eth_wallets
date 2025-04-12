from decimal import Decimal
from rest_framework import serializers
from .models import Wallet

class TransactionValuesErr(Exception):
    """
    Обрабатываем ошибки \
    значений для транзакций.
    """
    pass

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class TransactionSerializer(serializers.Serializer):
    from_wallet = serializers.CharField(max_length=255)
    to_wallet = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=20, decimal_places=18)
    currency = serializers.CharField(max_length=3, default='ETH')

    def validate(self, data):
        if data['amount'] <= Decimal("0.00"):
            raise TransactionValuesErr({"message": "Amount must be greater than zero.", "code": "invalid_amount"})
        if data['currency'] != "ETH":
            raise TransactionValuesErr({"message": "Currency must be ETH.", "code": "invalid_currency"})

        return data




