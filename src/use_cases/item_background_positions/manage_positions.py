import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.characters import ItemBackgroundPosition
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.characters import (
    ItemBackgroundPositionsRepository,
)


@dataclass
class CreatePositionInput:
    item_id: uuid.UUID
    background_id: uuid.UUID
    position_x: float
    position_y: float
    position_z: float = 0.0


@dataclass
class UpdatePositionInput:
    position_id: uuid.UUID
    position_x: float
    position_y: float
    position_z: float = 0.0


class ListPositionsForItemUseCase:
    def __init__(self, positions_repository: ItemBackgroundPositionsRepository) -> None:
        self._positions_repository = positions_repository

    async def execute(
        self, item_id: uuid.UUID, background_id: uuid.UUID
    ) -> list[ItemBackgroundPosition]:
        return await self._positions_repository.list_for_item_and_background(
            item_id, background_id
        )


class GetPositionUseCase:
    def __init__(self, positions_repository: ItemBackgroundPositionsRepository) -> None:
        self._positions_repository = positions_repository

    async def execute(self, position_id: uuid.UUID) -> ItemBackgroundPosition:
        position = await self._positions_repository.get_by_id(position_id)
        if position is None:
            raise EntityNotFoundException(
                f"ItemBackgroundPosition {position_id} not found"
            )
        return position


class CreatePositionUseCase:
    def __init__(self, positions_repository: ItemBackgroundPositionsRepository) -> None:
        self._positions_repository = positions_repository

    async def execute(self, data: CreatePositionInput) -> ItemBackgroundPosition:
        position = ItemBackgroundPosition(
            id=uuid.uuid4(),
            item_id=data.item_id,
            background_id=data.background_id,
            position_x=data.position_x,
            position_y=data.position_y,
            position_z=data.position_z,
        )
        return await self._positions_repository.add(position)


class UpdatePositionUseCase:
    def __init__(self, positions_repository: ItemBackgroundPositionsRepository) -> None:
        self._positions_repository = positions_repository

    async def execute(self, data: UpdatePositionInput) -> ItemBackgroundPosition:
        position = await self._positions_repository.get_by_id(data.position_id)
        if position is None:
            raise EntityNotFoundException(
                f"ItemBackgroundPosition {data.position_id} not found"
            )

        position.position_x = data.position_x
        position.position_y = data.position_y
        position.position_z = data.position_z

        return await self._positions_repository.update(position)


class DeletePositionUseCase:
    def __init__(self, positions_repository: ItemBackgroundPositionsRepository) -> None:
        self._positions_repository = positions_repository

    async def execute(self, position_id: uuid.UUID) -> None:
        position = await self._positions_repository.get_by_id(position_id)
        if position is None:
            raise EntityNotFoundException(
                f"ItemBackgroundPosition {position_id} not found"
            )
        await self._positions_repository.remove(position_id)
