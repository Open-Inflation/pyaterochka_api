from pyaterochka_api import PyaterochkaAPI
from io import BytesIO
from pytest_jsonschema_snapshot import SchemaShot


IS_DEBUG = True


# Catalog
def test_list(schemashot: SchemaShot):
    with PyaterochkaAPI(headless=IS_DEBUG) as API:
        categories = API.Catalog.tree(subcategories=True).json()
        schemashot.assert_json_match(categories, API.Catalog.tree)

        result = API.Catalog.products_list(category_id=categories[0]['id'], limit=5).json()
        schemashot.assert_json_match(result, API.Catalog.products_list)

def test_product_info(schemashot: SchemaShot):
    with PyaterochkaAPI(headless=IS_DEBUG, timeout=200.0) as API:
        result = API.Product.info(43347).json()
        schemashot.assert_json_match(result, API.Product.info)

# Advertising
def test_get_news(schemashot: SchemaShot):
    with PyaterochkaAPI(headless=IS_DEBUG, timeout=3000.0) as API:
        result = API.Advertising.get_news(limit=5).json()
        schemashot.assert_json_match(result, API.Advertising.get_news)

# Geolocation
def test_find_store(schemashot: SchemaShot):
    with PyaterochkaAPI(headless=IS_DEBUG) as API:
        categories = API.Geolocation.find_store(longitude=37.63156, latitude=55.73768).json()
        schemashot.assert_json_match(categories, API.Geolocation.find_store)

# General
def test_download_image(schemashot: SchemaShot):
    with PyaterochkaAPI(headless=IS_DEBUG) as API:
        result = API.General.download_image("https://photos.okolo.app/product/1392827-main/800x800.jpeg")
        blob = result.content
        assert isinstance(blob, bytes)
        assert len(blob) > 0
        assert blob[:8] == b"\x89PNG\r\n\x1a\n"
