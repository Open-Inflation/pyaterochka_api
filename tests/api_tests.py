# test_catalog.py (пример)
import imghdr
import pytest
from pytest_jsonschema_snapshot import SchemaShot

import pytest
pytestmark = pytest.mark.asyncio(loop_scope="session")



# catalog
async def test_list(schemashot: SchemaShot, api_client):
    API = api_client
    categories = await API.Catalog.tree(subcategories=True)
    rjson = categories.json()
    schemashot.assert_json_match(rjson, API.Catalog.tree)

    result = await API.Catalog.products_list(category_id=rjson[0]['id'], limit=5)
    schemashot.assert_json_match(result.json(), API.Catalog.products_list)


async def test_product_info(schemashot: SchemaShot, api_client):
    API = api_client
    # если тебе нужен особый timeout только для этого теста — см. ниже примечание
    result = await API.Catalog.Product.info(43347)
    schemashot.assert_json_match(result, API.Catalog.Product.info)


async def test_get_news(schemashot: SchemaShot, api_client):
    API = api_client
    result = await API.Advertising.get_news(limit=5)
    open("test_get_news.json", "w", encoding="utf-8").write(str(result.body))
    schemashot.assert_json_match(result.json(), API.Advertising.get_news)


async def test_find_store(schemashot: SchemaShot, api_client):
    API = api_client
    categories = await API.Geolocation.find_store(longitude=37.63156, latitude=55.73768)
    schemashot.assert_json_match(categories.json(), API.Geolocation.find_store)


async def test_download_image(schemashot: SchemaShot, api_client):
    API = api_client
    result = await API.General.download_image("https://photos.okolo.app/product/1392827-main/800x800.jpeg")
    assert result.status_code == 200
    assert result.headers["content-type"].startswith("image/")
    fmt = imghdr.what(None, bytes(result.raw))
    assert fmt in ("png", "jpeg", "webp")
