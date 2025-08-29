"""Общий (не класифицируемый) функционал"""
from .. import abstraction
from hrequests import Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import PyaterochkaAPI



class ClassGeneral:
    """Общие методы API Перекрёстка.
    
    Включает методы для работы с изображениями, формой обратной связи,
    получения информации о пользователе и других общих функций.
    """
    def __init__(self, parent: "PyaterochkaAPI", CATALOG_URL: str):
        self._parent: "PyaterochkaAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL

    def download_image(self, url: str) -> Response:
        return self._parent._request("GET", url)
