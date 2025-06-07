import re
import json
from io import BytesIO
from urllib import response
from beartype import beartype
from httpcore import NetworkError
from openai import base_url
from sympy import im
from .enums import PurchaseMode
from standard_open_inflation_package import BaseAPI, Page, Cookie
from standard_open_inflation_package.models import Request, Response, HttpMethod, Cookie
from standard_open_inflation_package.handler import Handler, HandlerSearchFailed, HandlerSearchSuccess, ExpectedContentType


class Pyaterochka:
    BASE_URL         = "https://5ka.ru"
    API_URL          = "https://5d.5ka.ru/api"
    DEFAULT_STORE_ID = "Y232"

    @beartype
    def __init__(self, **kwargs):
        self.BROWSER = BaseAPI(start_func=self._start_load, **kwargs)
        self.PAGE: Page | None = None

    @beartype
    def __enter__(self):
        raise NotImplementedError("Use `async with Pyaterochka() as ...:`")

    @beartype
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @beartype
    async def __aenter__(self):
        await self.rebuild_connection()
        return self

    @beartype
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @beartype
    async def rebuild_connection(self) -> None:
        """
        Rebuilds the connection to the Pyaterochka API.
        """
        await self.BROWSER.new_session()

    @beartype
    async def close(self) -> None:
        """
        Closes the connection to the Pyaterochka API.
        """
        await self.BROWSER.close()

    @beartype
    async def _start_load(self, tb: BaseAPI):
        self.PAGE = await tb.new_page()
        await self.PAGE.direct_fetch(self.BASE_URL)

    @beartype
    async def categories_list(
            self,
            subcategories: bool = False,
            include_restrict: bool = True,
            mode: PurchaseMode = PurchaseMode.STORE,
            sap_code_store_id: str = DEFAULT_STORE_ID
    ) -> Response:
        f"""
        Asynchronously retrieves a list of categories from the Pyaterochka API.

        Args:
            subcategories (bool, optional): Whether to include subcategories in the response. Defaults to False.
            include_restrict (bool, optional): I DO NOT KNOW WHAT IS IT
            mode (PurchaseMode, optional): The purchase mode to use. Defaults to PurchaseMode.STORE.
            sap_code_store_id (str, optional): The store ID (official name in API is "sap_code") to use. Defaults to "{self.DEFAULT_STORE_ID}". This lib not support search ID stores.

        Returns:
            list[dict]: A dictionary representing the categories list if the request is successful, error otherwise.

        Raises:
            Exception: If the response status is not 200 (OK) or 403 (Forbidden / Anti-bot).
        """

        request_url = f"{self.API_URL}/catalog/v2/stores/{sap_code_store_id}/categories?mode={mode.value}&include_restrict={include_restrict}&include_subcategories={1 if subcategories else 0}"
        response = await self.PAGE.direct_fetch(request_url, handlers=Handler.MAIN(expected_content=ExpectedContentType.JSON))
        if not isinstance(response, HandlerSearchSuccess):
            raise NetworkError("Data not found")
        real_resp = response.responses[0]
        return real_resp

    @beartype
    async def products_list(
            self,
            category_id: str,
            mode: PurchaseMode = PurchaseMode.STORE,
            sap_code_store_id: str = DEFAULT_STORE_ID,
            limit: int = 30
    ) -> Response:
        f"""
        Asynchronously retrieves a list of products from the Pyaterochka API for a given category.

        Args:
            category_id (str): The ID of the (sub)category.
            mode (PurchaseMode, optional): The purchase mode to use. Defaults to PurchaseMode.STORE.
            sap_code_store_id (str, optional): The store ID (official name in API is "sap_code") to use. Defaults to "{self.DEFAULT_STORE_ID}". This lib not support search ID stores.
            limit (int, optional): The maximum number of products to retrieve. Defaults to 30. Must be between 1 and 499.

        Returns:
            dict: A dictionary representing the products list if the request is successful, error otherwise.

        Raises:
            ValueError: If the limit is not between 1 and 499.
            Exception: If the response status is not 200 (OK) or 403 (Forbidden / Anti-bot).
        """

        if limit < 1 or limit >= 500:
            raise ValueError("Limit must be between 1 and 499")
        #               https://5ka.ru/catalog/{category_id}/?page=
        request_url = f"{self.API_URL}/catalog/v2/stores/{sap_code_store_id}/categories/{category_id}/products?mode={mode.value}&limit={limit}"
        response = await self.PAGE.direct_fetch(request_url, handlers=Handler.MAIN(expected_content=ExpectedContentType.JSON))
        if not isinstance(response, HandlerSearchSuccess):
            raise NetworkError("Data not found")
        real_resp = response.responses[0]
        return real_resp

    @beartype
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
        response = await self.PAGE.direct_fetch(url=url, wait_selector='script#__NEXT_DATA__[type="application/json"]')
        if not isinstance(response, HandlerSearchSuccess):
            raise NetworkError("Data not found")
        real_resp = response.responses[0]

        match = re.search(
            r'<script\s+id="__NEXT_DATA__"\s+type="application/json">(.+?)</script>',
            real_resp.response,
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
    
    @beartype
    async def get_news(self, limit: int | None = None) -> Response:
        """
        Asynchronously retrieves news from the Pyaterochka API.

        Args:
            limit (int, optional): The maximum number of news items to retrieve. Defaults to None.
        
        Returns:
            dict: A dictionary representing the news if the request is successful, error otherwise.
        """
        url = f"{self.BASE_URL}/api/public/v1/news/"
        if limit and limit > 0:
            url += f"?limit={limit}"

        response = await self.PAGE.direct_fetch(url, handlers=Handler.MAIN(expected_content=ExpectedContentType.JSON))
        if isinstance(response, HandlerSearchFailed):
            raise NetworkError("Data not found")
        real_resp = response.responses[0]
        
        return real_resp

    @beartype
    async def find_store(self, longitude: float, latitude: float) -> Response:
        """
        Asynchronously finds the store associated with the given coordinates.

        Args:
            longitude (float): The longitude of the location.
            latitude (float): The latitude of the location.

        Returns:
            dict: A dictionary representing the store information if the request is successful, error otherwise.
        """

        request_url = f"{self.API_URL}/orders/v1/orders/stores/?lon={longitude}&lat={latitude}"

        response = await self.PAGE.direct_fetch(request_url, handlers=Handler.MAIN(expected_content=ExpectedContentType.JSON))
        if not isinstance(response, HandlerSearchSuccess):
            raise NetworkError("Data not found")
        real_resp = response.responses[0]
        
        return real_resp

    @beartype
    async def download_image(self, url: str) -> Response:
        response = await self.PAGE.inject_fetch(url)

        if not isinstance(response, Response):
            raise NetworkError("Data not found")

        return response
