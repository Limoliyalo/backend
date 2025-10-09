from dataclasses import dataclass


@dataclass(frozen=True)
class Experience:
    points: int

    def __post_init__(self) -> None:
        if self.points < 0:
            raise ValueError("Experience cannot be negative")

    def add(self, value: int) -> "Experience":
        if value < 0:
            raise ValueError("Cannot add negative experience")
        return Experience(self.points + value)
