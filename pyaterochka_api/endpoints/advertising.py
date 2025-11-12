"""Реклама"""

from typing import TYPE_CHECKING

from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.

    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """

    def __init__(self, parent: "PyaterochkaAPI"):
        self._parent: "PyaterochkaAPI" = parent

    async def get_news(self, limit: int | None = None) -> FetchResponse:
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

        return await self._parent._request(method=HttpMethod.GET, url=url)
