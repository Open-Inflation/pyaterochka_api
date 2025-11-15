"""Работа с каталогом"""

import urllib.parse
from typing import TYPE_CHECKING, Optional

from human_requests.abstraction import FetchResponse, HttpMethod

from ..enums import PurchaseMode, Sorting

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassCatalog:
    """Методы для работы с каталогом товаров.

    Включает поиск товаров, получение информации о категориях,
    работу с фидами товаров и отзывами.
    """

    def __init__(self, parent: "PyaterochkaAPI"):
        self._parent: "PyaterochkaAPI" = parent
        self.Product: ProductService = ProductService(parent=self._parent)
        """Сервис для работы с товарами в каталоге."""

    async def tree(
        self,
        sap_code_store_id: str,
        subcategories: bool = False,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
    ) -> FetchResponse:
        """
        Список категорий (глобальный).

        include_restrict - включать ли в выдачу закончившиеся в магазине товары.
        """

        request_url = f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories?mode={mode.value}&include_restrict={include_restrict}&include_subcategories={1 if subcategories else 0}"
        return await self._parent._request(
            method=HttpMethod.GET, url=request_url, add_unstandard_headers=True
        )

    async def tree_extended(
        self,
        sap_code_store_id: str,
        category_id: str,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
    ) -> FetchResponse:
        """Расширенное представление категории и её подкатегорий."""
        request_url = f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories/{category_id}/extended?mode={mode.value}&include_restrict={str(include_restrict).lower()}"
        return await self._parent._request(
            method=HttpMethod.GET, url=request_url, add_unstandard_headers=True
        )

    async def search(
        self,
        sap_code_store_id: str,
        query: str,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
        limit: int = 12,
    ) -> FetchResponse:
        """Поиск по товарам И категориям."""
        q = urllib.parse.quote(query)
        request_url = f"{self._parent.CATALOG_URL}/catalog/v3/stores/{sap_code_store_id}/search?mode={mode.value}&include_restrict={str(include_restrict).lower()}&q={q}&limit={limit}"
        return await self._parent._request(
            method=HttpMethod.GET, url=request_url, add_unstandard_headers=True
        )

    async def products_list(
        self,
        category_id: str,
        sap_code_store_id: str,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        brands: list[str] = [],
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
        limit: int = 30,
    ) -> FetchResponse:
        """
        Список категорий (основная лента каталога).

        brands - должно быть полное совпадение, другие едпоинты предоставляют их.
        """

        if limit < 1 or limit >= 500:
            raise ValueError("Limit must be between 1 and 499")

        request_url = f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories/{category_id}/products?mode={mode.value}&limit={limit}&include_restrict={str(include_restrict).lower()}"
        if price_min:
            request_url += "&price_min=" + str(price_min)
        if price_max:
            request_url += "&price_max=" + str(price_max)
        if len(brands) > 0:
            encoded_brands = [f"brands={urllib.parse.quote(brand)}" for brand in brands]
            request_url += "&" + "&&".join(encoded_brands)

        return await self._parent._request(
            method=HttpMethod.GET, url=request_url, add_unstandard_headers=True
        )

    async def products_line(
        self,
        category_id: str,
        sap_code_store_id: str,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
        order_by: Sorting = Sorting.POPULARITY,
    ) -> FetchResponse:
        """Рекомендованные товары \"что интересного?\"."""
        request_url = f"{self._parent.CATALOG_URL}/catalog/v1/stores/{sap_code_store_id}/categories/{category_id}/products_line?mode={mode.value}&include_restrict={str(include_restrict).lower()}&order_by={order_by.value}"
        return await self._parent._request(
            method=HttpMethod.GET, url=request_url, add_unstandard_headers=True
        )


class ProductService:
    """Сервис для работы с товарами в каталоге."""

    def __init__(self, parent: "PyaterochkaAPI"):
        self._parent: "PyaterochkaAPI" = parent

    async def info(
        self,
        sap_code_store_id: str,
        plu_id: int,
        mode: PurchaseMode = PurchaseMode.STORE,
        include_restrict: bool = True,
    ) -> FetchResponse:
        """
        Подробная информация о конкретном товаре.
        """
        request_url = f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/products/{plu_id}?mode={mode.value}&include_restrict={str(include_restrict).lower()}"
        return await self._parent._request(
            method=HttpMethod.GET, url=request_url, add_unstandard_headers=True
        )
