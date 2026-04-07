class DomainError(Exception):
    pass


class PermissionDeniedError(DomainError):
    pass


class CannotModifySuperadminError(PermissionDeniedError):
    pass


class InsufficientRoleWeightError(PermissionDeniedError):
    pass
