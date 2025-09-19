# tests/conftest.py
import pytest_asyncio
from pyaterochka_api import PyaterochkaAPI

IS_DEBUG = False

@pytest_asyncio.fixture(scope="session")
async def api_client():
    """Один экземпляр клиента на всю сессию. Без ручного event_loop!"""
    async with PyaterochkaAPI(headless=IS_DEBUG) as api:
        yield api
