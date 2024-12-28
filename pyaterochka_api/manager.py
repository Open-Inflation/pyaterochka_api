from .api import main_fetch, download_hardcode_config
from enum import Enum

CATALOG_URL = "https://5d.5ka.ru/api/catalog/v2/stores"
HARDCODE_JS_CONFIG = "https://prod-cdn.5ka.ru/scripts/main.a0c039ea81eb8cf69492.js" # TODO сделать не хардкодным имя файла

class PurchaseMode(Enum):
    STORE = "store"
    DELIVERY = "delivery"


async def categories_list(
        subcategories: bool = False,
        mode: PurchaseMode = PurchaseMode.STORE,
        sap_code_store_id: str = "Y232",
        debug: bool = False
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
    is_success, response = await main_fetch(url=request_url, debug=debug)
    return response


async def products_list(
        category_id: int,
        mode: PurchaseMode = PurchaseMode.STORE,
        sap_code_store_id: str = "Y232",
        limit: int = 30,
        debug: bool = False
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
    is_success, response = await main_fetch(url=request_url, debug=debug)
    return response


async def get_config(debug: bool = False) -> list | None:
    """
    Asynchronously retrieves the configuration from the hardcoded JavaScript file.

    Args:
        debug (bool, optional): Whether to print debug information. Defaults to False.

    Returns:
        list | None: A list representing the configuration if the request is successful, None otherwise.
    """

    return await download_hardcode_config(config_url=HARDCODE_JS_CONFIG, debug=debug)
