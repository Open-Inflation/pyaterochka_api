"""Реклама"""

from typing import TYPE_CHECKING, Literal, Optional

from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.

    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """

    def __init__(self, parent: "PyaterochkaAPI"):
        self._parent: "PyaterochkaAPI" = parent

    async def news(self, limit: int = 12, offset: int = 0):
        """Список новостей. Сортировка: сначала новые"""
        request_url = f"{self._parent.SECOND_API_URL}/public/v1/news/?limit={limit}&offset={offset}"
        return await self._parent._request(
            method=HttpMethod.GET,
            url=request_url,
            add_unstandard_headers=False,
            credentials=False,
        )

    async def promo_offers(
        self,
        limit: int = 20,
        web_version: bool = True,
        type_offers: Optional[
            Literal[
                "mainpage_promotion",
                "zooclub_promotion",
                "childrenclub_promotion",
                "barclub_promotion",
            ]
        ] = None,
    ) -> FetchResponse:
        """Промо-реклама с необязательным фильтром по топику."""
        request_url = f"{self._parent.SECOND_API_URL}/public/v1/promo-offers/?limit={limit}&web_version={str(web_version).lower()}"
        if type_offers:
            request_url += f"&type={type_offers}"
        return await self._parent._request(
            method=HttpMethod.GET,
            url=request_url,
            add_unstandard_headers=False,
            credentials=False,
        )
