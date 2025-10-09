from dataclasses import dataclass, field
from typing import List

from src.domain.value_objects.telegram_id import TelegramId


@dataclass
class UserPictures:
    telegram_id: TelegramId
    opened_pictures: List[int] = field(default_factory=list)

    def add_opened_picture(self, picture_id: int) -> None:
        if picture_id not in self.opened_pictures:
            self.opened_pictures.append(picture_id)

    def is_picture_opened(self, picture_id: int) -> bool:
        return picture_id in self.opened_pictures

    def get_opened_count(self) -> int:
        return len(self.opened_pictures)
