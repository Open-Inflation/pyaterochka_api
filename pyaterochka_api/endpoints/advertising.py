"""Реклама"""

from typing import TYPE_CHECKING

from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..old import ChizhikAPI


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.

    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """

    def __init__(self, parent: "ChizhikAPI", CATALOG_URL: str):
        self._parent: "ChizhikAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL

    async def get_news(self, limit: int | None = None) -> FetchResponse:
        """
        Asynchronously retrieves news from the Pyaterochka API.

        Args:
            limit (int, optional): The maximum number of news items to retrieve. Defaults to None.
        
        Returns:
            dict: A dictionary representing the news if the request is successful, error otherwise.
        """
        url = f"{self.BASE_URL}/api/public/v1/news/"
        if limit and limit > 0:
            url += f"?limit={limit}"

        _is_success, response, _response_type = await self.api.fetch(url=url)
        
        return response
