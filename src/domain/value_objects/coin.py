from dataclasses import dataclass


@dataclass(frozen=True)
class Coin:
    amount: int

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Coins cannot be negative")

    def add(self, value: int) -> "Coin":
        if value < 0:
            raise ValueError("Cannot add negative coins")
        return Coin(self.amount + value)

    def subtract(self, value: int) -> "Coin":
        if value < 0:
            raise ValueError("Cannot subtract negative coins")
        remaining = self.amount - value
        if remaining < 0:
            raise ValueError("Insufficient coins")
        return Coin(remaining)
