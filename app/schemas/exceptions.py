class TokenError(Exception):
    """Base exception for token validation failures"""
    pass


class InvalidTokenError(TokenError):
    """Token is malformed, expired, or has an invalid signature"""
    pass


class WrongTokenTypeError(TokenError):
    """Token is valid but not the expected type (access vs refresh)"""
    pass
