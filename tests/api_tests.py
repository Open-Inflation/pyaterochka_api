import pytest
from PIL import Image
from pyaterochka_api import PyaterochkaAPI
from pytest_jsonschema_snapshot import SchemaShot


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Переопределяет фикстуру anyio_backend, чтобы использовать asyncio 
    для всей сессии, устраняя ScopeMismatch с фикстурой 'api'.
    """
    return 'asyncio' 


@pytest.fixture(scope="session")
async def api():
    """Фикстура для инициализации API в рамках сессии"""
    # anyio автоматически управляет асинхронным контекстным менеджером
    async with PyaterochkaAPI() as api_instance:
        yield api_instance


@pytest.fixture(scope="session")
async def sap_code(api: PyaterochkaAPI) -> str:
    resp = await api.delivery_panel_store()
    return resp["selectedStore"]["sapCode"]

@pytest.fixture(scope="session")
async def first_category(api: PyaterochkaAPI, sap_code: str) -> str:
    """Фикстура для получения данных категории"""
    tree_resp = await api.Catalog.tree(sap_code_store_id=sap_code)
    tree_data = tree_resp.json()
    return tree_data[0]

@pytest.fixture(scope="session")
async def product_plu(api: PyaterochkaAPI, sap_code: str, first_category: dict) -> str:
    resp = await api.Catalog.products_list(category_id=first_category["id"], sap_code_store_id=sap_code)
    data = resp.json()
    return data["products"][0]["plu"]

@pytest.fixture(scope="session")
async def geoposition(api: PyaterochkaAPI):
    resp = await api.Geolocation.geocode()
    pos: str = resp.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
    return pos.split(" ")


async def test_delivery_panel_store(api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.delivery_panel_store()
    schemashot.assert_json_match(resp, api.delivery_panel_store)

async def test_device_id(api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.device_id()
    schemashot.assert_json_match(resp, api.device_id)

async def test_tree(sap_code: str, api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Catalog.tree(sap_code_store_id=sap_code)
    data = resp.json()
    schemashot.assert_json_match(data, api.Catalog.tree)

async def test_tree_extended(sap_code: str, first_category: dict, api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Catalog.tree_extended(sap_code_store_id=sap_code, category_id=first_category["id"])
    data = resp.json()
    schemashot.assert_json_match(data, api.Catalog.tree_extended)

async def test_search(sap_code: str, api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Catalog.search(sap_code_store_id=sap_code, query="кола")
    data = resp.json()
    schemashot.assert_json_match(data, api.Catalog.search)

async def test_products_list(sap_code: str, first_category: dict, api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Catalog.products_list(category_id=first_category["id"], sap_code_store_id=sap_code)
    data = resp.json()
    schemashot.assert_json_match(data, api.Catalog.products_list)

async def test_products_line(sap_code: str, first_category: dict, api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Catalog.products_line(category_id=first_category["id"], sap_code_store_id=sap_code)
    data = resp.json()
    schemashot.assert_json_match(data, api.Catalog.products_line)

async def test_product_info(product_plu: str, sap_code: str, api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Catalog.Product.info(sap_code_store_id=sap_code, plu_id=product_plu)
    data = resp.json()
    schemashot.assert_json_match(data, api.Catalog.Product.info)

async def test_news(api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Advertising.news()
    data = resp.json()
    schemashot.assert_json_match(data, api.Advertising.news)

async def test_promo_offers(api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Advertising.promo_offers()
    data = resp.json()
    schemashot.assert_json_match(data, api.Advertising.promo_offers)

async def test_suggest(api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Geolocation.suggest("армавир")
    data = resp.json()
    schemashot.assert_json_match(data, api.Geolocation.suggest)

async def test_geocode(api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Geolocation.geocode()
    data = resp.json()
    schemashot.assert_json_match(data, api.Geolocation.geocode)

async def test_find_store(geoposition: list[float, float], api: PyaterochkaAPI, schemashot: SchemaShot):
    resp = await api.Geolocation.find_store(longitude=geoposition[0], latitude=geoposition[1])
    data = resp.json()
    schemashot.assert_json_match(data, api.Geolocation.find_store)

async def test_download_image(api: PyaterochkaAPI, first_category: dict):
    resp = await api.General.download_image(first_category["categories"][0]["image_link"])

    with Image.open(resp) as img:
        fmt = img.format.lower()
    assert fmt in ("png", "jpeg", "webp")
