from django.conf import settings
from wallet.exceptions import DatabaseOperationError, ObjectAlreadyExistsError, InvalidCurrencyError, \
    WalletsNotExistError, WalletsAddressErrors, InsufficientFundsError


wallet_currency = settings.WALLET_CURRENCY

def create_new_wallet(request, repo):
    currency = request.data.get('currency')
    w3 = settings.W3

    if currency != wallet_currency:
        raise InvalidCurrencyError({
            "message": "Invalid currency provided.",
            "code": "invalid_currency_error",
        })

    account = w3.eth.account.create()
    public_key = account.address
    private_key = w3.to_hex(account.key)

    try:
        new_wallet = repo.new_wallet_create(
            public_key=public_key,
            private_key=private_key
        )
    except DatabaseOperationError as err:
        raise DatabaseOperationError(str(err))
    except ObjectAlreadyExistsError as err:
        raise ObjectAlreadyExistsError(str(err))
    return new_wallet

def get_all_wallets_info(repo):
    try:
        wallets = repo.each_wallet_info()
    except DatabaseOperationError:
        raise
    except WalletsNotExistError:
        raise
    return wallets

def send_payment(serializer, repo):
    from_public_key = serializer.validated_data['from_wallet']
    to_public_key = serializer.validated_data['to_wallet']
    amount = serializer.validated_data['amount']

    w3 = settings.W3

    amount_to_wei = w3.to_wei(amount, 'ether')

    try:
        transaction = repo.process_transaction(
            from_address=from_public_key,
            to_address=to_public_key,
            amount=amount_to_wei,
        )
    except WalletsAddressErrors:
        raise
    except InsufficientFundsError:
        raise

    return transaction








