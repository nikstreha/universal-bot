from universal_bot.application.exeption.common import ApplicationError


class UserError(ApplicationError):
    pass


class UserNotFoundError(UserError):
    pass
