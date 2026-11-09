class CustomerNotFoundException(Exception):
    pass


class CreateOrderException(Exception):
    pass


class CreateUserException(Exception):
    pass


class CreateIDException(Exception):
    pass


class AuthenticationException(Exception):
    pass

class InvalidRequestException(Exception):
    pass

class UnsupportedAPIFeatureException(InvalidRequestException):
    """Raised when a feature is used in API key mode but is not supported by the public Meadow API."""
    pass

class ConnectionException(Exception):
    pass

class ResponseParseException(Exception):
    pass