from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any
import json

from camoufox.async_api import AsyncCamoufox
from human_requests import HumanBrowser, HumanContext, HumanPage
from human_requests.abstraction import FetchResponse, HttpMethod, Proxy

from .endpoints.advertising import ClassAdvertising
from .endpoints.catalog import ClassCatalog
from .endpoints.general import ClassGeneral
from .endpoints.geolocation import ClassGeolocation


def _pick_https_proxy() -> str | None:
    """Возвращает прокси из HTTPS_PROXY/https_proxy (если заданы)."""
    return os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")


@dataclass
class PyaterochkaAPI:
    """
    Клиент Пятерочки.
    """

    timeout_ms: float = 5000.0
    """Время ожидания ответа от сервера в миллисекундах."""
    headless: bool = False
    """Запускать браузер в headless режиме?"""
    proxy: str | dict | None = field(default_factory=_pick_https_proxy)
    """Прокси-сервер для всех запросов (если нужен). По умолчанию берет из окружения (если есть).
    Принимает как формат Playwright, так и строчный формат."""
    browser_opts: dict[str, Any] = field(default_factory=dict)
    """Дополнительные опции для браузера (см. https://camoufox.com/python/installation/)"""
    CATALOG_URL: str = "https://5d.5ka.ru/api"
    """URL для работы с каталогом."""
    MAIN_SITE_URL: str = "https://5ka.ru"
    """URL главной страницы сайта."""

    # будет создана в __post_init__
    session: HumanBrowser = field(init=False, repr=False)
    """Внутренняя сессия браузера для выполнения HTTP-запросов."""
    # будет создано в warmup
    ctx: HumanContext = field(init=False, repr=False)
    """Внутренний контекст сессии браузера"""
    page: HumanPage = field(init=False, repr=False)
    """Внутренний страница сессии браузера"""

    Geolocation: ClassGeolocation = field(init=False)
    """API для работы с геолокацией."""
    Catalog: ClassCatalog = field(init=False)
    """API для работы с каталогом товаров."""
    Advertising: ClassAdvertising = field(init=False)
    """API для работы с рекламой."""
    General: ClassGeneral = field(init=False)
    """API для работы с общими функциями."""

    # ───── lifecycle ─────
    def __post_init__(self) -> None:
        self.Geolocation = ClassGeolocation(self)
        self.Catalog = ClassCatalog(self)
        self.Advertising = ClassAdvertising(self)
        self.General = ClassGeneral(self)

    async def __aenter__(self):
        """Вход в контекстный менеджер с автоматическим прогревом сессии."""
        await self._warmup()
        return self

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    async def _warmup(self) -> None:
        """Прогрев сессии через браузер для получения человекоподобности."""
        br = await AsyncCamoufox(
            headless=self.headless,
            proxy=Proxy(self.proxy).as_dict() if self.proxy else None,
            **self.browser_opts,
        ).start()

        self.session = HumanBrowser.replace(br)
        self.ctx = await self.session.new_context()
        self.page = await self.ctx.new_page()

        await self.page.goto("https://5ka.ru", wait_until="load")
        await self.page.wait_for_selector(selector="next-route-announcer", state="attached")
        await self.page.wait_for_load_state('networkidle')

    async def __aexit__(self, *exc):
        """Выход из контекстного менеджера с закрытием сессии."""
        await self.close()

    async def close(self):
        """Закрыть HTTP-сессию и освободить ресурсы."""
        await self.session.close()

    async def delivery_panel_store(self) -> dict:
        """Текущий адрес доставке (при инициализации проставляется автоматически)"""
        return json.loads((await self.page.local_storage()).get("DeliveryPanelStore"))

    async def _request(
        self,
        method: HttpMethod,
        url: str,
        *,
        json_body: Any | None = None,
    ) -> FetchResponse:
        """Выполнить HTTP-запрос через внутреннюю сессию.

        Единая точка входа для всех HTTP-запросов библиотеки.

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            json_body: Тело запроса в формате JSON (опционально)
        """
        # Единая точка входа в чужую библиотеку для удобства
        print(url)
        resp: FetchResponse = await self.page.fetch(
            url=url,
            method=method,
            body=json_body,
            mode="cors",
            timeout_ms=self.timeout_ms,
            referrer=self.MAIN_SITE_URL,
            headers={"Accept": "application/json, text/plain, */*"},
        )

        return resp
