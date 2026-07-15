class TokenError(Exception):
    """Base exception for token validation failures"""
    pass


class ForbiddenRequest(Exception):
    """Base exception for forbidden requests failures"""
    pass


class BadRequest(Exception):
    """Base exception for forbidden requests failures"""
    pass


class UnauthorizedRequest(Exception):
    """Base exception for forbidden requests failures"""
    pass


class InvalidTokenError(TokenError):
    """Token is malformed, expired, or has an invalid signature"""
    pass


class WrongTokenTypeError(TokenError):
    """Token is valid but not the expected type (access vs refresh)"""
    pass


class NotFoundError(Exception):
    """Requested resource does not exist"""
    pass


class ConflictError(Exception):
    """Operation conflicts with existing state"""
    pass
