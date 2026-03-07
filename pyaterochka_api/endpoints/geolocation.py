"""Геолокация."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from human_requests import ApiChild, autotest
from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassGeolocation(ApiChild["PyaterochkaAPI"]):
    """Методы для работы с геолокацией и поиском магазинов."""

    @autotest
    async def find_store(self, longitude: float, latitude: float) -> FetchResponse:
        """Найти ближайший магазин по координатам."""
        request_url = (
            f"{self._parent.CATALOG_URL}/orders/v1/orders/stores/?lon={longitude}"
            f"&lat={latitude}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)

    @autotest
    async def suggest(self, query: str) -> FetchResponse:
        """Подсказки адресов по поисковой строке."""
        request_url = (
            f"{self._parent.MAIN_SITE_URL}/api/maps/suggest/?text={quote(query)}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)

    @autotest
    async def geocode(
        self,
        country: str = "Россия",
        city: str = "Москва",
        street: str = "проспект Мира",
        house: str | None = None,
    ) -> FetchResponse:
        """Геокодирование адреса."""
        address_parts = [country, city, street]
        if house:
            address_parts.append(house)
        encoded_address = quote(", ".join(address_parts))
        request_url = (
            f"{self._parent.MAIN_SITE_URL}/api/maps/geocode/?geocode={encoded_address}"
        )
        return await self._parent._request(HttpMethod.GET, request_url)
