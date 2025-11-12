"""Геолокация"""

from typing import TYPE_CHECKING

from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..old import ChizhikAPI


class ClassGeolocation:
    """Методы для работы с геолокацией и выбором магазинов.

    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.
    """

    def __init__(self, parent: "ChizhikAPI", CATALOG_URL: str):
        self._parent: ChizhikAPI = parent
        self.CATALOG_URL: str = CATALOG_URL

    async def find_store(self, longitude: float, latitude: float) -> dict:
        """
        Asynchronously finds the store associated with the given coordinates.

        Args:
            longitude (float): The longitude of the location.
            latitude (float): The latitude of the location.

        Returns:
            dict: A dictionary representing the store information if the request is successful, error otherwise.
        """

        request_url = f"{self.API_URL}/orders/v1/orders/stores/?lon={longitude}&lat={latitude}"
        _is_success, response, _response_type = await self.api.fetch(url=request_url)
        return response
