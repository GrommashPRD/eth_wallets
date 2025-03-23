from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class TransactionSerializer(serializers.Serializer):
    from_wallet = serializers.CharField(max_length=255)
    to_wallet = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=20, decimal_places=18)
    currency = serializers.CharField(max_length=3, default='ETH')

