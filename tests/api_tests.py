import debian
import pytest
from pyaterochka_api import Pyaterochka
from io import BytesIO
from typed_schema_shot import SchemaShot


IS_DEBUG = True


@pytest.mark.asyncio
async def test_list(schemashot: SchemaShot):
    async with Pyaterochka(debug=IS_DEBUG, trust_env=True) as API:
        categories = await API.categories_list(subcategories=True)
        schemashot.assert_match(categories.response, "categories_list")

        result = await API.products_list(category_id=categories.response[0]['id'], limit=5)
        schemashot.assert_match(result.response, "products_list")

@pytest.mark.asyncio
async def test_product_info(schemashot: SchemaShot):
    async with Pyaterochka(debug=IS_DEBUG, trust_env=True, timeout=200.0) as API:
        result = await API.product_info(43347)
        schemashot.assert_match(result, "product_info")

@pytest.mark.asyncio
async def test_get_news(schemashot: SchemaShot):
    async with Pyaterochka(debug=IS_DEBUG, trust_env=True, timeout=3000.0) as API:
        result = await API.get_news(limit=5)
        schemashot.assert_match(result.response, "get_news")

@pytest.mark.asyncio
async def test_find_store(schemashot: SchemaShot):
    async with Pyaterochka(debug=IS_DEBUG, trust_env=True) as API:
        categories = await API.find_store(longitude=37.63156, latitude=55.73768)
        schemashot.assert_match(categories.response, "store_info")

@pytest.mark.asyncio
async def test_download_image():
    async with Pyaterochka(debug=IS_DEBUG, trust_env=True) as API:
        result = await API.download_image("https://photos.okolo.app/product/1392827-main/800x800.jpeg")
        assert isinstance(result.response, BytesIO)
        assert result.response.getvalue()

@pytest.mark.asyncio
async def test_set_debug():
    async with Pyaterochka(debug=IS_DEBUG) as API:
        assert API.BROWSER.debug == True
        API.BROWSER.debug = False
        assert API.BROWSER.debug == False

@pytest.mark.asyncio
async def test_rebuild_connection():
    async with Pyaterochka(debug=IS_DEBUG, trust_env=True) as API:
        await API.rebuild_connection()
