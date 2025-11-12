"""Геолокация"""

from typing import TYPE_CHECKING

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
        return await self._parent._request(method=HttpMethod.GET, url=request_url)
