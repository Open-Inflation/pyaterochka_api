"""Геолокация"""

from typing import TYPE_CHECKING, Optional
import urllib

from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassGeolocation:
    """Методы для работы с геолокацией и выбором магазинов.

    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.
    """

    def __init__(self, parent: "PyaterochkaAPI"):
        self._parent: PyaterochkaAPI = parent

    async def find_store(self, longitude: float, latitude: float) -> FetchResponse:
        """
        Asynchronously finds the store associated with the given coordinates.

        Args:
            longitude (float): The longitude of the location.
            latitude (float): The latitude of the location.

        Returns:
            dict: A dictionary representing the store information if the request is successful, error otherwise.
        """

        request_url = f"{self._parent.CATALOG_URL}/orders/v1/orders/stores/?lon={longitude}&lat={latitude}"
        return await self._parent._request(method=HttpMethod.GET, url=request_url, add_unstandard_headers=True)

    async def suggest(self, query: str) -> FetchResponse:
        """Начинайте вводить адрес, он предложит точные варианты"""
        request_url = f"{self._parent.MAIN_SITE_URL}/api/maps/suggest/?text={urllib.parse.quote(query)}"
        return await self._parent._request(method=HttpMethod.GET, url=request_url, add_unstandard_headers=True)

    async def geocode(self,
                      country: str = "Россия",
                      city: str = "Москва",
                      street: str = "проспект Мира",
                      house: Optional[str] = None) -> FetchResponse:
        """Возвращает геокод (геопозицию) на четкий запрос (используй suggest)"""
        tup = [country, city, street]
        if house:
            tup.append(house)
        string = urllib.parse.quote(", ".join(tup))
        
        request_url = f"{self._parent.MAIN_SITE_URL}/api/maps/geocode/?geocode={string}"
        return await self._parent._request(method=HttpMethod.GET, url=request_url, add_unstandard_headers=True)
