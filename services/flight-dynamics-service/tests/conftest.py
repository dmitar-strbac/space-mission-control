from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import get_session
from app.main import app
from app.models import Base
from app.services.runtime_store import runtime_store
from app.services.simulation_runtime import simulation_runtime_manager


@pytest.fixture(autouse=True)
def clear_runtime_store() -> Iterator[None]:
    runtime_store.clear()
    yield
    runtime_store.clear()


@pytest_asyncio.fixture
async def session(
    tmp_path: Path,
) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")

    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with factory() as test_session:
        yield test_session

    await engine.dispose()


@pytest.fixture
def client(
    session: AsyncSession,
) -> Iterator[TestClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def disable_autonomous_runtime() -> Iterator[None]:
    previous_state = simulation_runtime_manager.enabled

    simulation_runtime_manager.enabled = False

    yield

    simulation_runtime_manager.enabled = previous_state
