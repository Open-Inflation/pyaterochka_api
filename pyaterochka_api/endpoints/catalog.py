"""Работа с каталогом"""
from typing import Optional
from .. import abstraction
from hrequests import Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassCatalog:
    """Методы для работы с каталогом товаров.
    
    Включает поиск товаров, получение информации о категориях,
    работу с фидами товаров и отзывами.

    Attributes
    ----------
    Product : ProductService
        Сервис для работы с товарами в каталоге.
    """
    def __init__(self, parent: "PyaterochkaAPI", CATALOG_URL: str, DEFAULT_STORE_ID: str):
        self._parent: "PyaterochkaAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL
        self.DEFAULT_STORE_ID: str = DEFAULT_STORE_ID
        self.Product: ProductService = ProductService(parent=self._parent, CATALOG_URL=CATALOG_URL)

    def tree(
            self,
            subcategories: bool = False,
            include_restrict: bool = True,
            mode: abstraction.PurchaseMode = abstraction.PurchaseMode.STORE,
            sap_code_store_id: Optional[str] = None
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

        request_url = f"{self.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories?mode={mode.value}&include_restrict={include_restrict}&include_subcategories={1 if subcategories else 0}"

        return self._parent._request("GET", request_url)

    def products_list(
            self,
            category_id: str,
            mode: abstraction.PurchaseMode = abstraction.PurchaseMode.STORE,
            sap_code_store_id: Optional[str] = None,
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
        request_url = f"{self.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories/{category_id}/products?mode={mode.value}&limit={limit}"
        return self._parent._request("GET", request_url)

class ProductService:
    """Сервис для работы с товарами в каталоге."""
    def __init__(self, parent: "PyaterochkaAPI", CATALOG_URL: str):
        self._parent: "PyaterochkaAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL

    def info(self, plu_id: int) -> dict:
        """
        Asynchronously retrieves product information from the Pyaterochka API for a given PLU ID. Average time processing 2 seconds (first start 6 seconds).
        
        Args:
            plu_id (int): The PLU ID of the product.
        Returns:
            dict: A dictionary representing the product information.
        Raises:
            ValueError: If the response does not contain the expected JSON data.
        """

        url = f"{self._parent.MAIN_SITE_URL}/product/{plu_id}/"
        response = self._parent._request("GET", url)

        #match = re.search(
        #    r'<script\s+id="__NEXT_DATA__"\s+type="application/json">(.+?)</script>',
        #    real_resp.response,
        #    flags=re.DOTALL
        #)
        #if not match:
        #    raise ValueError("product_info: Failed to find JSON data in the response")
        #json_text = match.group(1)
        #data = json.loads(json_text)
        #data["props"]["pageProps"]["props"]["productStore"] = json.loads(data["props"]["pageProps"]["props"]["productStore"])
        #data["props"]["pageProps"]["props"]["catalogStore"] = json.loads(data["props"]["pageProps"]["props"]["catalogStore"])
        #data["props"]["pageProps"]["props"]["filtersPageStore"] = json.loads(data["props"]["pageProps"]["props"]["filtersPageStore"])

        return response
