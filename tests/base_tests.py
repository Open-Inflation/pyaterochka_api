import pytest
from pyaterochka_api import Pyaterochka
from io import BytesIO
from snapshottest.pytest import SnapshotTest

def gen_schema(data):
    """Генерирует схему (типы данных вместо значений)."""
    if isinstance(data, dict):
        return {k: gen_schema(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [gen_schema(data[0])] if data else []
    else:
        return type(data).__name__

@pytest.mark.asyncio
async def test_list(snapshot: SnapshotTest):
    async with Pyaterochka() as API:
        categories = await API.categories_list(subcategories=True)
        snapshot.assert_match(gen_schema(categories), "categories_list")
        
        result = await API.products_list(category_id=categories[0]['id'], limit=5)
        snapshot.assert_match(gen_schema(result), "products_list")

@pytest.mark.asyncio
async def test_product_info(snapshot: SnapshotTest):
    async with Pyaterochka() as API:
        result = await API.product_info(43347)
        snapshot.assert_match(gen_schema(result), "product_info")

@pytest.mark.asyncio
async def test_get_news(snapshot: SnapshotTest):
    async with Pyaterochka() as API:
        result = await API.get_news(limit=5)
        snapshot.assert_match(gen_schema(result), "get_news")

@pytest.mark.asyncio
async def test_find_store(snapshot: SnapshotTest):
    async with Pyaterochka() as API:
        categories = await API.find_store(longitude=37.63156, latitude=55.73768)
        snapshot.assert_match(gen_schema(categories), "store_info")

@pytest.mark.asyncio
async def test_download_image(snapshot: SnapshotTest):
    async with Pyaterochka() as API:
        result = await API.download_image("https://photos.okolo.app/product/1392827-main/800x800.jpeg")
        assert isinstance(result, BytesIO)
        assert result.getvalue()
    snapshot.assert_match("image downloaded", "download_image")

@pytest.mark.asyncio
async def test_set_debug(snapshot: SnapshotTest):
    async with Pyaterochka(debug=True) as API:
        API.debug = False
        snapshot.assert_match(API.debug, "set_debug")

@pytest.mark.asyncio
async def test_rebuild_connection(snapshot: SnapshotTest):
    async with Pyaterochka() as API:
        await API.rebuild_connection()
        snapshot.assert_match("connection has been rebuilt", "rebuild_connection")

@pytest.mark.asyncio
async def test_get_config(snapshot: SnapshotTest):
    async with Pyaterochka() as API:
        result = await API.get_config()
        snapshot.assert_match(gen_schema(result), "get_config")
