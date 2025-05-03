from .api import PyaterochkaAPI
from enum import Enum
from io import BytesIO


class Pyaterochka:
    CATALOG_URL = "https://5d.5ka.ru/api"
    HARDCODE_JS_CONFIG = "https://prod-cdn.5ka.ru/scripts/main.a0c039ea81eb8cf69492.js" # TODO сделать не хардкодным имя файла
    DEFAULT_STORE_ID = "Y232"

    class PurchaseMode(Enum):
        STORE = "store"
        DELIVERY = "delivery"

    def __init__(self, debug: bool = False, proxy: str = None):
        self._debug = debug
        self._proxy = proxy
        self.api = PyaterochkaAPI(debug=self._debug, proxy=self._proxy)

    def __enter__(self):
        raise NotImplementedError("Use `async with Pyaterochka() as ...:`")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        await self.rebuild_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def rebuild_connection(self) -> None:
        await self.api._new_session()

    async def close(self) -> None:
        await self.api.close()

    @property
    def debug(self) -> bool:
        """Get or set debug mode. If set to True, it will print debug messages."""
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        self._debug = value
        self.api.debug = value

    @property
    def proxy(self) -> str:
        return self._proxy

    @proxy.setter
    def proxy(self, value: str):
        self._proxy = value
        self.api.proxy = value


    async def categories_list(
            self,
            subcategories: bool = False,
            mode: PurchaseMode = PurchaseMode.STORE,
            sap_code_store_id: str = DEFAULT_STORE_ID
    ) -> dict | None:
        f"""
        Asynchronously retrieves a list of categories from the Pyaterochka API.

        Args:
            subcategories (bool, optional): Whether to include subcategories in the response. Defaults to False.
            mode (PurchaseMode, optional): The purchase mode to use. Defaults to PurchaseMode.STORE.
            sap_code_store_id (str, optional): The store ID (official name in API is "sap_code") to use. Defaults to "{self.DEFAULT_STORE_ID}". This lib not support search ID stores.
            debug (bool, optional): Whether to print debug information. Defaults to False.

        Returns:
            dict | None: A dictionary representing the categories list if the request is successful, None otherwise.

        Raises:
            Exception: If the response status is not 200 (OK) or 403 (Forbidden / Anti-bot).
        """

        request_url = f"{self.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories?mode={mode.value}&include_subcategories={1 if subcategories else 0}"
        _is_success, response, _response_type = await self.api.fetch(url=request_url)
        return response

    async def products_list(
            self,
            category_id: int,
            mode: PurchaseMode = PurchaseMode.STORE,
            sap_code_store_id: str = DEFAULT_STORE_ID,
            limit: int = 30
    ) -> dict | None:
        f"""
        Asynchronously retrieves a list of products from the Pyaterochka API for a given category.

        Args:
            category_id (int): The ID of the category.
            mode (PurchaseMode, optional): The purchase mode to use. Defaults to PurchaseMode.STORE.
            sap_code_store_id (str, optional): The store ID (official name in API is "sap_code") to use. Defaults to "{self.DEFAULT_STORE_ID}". This lib not support search ID stores.
            limit (int, optional): The maximum number of products to retrieve. Defaults to 30. Must be between 1 and 499.

        Returns:
            dict | None: A dictionary representing the products list if the request is successful, None otherwise.

        Raises:
            ValueError: If the limit is not between 1 and 499.
            Exception: If the response status is not 200 (OK) or 403 (Forbidden / Anti-bot).
        """

        if limit < 1 or limit >= 500:
            raise ValueError("Limit must be between 1 and 499")

        request_url = f"{self.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories/{category_id}/products?mode={mode.value}&limit={limit}"
        _is_success, response, _response_type = await self.api.fetch(url=request_url)
        return response

    async def find_store(self, longitude: float, latitude: float) -> dict | None:
        """
        Находит магазин закрепленный за этими координами (в понимании сервера это точка доставки заказа)
        Finds the store associated with these coordinates (in the server's understanding, this is the order delivery point).
        """

        request_url = f"{self.CATALOG_URL}/orders/v1/orders/stores/?lon={longitude}&lat={latitude}"
        _is_success, response, _response_type = await self.api.fetch(url=request_url)
        return response

    async def download_image(self, url: str) -> BytesIO | None:
        is_success, image_data, response_type = await self.api.fetch(url=url)

        if not is_success:
            if self.debug:
                print("Failed to fetch image")
            return None
        elif self.debug:
            print("Image fetched successfully")

        image = BytesIO(image_data)
        image.name = f'{url.split("/")[-1]}.{response_type.split("/")[-1]}'

        return image

    async def get_config(self) -> list | None:
        """
        Asynchronously retrieves the configuration from the hardcoded JavaScript file.

        Args:
            debug (bool, optional): Whether to print debug information. Defaults to False.

        Returns:
            list | None: A list representing the configuration if the request is successful, None otherwise.
        """

        return await self.api.download_config(config_url=self.HARDCODE_JS_CONFIG)
