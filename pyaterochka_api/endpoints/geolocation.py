"""Геолокация"""
from .. import abstraction
from hrequests import Response
from urllib.parse import quote, unquote


class ClassGeolocation:
    """Методы для работы с геолокацией и выбором магазинов.
    
    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.

    Attributes
    ----------
    Selection : GeolocationSelection
        Доступ к методам выбора точек доставки и магазинов.
    Shop : ShopService
        Доступ к методам работы с магазинами.
    """
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL
    
    def find_store(self, longitude: float, latitude: float) -> Response:
        """
        Asynchronously finds the store associated with the given coordinates.

        Args:
            longitude (float): The longitude of the location.
            latitude (float): The latitude of the location.

        Returns:
            dict: A dictionary representing the store information if the request is successful, error otherwise.
        """

        request_url = f"{self.CATALOG_URL}/orders/v1/orders/stores/?lon={longitude}&lat={latitude}"
        return self._parent._request("GET", request_url)
