import asyncio
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from decisionos.core.database.repository import BaseRepository
from decisionos.modules.identity.models import User


def test_create_flushes_and_refreshes_instance() -> None:
    async def run() -> None:
        session = Mock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        repository = BaseRepository(session, User)

        user = await repository.create(
            {"email": "user@example.com", "username": "user", "password_hash": "hash"}
        )

        assert user.email == "user@example.com"
        session.add.assert_called_once_with(user)
        session.flush.assert_awaited_once()
        session.refresh.assert_awaited_once_with(user)

    asyncio.run(run())


def test_update_changes_only_supplied_fields() -> None:
    async def run() -> None:
        session = Mock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        repository = BaseRepository(session, User)
        user = User(email="old@example.com", username="old", password_hash="hash")

        updated_user = await repository.update(user, {"email": "new@example.com"})

        assert updated_user is user
        assert user.email == "new@example.com"
        assert user.username == "old"
        session.flush.assert_awaited_once()
        session.refresh.assert_awaited_once_with(user)

    asyncio.run(run())


@pytest.mark.parametrize(("limit", "offset"), [(0, 0), (1, -1)])
def test_paginate_rejects_invalid_bounds(limit: int, offset: int) -> None:
    async def run() -> None:
        repository = BaseRepository(Mock(), User)

        with pytest.raises(ValueError):
            await repository.paginate(limit=limit, offset=offset)

    asyncio.run(run())


def test_get_by_id_delegates_to_session() -> None:
    async def run() -> None:
        session = Mock()
        session.get = AsyncMock(return_value=None)
        repository = BaseRepository(session, User)
        model_id = uuid4()

        assert await repository.get_by_id(model_id) is None
        session.get.assert_awaited_once_with(User, model_id)

    asyncio.run(run())
