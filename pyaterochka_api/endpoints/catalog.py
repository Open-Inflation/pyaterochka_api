"""Работа с каталогом."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import quote

from human_requests import ApiChild, ApiParent, api_child_field, autotest
from human_requests.abstraction import FetchResponse, HttpMethod

from ..enums import PurchaseMode, Sorting

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


@dataclass(init=False)
class ClassCatalog(ApiChild["PyaterochkaAPI"], ApiParent):
    """Методы для работы с каталогом товаров."""

    Product: ProductService = api_child_field(
        lambda parent: ProductService(parent.parent)
    )
    """Сервис для работы с товарами в каталоге."""

    def __init__(self, parent: "PyaterochkaAPI"):
        super().__init__(parent)
        ApiParent.__post_init__(self)

    @autotest
    async def tree(
        self,
        sap_code_store_id: str,
        subcategories: bool = False,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
    ) -> FetchResponse:
        """Список категорий."""
        request_url = (
            f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories"
            f"?mode={mode.value}&include_restrict={str(include_restrict).lower()}"
            f"&include_subcategories={1 if subcategories else 0}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)

    @autotest
    async def tree_extended(
        self,
        sap_code_store_id: str,
        category_id: str,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
    ) -> FetchResponse:
        """Расширенное представление категории и подкатегорий."""
        request_url = (
            f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories/"
            f"{category_id}/extended?mode={mode.value}"
            f"&include_restrict={str(include_restrict).lower()}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)

    @autotest
    async def search(
        self,
        sap_code_store_id: str,
        query: str,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
        limit: int = 12,
    ) -> FetchResponse:
        """Поиск по товарам и категориям."""
        encoded_query = quote(query)
        request_url = (
            f"{self._parent.CATALOG_URL}/catalog/v3/stores/{sap_code_store_id}/search"
            f"?mode={mode.value}&include_restrict={str(include_restrict).lower()}"
            f"&q={encoded_query}&limit={limit}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)

    @autotest
    async def products_list(
        self,
        category_id: str,
        sap_code_store_id: str,
        price_min: int | None = None,
        price_max: int | None = None,
        brands: list[str] | None = None,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
        limit: int = 30,
    ) -> FetchResponse:
        """Список товаров категории."""
        if limit < 1 or limit >= 500:
            raise ValueError("Limit must be between 1 and 499")

        request_url = (
            f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/categories/"
            f"{category_id}/products?mode={mode.value}&limit={limit}"
            f"&include_restrict={str(include_restrict).lower()}"
        )
        if price_min is not None:
            request_url += f"&price_min={price_min}"
        if price_max is not None:
            request_url += f"&price_max={price_max}"
        if brands:
            encoded_brands = [f"brands={quote(brand)}" for brand in brands]
            request_url += "&" + "&".join(encoded_brands)

        return await self._parent._request(HttpMethod.GET, request_url)

    @autotest
    async def products_line(
        self,
        category_id: str,
        sap_code_store_id: str,
        include_restrict: bool = True,
        mode: PurchaseMode = PurchaseMode.STORE,
        order_by: Sorting = Sorting.POPULARITY,
    ) -> FetchResponse:
        """Рекомендованные товары для категории."""
        request_url = (
            f"{self._parent.CATALOG_URL}/catalog/v1/stores/{sap_code_store_id}/categories/"
            f"{category_id}/products_line?mode={mode.value}"
            f"&include_restrict={str(include_restrict).lower()}&order_by={order_by.value}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)


class ProductService(ApiChild["PyaterochkaAPI"]):
    """Сервис для работы с товарами в каталоге."""

    @autotest
    async def info(
        self,
        sap_code_store_id: str,
        plu_id: int | str,
        mode: PurchaseMode = PurchaseMode.STORE,
        include_restrict: bool = True,
    ) -> FetchResponse:
        """Подробная информация о конкретном товаре."""
        request_url = (
            f"{self._parent.CATALOG_URL}/catalog/v2/stores/{sap_code_store_id}/products/"
            f"{plu_id}?mode={mode.value}&include_restrict={str(include_restrict).lower()}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)
