from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from decisionos.core.config.settings import settings

# Connection pooling is tuned for production traffic. Each knob exists to
# protect the database from a misbehaving or overwhelmed application:
#
# * pool_size (20)      – number of connections kept open per engine. Enough
#                         to serve concurrent requests without reconnecting.
# * max_overflow (10)   – additional connections allowed on top of pool_size
#                         under a burst, then released back to the pool.
# * pool_timeout (30s)  – how long a caller waits for a connection before the
#                         pool raises "TimeoutError"; surfaces saturation.
# * pool_recycle (30m)  – PostgreSQL closes idle-forever connections; recycling
#                         about every 30 minutes prevents "connection closed"
#                         errors after long idle periods.
# * pool_pre_ping       – verifies a pooled connection is still alive before
#                         handing it out; trades a cheap SELECT for the cost of
#                         a stale-connection failure.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped session.

    The session lifespan is tied to the request: it is opened when the request
    begins and committed or rolled back once the handler finishes. Services
    flush within a transaction; the final commit is explicit in each service.
    """
    async with SessionLocal() as session:
        yield session


def get_engine() -> AsyncEngine:
    """FastAPI dependency exposing the shared async engine (used by health checks)."""
    return engine
