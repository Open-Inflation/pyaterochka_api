"""Реклама"""

from typing import TYPE_CHECKING, Literal

from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.

    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """

    def __init__(self, parent: "PyaterochkaAPI"):
        self._parent: "PyaterochkaAPI" = parent

    async def news(self,
                   limit: int = 12,
                   offset: int = 0):
        request_url = f"{self._parent.CATALOG_URL}/public/v1/news/?limit={limit}&offset={offset}"
        return await self._parent._request(method=HttpMethod.GET, url=request_url)

    async def promo_offers(self,
                       limit: int = 20,
                       web_version: bool = True,
                       type_offers: Literal["mainpage_promotion",
                                            "zooclub_promotion",
                                            "childrenclub_promotion",
                                            "barclub_promotion"] = "mainpage_promotion") -> FetchResponse:
        request_url = f"{self._parent.CATALOG_URL}/public/v1/promo-offers/?limit={limit}&web_version={str(web_version).lower()}&type={type_offers}"
        return await self._parent._request(method=HttpMethod.GET, url=request_url)
