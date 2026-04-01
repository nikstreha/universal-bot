class DomainError(Exception): ...


class PermissionDeniedError(DomainError):
    """Actor does not have sufficient permissions."""


class CannotModifySuperadminError(PermissionDeniedError):
    """Cannot ban or change role of a superadmin."""


class InsufficientRoleWeightError(PermissionDeniedError):
    """Actor's role weight is not greater than the target's."""
