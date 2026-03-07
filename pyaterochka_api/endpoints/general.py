"""Общий (не классифицируемый) функционал."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from aiohttp_retry import ExponentialRetry, RetryClient
from human_requests import ApiChild
from human_requests.abstraction import Proxy

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI


class ClassGeneral(ApiChild["PyaterochkaAPI"]):
    """Общие методы API Пятёрочки."""

    async def download_image(
        self, url: str, retry_attempts: int = 3, timeout: float = 10
    ) -> BytesIO:
        """Скачать изображение по URL."""
        retry_options = ExponentialRetry(
            attempts=retry_attempts,
            start_timeout=3.0,
            max_timeout=timeout,
        )

        px = (
            self._parent.proxy
            if isinstance(self._parent.proxy, Proxy)
            else Proxy(self._parent.proxy)
        )
        async with RetryClient(retry_options=retry_options) as retry_client:
            async with retry_client.get(
                url,
                raise_for_status=True,
                proxy=px.as_str(),
            ) as resp:
                body = await resp.read()
                file = BytesIO(body)
                file.name = url.split("/")[-1]
        return file
