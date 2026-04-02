import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.catalog import Background
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.catalog import BackgroundsRepository


@dataclass
class CreateBackgroundInput:
    name: str
    description: str | None = None
    color: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True
    picture_url: str | None = None
    shop_url: str | None = None
    profile_url: str | None = None
    settings_url: str | None = None
    friends_url: str | None = None


@dataclass
class UpdateBackgroundInput:
    background_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    color: str | None = None
    cost: int | None = None
    required_level: int | None = None
    is_available: bool | None = None
    picture_url: str | None = None
    shop_url: str | None = None
    profile_url: str | None = None
    settings_url: str | None = None
    friends_url: str | None = None


class CreateBackgroundUseCase:
    def __init__(self, backgrounds_repository: BackgroundsRepository) -> None:
        self._backgrounds_repository = backgrounds_repository

    async def execute(self, data: CreateBackgroundInput) -> Background:
        background = Background(
            id=uuid.uuid4(),
            name=data.name,
            description=data.description,
            color=data.color,
            cost=data.cost,
            required_level=data.required_level,
            is_available=data.is_available,
            picture_url=data.picture_url,
            shop_url=data.shop_url,
            profile_url=data.profile_url,
            settings_url=data.settings_url,
            friends_url=data.friends_url,
        )
        return await self._backgrounds_repository.add(background)


class GetBackgroundUseCase:
    def __init__(self, backgrounds_repository: BackgroundsRepository) -> None:
        self._backgrounds_repository = backgrounds_repository

    async def execute(self, background_id: uuid.UUID) -> Background:
        background = await self._backgrounds_repository.get(background_id)
        if background is None:
            raise EntityNotFoundException(f"Background {background_id} not found")
        return background


class ListBackgroundsUseCase:
    def __init__(self, backgrounds_repository: BackgroundsRepository) -> None:
        self._backgrounds_repository = backgrounds_repository

    async def execute(self, limit: int = 100, offset: int = 0) -> list[Background]:
        return await self._backgrounds_repository.list_all(limit=limit, offset=offset)


class ListAvailableBackgroundsUseCase:
    def __init__(self, backgrounds_repository: BackgroundsRepository) -> None:
        self._backgrounds_repository = backgrounds_repository

    async def execute(self) -> list[Background]:
        return await self._backgrounds_repository.list_available()


class UpdateBackgroundUseCase:
    def __init__(self, backgrounds_repository: BackgroundsRepository) -> None:
        self._backgrounds_repository = backgrounds_repository

    async def execute(self, data: UpdateBackgroundInput) -> Background:
        background = await self._backgrounds_repository.get(data.background_id)
        if background is None:
            raise EntityNotFoundException(f"Background {data.background_id} not found")

        if data.name is not None:
            background.name = data.name
        if data.description is not None:
            background.description = data.description
        if data.color is not None:
            background.color = data.color
        if data.cost is not None:
            background.cost = data.cost
        if data.required_level is not None:
            background.required_level = data.required_level
        if data.is_available is not None:
            background.is_available = data.is_available
        if data.picture_url is not None:
            background.picture_url = data.picture_url
        if data.shop_url is not None:
            background.shop_url = data.shop_url
        if data.profile_url is not None:
            background.profile_url = data.profile_url
        if data.settings_url is not None:
            background.settings_url = data.settings_url
        if data.friends_url is not None:
            background.friends_url = data.friends_url

        return await self._backgrounds_repository.update(background)


class DeleteBackgroundUseCase:
    def __init__(self, backgrounds_repository: BackgroundsRepository) -> None:
        self._backgrounds_repository = backgrounds_repository

    async def execute(self, background_id: uuid.UUID) -> None:
        background = await self._backgrounds_repository.get(background_id)
        if background is None:
            raise EntityNotFoundException(f"Background {background_id} not found")
        await self._backgrounds_repository.delete(background_id)
