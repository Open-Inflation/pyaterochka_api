from .api import PyaterochkaAPI
from enum import Enum
import re
import json
from io import BytesIO


class Pyaterochka:
    BASE_URL = "https://5ka.ru"
    API_URL = "https://5d.5ka.ru/api"
    HARDCODE_JS_CONFIG = "https://prod-cdn.5ka.ru/scripts/main.a0c039ea81eb8cf69492.js" # TODO сделать не хардкодным имя файла
    DEFAULT_STORE_ID = "Y232"

    class PurchaseMode(Enum):
        STORE = "store"
        DELIVERY = "delivery"

    def __init__(self, debug: bool = False, proxy: str = None, autoclose_browser: bool = False):
        self._debug = debug
        self._proxy = proxy
        self.api = PyaterochkaAPI(debug=self._debug, proxy=self._proxy, autoclose_browser=autoclose_browser)

    def __enter__(self):
        raise NotImplementedError("Use `async with Pyaterochka() as ...:`")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        await self.rebuild_connection(session=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def rebuild_connection(self, session: bool = True, browser: bool = False) -> None:
        """
        Rebuilds the connection to the Pyaterochka API.
        Args:
            session (bool, optional): Whether to create a new session (for all, except product_info). Defaults to True.
            browser (bool, optional): Whether to create a new browser instance (for product_info). Defaults to False.
        """
        await self.api._new_session(session, browser)

    async def close(self, session: bool = True, browser: bool = True) -> None:
        """
        Closes the connection to the Pyaterochka API.
        Args:
            session (bool, optional): Whether to close the session (for all, except product_info). Defaults to True.
            browser (bool, optional): Whether to close the browser instance (for product_info). Defaults to True.
        """
        await self.api.close(include_aiohttp=session, include_browser=browser)

    @property
    def debug(self) -> bool:
        """If True, it will print debug messages and disable headless in browser."""
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        self._debug = value
        self.api.debug = value

    @property
    def proxy(self) -> str:
        """Proxy for requests. If None, it will be used without proxy."""
        return self._proxy

    @proxy.setter
    def proxy(self, value: str):
        self._proxy = value
        self.api.proxy = value
    
    @property
    def autoclose_browser(self) -> bool:
        """If True, the browser closes after each request, clearing all cookies and caches.
        If you have more than one request and this function is enabled, the processing speed will be greatly affected! (all caches are recreated every time)"""
        return self.api._autoclose_browser

    @proxy.setter
    def autoclose_browser(self, value: bool):
        self.api._autoclose_browser = value


    async def categories_list(
            self,
            subcategories: bool = False,
            include_restrict: bool = True,
            mode: PurchaseMode = PurchaseMode.STORE,
            sap_code_store_id: str = DEFAULT_STORE_ID
    ) -> dict | None:
        f"""
        Asynchronously retrieves a list of categories from the Pyaterochka API.

        Args:
            subcategories (bool, optional): Whether to include subcategories in the response. Defaults to False.
            include_restrict (bool, optional): I DO NOT KNOW WHAT IS IT
            mode (PurchaseMode, optional): The purchase mode to use. Defaults to PurchaseMode.STORE.
            sap_code_store_id (str, optional): The store ID (official name in API is "sap_code") to use. Defaults to "{self.DEFAULT_STORE_ID}". This lib not support search ID stores.

        Returns:
            dict | None: A dictionary representing the categories list if the request is successful, None otherwise.

        Raises:
            Exception: If the response status is not 200 (OK) or 403 (Forbidden / Anti-bot).
        """

        request_url = f"{self.API_URL}/catalog/v2/stores/{sap_code_store_id}/categories?mode={mode.value}&include_restrict={include_restrict}&include_subcategories={1 if subcategories else 0}"
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

        request_url = f"{self.API_URL}/catalog/v2/stores/{sap_code_store_id}/categories/{category_id}/products?mode={mode.value}&limit={limit}"
        _is_success, response, _response_type = await self.api.fetch(url=request_url)
        return response

    async def product_info(self, plu_id: int) -> dict:
        """
        Asynchronously retrieves product information from the Pyaterochka API for a given PLU ID. Average time processing 2 seconds (first start 6 seconds).
        Args:
            plu_id (int): The PLU ID of the product.
        Returns:
            dict: A dictionary representing the product information.
        Raises:
            ValueError: If the response does not contain the expected JSON data.
        """

        url = f"{self.BASE_URL}/product/{plu_id}/"
        response = await self.api._browser_fetch(url=url, selector='script#__NEXT_DATA__[type="application/json"]')

        match = re.search(
            r'<script\s+id="__NEXT_DATA__"\s+type="application/json">(.+?)</script>',
            response,
            flags=re.DOTALL
        )
        if not match:
            raise ValueError("product_info: Failed to find JSON data in the response")
        json_text = match.group(1)
        data = json.loads(json_text)
        data["props"]["pageProps"]["props"]["productStore"] = json.loads(data["props"]["pageProps"]["props"]["productStore"])
        data["props"]["pageProps"]["props"]["catalogStore"] = json.loads(data["props"]["pageProps"]["props"]["catalogStore"])
        data["props"]["pageProps"]["props"]["filtersPageStore"] = json.loads(data["props"]["pageProps"]["props"]["filtersPageStore"])

        return data
    
    async def get_news(self, limit: int = None) -> dict | None:
        """
        Asynchronously retrieves news from the Pyaterochka API.

        Args:
            limit (int, optional): The maximum number of news items to retrieve. Defaults to None.
        
        Returns:
            dict | None: A dictionary representing the news if the request is successful, None otherwise.
        """
        url = f"{self.BASE_URL}/api/public/v1/news/"
        if limit and limit > 0:
            url += f"?limit={limit}"

        _is_success, response, _response_type = await self.api.fetch(url=url)
        
        return response

    async def find_store(self, longitude: float, latitude: float) -> dict | None:
        """
        Asynchronously finds the store associated with the given coordinates.

        Args:
            longitude (float): The longitude of the location.
            latitude (float): The latitude of the location.

        Returns:
            dict | None: A dictionary representing the store information if the request is successful, None otherwise.
        """

        request_url = f"{self.API_URL}/orders/v1/orders/stores/?lon={longitude}&lat={latitude}"
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
