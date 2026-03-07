from __future__ import annotations

import pytest

from pyaterochka_api import PyaterochkaAPI


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def api() -> PyaterochkaAPI:
    async with PyaterochkaAPI() as client:
        yield client
