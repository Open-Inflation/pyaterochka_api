import pytest
from pyaterochka_api import Pyaterochka
from io import BytesIO
from typed_schema_shot import SchemaShot


@pytest.mark.asyncio
async def test_list(schemashot: SchemaShot):
    async with Pyaterochka(debug=True, trust_env=True) as API:
        categories = await API.categories_list(subcategories=True)
        schemashot.assert_match(categories, "categories_list")

        result = await API.products_list(category_id=categories[0]['id'], limit=5)
        schemashot.assert_match(result, "products_list")

@pytest.mark.asyncio
async def test_product_info(schemashot: SchemaShot):
    async with Pyaterochka(trust_env=True) as API:
        result = await API.product_info(43347)
        schemashot.assert_match(result, "product_info")

@pytest.mark.asyncio
async def test_get_news(schemashot: SchemaShot):
    async with Pyaterochka(debug=True, trust_env=True) as API:
        result = await API.get_news(limit=5)
        schemashot.assert_match(result, "get_news")

@pytest.mark.asyncio
async def test_find_store(schemashot: SchemaShot):
    async with Pyaterochka(debug=True, trust_env=True) as API:
        categories = await API.find_store(longitude=37.63156, latitude=55.73768)
        schemashot.assert_match(categories, "store_info")

@pytest.mark.asyncio
async def test_download_image(schemashot: SchemaShot):
    async with Pyaterochka(debug=True, trust_env=True) as API:
        result = await API.download_image("https://photos.okolo.app/product/1392827-main/800x800.jpeg")
        assert isinstance(result, BytesIO)
        assert result.getvalue()

@pytest.mark.asyncio
async def test_set_debug(schemashot: SchemaShot):
    async with Pyaterochka(debug=True) as API:
        assert API.debug == True
        API.debug = False
        assert API.debug == False

@pytest.mark.asyncio
async def test_rebuild_connection(schemashot: SchemaShot):
    async with Pyaterochka(debug=True, trust_env=True) as API:
        await API.rebuild_connection()

#@pytest.mark.asyncio
#async def test_get_config(snapshot: SnapshotTest):
#    async with Pyaterochka(debug=True, trust_env=True, timeout=30) as API:
#        result = await API.get_config()
#        snapshot.assert_match(gen_schema(result), "get_config")
