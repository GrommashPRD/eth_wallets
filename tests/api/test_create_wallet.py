# import pytest
# from django.core.exceptions import ValidationError
# from wallet.models import Wallet
# from wallet.utils.walletCreate import create_wallet  # Предположим, что ваша функция находится в wallet/utils.py
# from unittest.mock import patch
#
# import logging
#
# logger = logging.getLogger('tests')
#
# @pytest.mark.django_db
# class TestCreateWallet:
#
#     @patch('wallet.utils.walletCreate.w3.eth.account.create')
#     @patch('wallet.utils.walletCreate.w3.to_hex')
#     def test_create_wallet_success(self, mock_to_hex, mock_create):
#         mock_account = mock_create.return_value
#         mock_account.address = '0x1234567890123456789012345678901234567890'
#         mock_account.key = b'\x01' * 32  # Пример сгенерированного ключа
#
#         mock_to_hex.return_value = '0x' + '01' * 32
#
#         wallet = create_wallet(currency='ETH')
#
#         assert wallet.public_key == mock_account.address
#         assert wallet.private_key == '0x' + '01' * 32
#         assert Wallet.objects.count() == 1  # Проверка, что кошелек был создан
#
#     def test_create_wallet_invalid_currency(self):
#         with pytest.raises(ValidationError, match="Only ETH currency is allowed."):
#             create_wallet(currency='BTC')