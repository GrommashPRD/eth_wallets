from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from .models import Wallet

class TransactionValuesErr(Exception):
    """
    Обрабатываем ошибки
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
    amount = serializers.CharField()

    def validate_amount(self, value):
        try:
            amount_value = Decimal(value)
            if amount_value <= 0:
                raise TransactionValuesErr(
                    {
                        "message": "Amount must be greater than zero.",
                        "code": "invalid_amount"
                    }
                )
            return amount_value
        except InvalidOperation:
            raise TransactionValuesErr(
                {
                    "message": "Invalid amount format. Please provide a valid number.",
                    "code": "invalid_amount"
                }
            )

    def validate(self, data):
        if data['from_wallet'] is None or data['to_wallet'] is None:
            raise TransactionValuesErr(
                {
                    "message": "Address can't be empty.",
                    "code": "empty_wallets_address"
                }
            )
        return data




