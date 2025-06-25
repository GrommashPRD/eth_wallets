from decimal import Decimal
from rest_framework import serializers

from .exceptions import SendPaymentToYourselfError, TransactionAddressErr, ZeroAmountError
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class TransactionSerializer(serializers.Serializer):
    from_wallet = serializers.CharField(max_length=255)
    to_wallet = serializers.CharField(max_length=255)
    amount = serializers.CharField()

    def validate(self, data):
        from_wallet = data.get('from_wallet')
        to_wallet = data.get('to_wallet')
        amount = Decimal(data.get('amount'))
        if amount <= Decimal(0):
            raise ZeroAmountError(
                {
                    "message": "Serializer validation error",
                    "code": "address_validation_error"
                })
        if not from_wallet or not to_wallet:
            raise TransactionAddressErr(
                {
                    "message": "Serializer validation error: Address can't be empty.",
                    "code": "address_validation_error"
                }
            )
        if from_wallet == to_wallet:
            raise SendPaymentToYourselfError({
                "message": "Serializer validation error: Address 'TO' = Address 'FROM'",
                "code": "address_validation_error"
            })
        return data




