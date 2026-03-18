NOT_AUTHENTICATED = "Not authenticated"
INSUFFICIENT_ROLE = "Insufficient role"
USER_NOT_FOUND = "User not active or not found"


class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class DomainValidationError(DomainError):
    pass


class PermissionDeniedError(DomainError):
    pass
