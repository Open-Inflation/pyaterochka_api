"""Реклама"""
from human_requests.abstraction.response import Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.
    
    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """
    def __init__(self, parent: "PyaterochkaAPI", CATALOG_URL: str):
        self._parent: "PyaterochkaAPI" = parent
        self.CATALOG_URL = CATALOG_URL
    
    async def get_news(self, limit: int | None = None) -> Response:
        """
        Asynchronously retrieves news from the Pyaterochka API.

        Args:
            limit (int, optional): The maximum number of news items to retrieve. Defaults to None.
        
        Returns:
            dict: A dictionary representing the news if the request is successful, error otherwise.
        """
        url = f"{self._parent.MAIN_SITE_URL}/api/public/v1/news/"
        if limit and limit > 0:
            url += f"?limit={limit}"

        return await self._parent._request("GET", url)