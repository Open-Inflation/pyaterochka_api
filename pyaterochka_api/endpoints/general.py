"""Общий (не класифицируемый) функционал"""

from io import BytesIO
from typing import TYPE_CHECKING
from aiohttp_retry import RetryClient, ExponentialRetry


if TYPE_CHECKING:
    from ..old import ChizhikAPI


class ClassGeneral:
    """Общие методы API Чижика.

    Включает методы для работы с изображениями, формой обратной связи,
    получения информации о пользователе и других общих функций.
    """

    def __init__(self, parent: "ChizhikAPI", CATALOG_URL: str):
        self._parent: ChizhikAPI = parent
        self.CATALOG_URL: str = CATALOG_URL

    async def download_image(self, url: str) -> BytesIO:
        is_success, image_data, response_type = await self.api.fetch(url=url)

        if not is_success:
            self.api._logger.error("Failed to fetch image")
            return
        elif not isinstance(image_data, (bytes, bytearray)):
            self.api._logger.error("Image data is not bytes")
            return
        
        self.api._logger.debug("Image fetched successfully")

        image = BytesIO(image_data)
        image.name = f'{url.split("/")[-1]}.{response_type.split("/")[-1]}'

        return image
