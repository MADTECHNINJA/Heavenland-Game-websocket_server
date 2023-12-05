
class JWTDecodeError(Exception):
    """
    raised if the decoding of JWT was not successful
    """


class UnauthorizedError(Exception):
    """
    raised if the request is unauthorized
    """