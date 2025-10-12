class DomainException(Exception): ...


class CoinAddException(DomainException):
    def __init__(self, message: str = "Failed to add coins", coins_amount: int = 0):
        self.coins_amount = coins_amount
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}. Amount: {self.coins_amount}"


class ExperienceAddException(DomainException):
    def __init__(
        self, message: str = "Failed to add experience", experience_amount: int = 0
    ):
        self.experience_amount = experience_amount
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}. Amount: {self.experience_amount}"


class SpendCoinException(DomainException):
    def __init__(self, message: str = "Failed to spend coins"):
        self.message = message
        super().__init__(self.message)


class InsufficientCoinsException(DomainException):
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        self.message = (
            f"Insufficient coins. Required: {required}, Available: {available}"
        )
        super().__init__(self.message)


class InsufficientLevelException(DomainException):
    def __init__(self, required_level: int, current_level: int):
        self.required_level = required_level
        self.current_level = current_level
        self.message = (
            f"Level {required_level} required. Current level: {current_level}"
        )
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Базовое исключение когда сущность не найдена"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(EntityNotFoundException):
    def __init__(self, tg_id: int):
        self.tg_id = tg_id
        super().__init__(f"User with tg_id {tg_id} not found")


class InvalidCredentialsException(DomainException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)


class InactiveUserException(DomainException):
    def __init__(self, tg_id: int):
        super().__init__(f"User with tg_id {tg_id} is inactive")


class RefreshTokenNotFoundException(EntityNotFoundException):
    def __init__(self, jti: str):
        super().__init__(f"Refresh token with jti {jti} not found")


class RefreshTokenRevokedException(DomainException):
    def __init__(self, jti: str):
        super().__init__(f"Refresh token with jti {jti} has been revoked")


class InvalidTokenException(DomainException):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class TokenExpiredException(DomainException):
    def __init__(self, message: str = "Token expired"):
        super().__init__(message)
