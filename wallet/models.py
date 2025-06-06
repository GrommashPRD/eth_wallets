from django.db import models
from django.conf import settings

# Create your models here.

class Wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=3, default='ETH')
    balance = models.BigIntegerField(default=settings.DEFAULT_BALANCE)
    public_key = models.CharField(max_length=255, unique=True)
    private_key = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.public_key


class Transaction(models.Model):
    from_wallet = models.ForeignKey(Wallet, related_name='outgoing_transaction', on_delete=models.CASCADE)
    to_wallet = models.ForeignKey(Wallet, related_name='incoming_transaction', on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction from {self.from_wallet} to {self.to_wallet} for {self.amount} ETH'

