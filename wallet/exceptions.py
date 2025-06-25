class InsufficientFundsError(Exception):
    pass

class DatabaseOperationError(Exception):
    pass

class ObjectAlreadyExistsError(Exception):
    pass

class WalletsAddressErrors(Exception):
    pass

class AddressFromNotFound(Exception):
    pass

class AddressToNotFound(Exception):
    pass

class InvalidCurrencyError(Exception):
    pass

class WalletsNotExistError(Exception):
    pass

class SendPaymentToYourselfError(Exception):
    pass

class ZeroAmountError(Exception):
    pass

class TransactionAddressErr(Exception):
    pass
