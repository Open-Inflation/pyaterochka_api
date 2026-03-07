"""Реклама."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from human_requests import ApiChild, autotest
from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassAdvertising(ApiChild["PyaterochkaAPI"]):
    """Методы для работы с рекламными материалами."""

    @autotest
    async def news(self, limit: int = 12, offset: int = 0) -> FetchResponse:
        """Список новостей, сортировка: сначала новые."""
        request_url = (
            f"{self._parent.SECOND_API_URL}/public/v1/news/?limit={limit}&offset={offset}"
        )
        return await self._parent._request(
            HttpMethod.GET,
            request_url,
            add_unstandard_headers=False,
            credentials=False,
        )

    @autotest
    async def promo_offers(
        self,
        limit: int = 20,
        web_version: bool = True,
        type_offers: Literal[
            "mainpage_promotion",
            "zooclub_promotion",
            "childrenclub_promotion",
            "barclub_promotion",
        ]
        | None = None,
    ) -> FetchResponse:
        """Промо-реклама с необязательным фильтром по типу."""
        request_url = (
            f"{self._parent.SECOND_API_URL}/public/v1/promo-offers/?limit={limit}"
            f"&web_version={str(web_version).lower()}"
        )
        if type_offers:
            request_url += f"&type={type_offers}"
        return await self._parent._request(
            HttpMethod.GET,
            request_url,
            add_unstandard_headers=False,
            credentials=False,
        )
