from .api import PyaterochkaAPI as ClassPyaterochkaAPI
from enum import Enum
from io import BytesIO


CATALOG_URL = "https://5d.5ka.ru/api/catalog/v2/stores"
HARDCODE_JS_CONFIG = "https://prod-cdn.5ka.ru/scripts/main.a0c039ea81eb8cf69492.js" # TODO сделать не хардкодным имя файла

class PurchaseMode(Enum):
    STORE = "store"
    DELIVERY = "delivery"


PyaterochkaAPI = ClassPyaterochkaAPI(debug=False)


async def categories_list(
        subcategories: bool = False,
        mode: PurchaseMode = PurchaseMode.STORE,
        sap_code_store_id: str = "Y232"
) -> dict | None:
    """
    Asynchronously retrieves a list of categories from the Pyaterochka API.

    Args:
        subcategories (bool, optional): Whether to include subcategories in the response. Defaults to False.
        mode (PurchaseMode, optional): The purchase mode to use. Defaults to PurchaseMode.STORE.
        sap_code_store_id (str, optional): The store ID (official name in API is "sap_code") to use. Defaults to "Y232". This lib not support search ID stores.
        debug (bool, optional): Whether to print debug information. Defaults to False.

    Returns:
        dict | None: A dictionary representing the categories list if the request is successful, None otherwise.

    Raises:
        Exception: If the response status is not 200 (OK) or 403 (Forbidden / Anti-bot).
    """

    request_url = f"{CATALOG_URL}/{sap_code_store_id}/categories?mode={mode.value}&include_subcategories={1 if subcategories else 0}"
    _is_success, response, _response_type = await PyaterochkaAPI.fetch(url=request_url)
    return response

async def products_list(
        category_id: int,
        mode: PurchaseMode = PurchaseMode.STORE,
        sap_code_store_id: str = "Y232",
        limit: int = 30
) -> dict | None:
    """
    Asynchronously retrieves a list of products from the Pyaterochka API for a given category.

    Args:
        category_id (int): The ID of the category.
        mode (PurchaseMode, optional): The purchase mode to use. Defaults to PurchaseMode.STORE.
        sap_code_store_id (str, optional): The store ID (official name in API is "sap_code") to use. Defaults to "Y232". This lib not support search ID stores.
        limit (int, optional): The maximum number of products to retrieve. Defaults to 30. Must be between 1 and 499.

    Returns:
        dict | None: A dictionary representing the products list if the request is successful, None otherwise.

    Raises:
        ValueError: If the limit is not between 1 and 499.
        Exception: If the response status is not 200 (OK) or 403 (Forbidden / Anti-bot).
    """

    if limit < 1 or limit >= 500:
        raise ValueError("Limit must be between 1 and 499")

    request_url = f"{CATALOG_URL}/{sap_code_store_id}/categories/{category_id}/products?mode={mode.value}&limit={limit}"
    _is_success, response, _response_type = await PyaterochkaAPI.fetch(url=request_url)
    return response

async def download_image(url: str) -> BytesIO | None:
    is_success, image_data, response_type = await PyaterochkaAPI.fetch(url=url)

    if not is_success:
        if PyaterochkaAPI._debug:
            print("Failed to fetch image")
        return None
    elif PyaterochkaAPI._debug:
        print("Image fetched successfully")

    image = BytesIO(image_data)
    image.name = f'{url.split("/")[-1]}.{response_type.split("/")[-1]}'

    return image

async def get_config() -> list | None:
    """
    Asynchronously retrieves the configuration from the hardcoded JavaScript file.

    Args:
        debug (bool, optional): Whether to print debug information. Defaults to False.

    Returns:
        list | None: A list representing the configuration if the request is successful, None otherwise.
    """

    return await PyaterochkaAPI.download_config(config_url=HARDCODE_JS_CONFIG)


def set_debug(debug: bool) -> None:
    PyaterochkaAPI.set_debug(debug=debug)

