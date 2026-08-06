"""Generic asynchronous persistence primitives."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

from decisionos.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


@dataclass(frozen=True, slots=True)
class Page[ModelT: Base]:
    """A single page of database results and its total size."""

    items: Sequence[ModelT]
    total: int
    limit: int
    offset: int


class BaseRepository[ModelT: Base]:
    """Reusable database operations for one SQLAlchemy model.

    Methods flush changes but never commit. Service methods control transaction
    boundaries so a business workflow can safely compose multiple repositories.
    """

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def create(self, data: Mapping[str, Any]) -> ModelT:
        instance = self.model(**dict(data))
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, model_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, model_id)

    async def get_one(self, *filters: ColumnElement[bool]) -> ModelT | None:
        result = await self.session.execute(select(self.model).where(*filters))
        return result.scalar_one_or_none()

    async def index(
        self,
        *filters: ColumnElement[bool],
        limit: int | None = None,
        offset: int | None = None,
        order_by: InstrumentedAttribute[Any] | None = None,
    ) -> Sequence[ModelT]:
        statement = select(self.model).where(*filters)
        if order_by is not None:
            statement = statement.order_by(order_by)
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update(self, instance: ModelT, data: Mapping[str, Any]) -> ModelT:
        for field, value in data.items():
            setattr(instance, field, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def exists(self, *filters: ColumnElement[bool]) -> bool:
        statement = select(select(self.model).where(*filters).exists())
        return bool(await self.session.scalar(statement))

    async def count(self, *filters: ColumnElement[bool]) -> int:
        statement = select(func.count()).select_from(self.model).where(*filters)
        return int(await self.session.scalar(statement) or 0)

    async def paginate(
        self,
        *filters: ColumnElement[bool],
        limit: int,
        offset: int = 0,
        order_by: InstrumentedAttribute[Any] | None = None,
    ) -> Page[ModelT]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if offset < 0:
            raise ValueError("offset must not be negative")
