# from django.core.exceptions import ValidationError
# from web3 import Web3
# from django.conf import settings
# from wallet.models import Wallet
#
# import logging
#
# w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
# logger = logging.getLogger('django')
#
# def create_wallet(currency):
#
#     if currency != 'ETH':
#         logging.error(f'Invalid currency: {currency}. Only ETH is allowed.')
#         raise ValidationError("Only ETH currency is allowed.")
#
#     account = w3.eth.account.create()
#     public_key = account.address
#     private_key = w3.to_hex(account.key)
#
#     wallet = Wallet.objects.create(
#         public_key=public_key,
#         private_key=private_key,
#     )
#
#     return wallet