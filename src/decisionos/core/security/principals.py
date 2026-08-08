from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Principal:
    id: UUID
    role: str
    permissions: frozenset[str] = frozenset()


PrincipalLoader = Callable[[UUID], Awaitable[Principal | None]]
_principal_loader: PrincipalLoader | None = None


def register_principal_loader(loader: PrincipalLoader) -> None:
    global _principal_loader
    _principal_loader = loader


async def load_principal(user_id: UUID) -> Principal | None:
    if _principal_loader is None:
        raise RuntimeError("No security principal loader is registered")
    return await _principal_loader(user_id)
