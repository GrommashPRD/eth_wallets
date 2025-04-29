from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from web3 import Web3

import logging

from wallet.repository.walletsRepository import ActionsWithWallets

logger = logging.getLogger('django')

def superuser_required(function=None):
    """
    :param function:
    :return:
    """
    return user_passes_test(lambda u: u.is_superuser, login_url='/') (function)


def new_account(request):

    w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))

    account = w3.eth.account.create()
    public_key = account.address
    private_key = w3.to_hex(account.key)

    new_wallet = ActionsWithWallets.new_wallet_create(
        public_key=public_key,
        private_key=private_key,
    )

    return new_wallet