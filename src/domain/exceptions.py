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


class UserNotFoundException(DomainException):
    def __init__(self, tg_id: int):
        self.tg_id = tg_id
        self.message = f"User with tg_id {tg_id} not found"
        super().__init__(self.message)


class PictureNotFoundException(DomainException):
    def __init__(self, picture_id: int | None = None, message: str | None = None):
        self.picture_id = picture_id
        self.message = message or f"Picture with id {picture_id} not found"
        super().__init__(self.message)
