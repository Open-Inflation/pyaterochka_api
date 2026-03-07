from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from camoufox import AsyncCamoufox
from human_requests import (
    ApiParent,
    HumanBrowser,
    HumanContext,
    HumanPage,
    api_child_field,
)
from human_requests.abstraction import FetchResponse, HttpMethod, Proxy
from human_requests.network_analyzer.anomaly_sniffer import (
    HeaderAnomalySniffer,
    WaitHeader,
    WaitSource,
)
from playwright.async_api import Error as PWError
from playwright.async_api import TimeoutError as PWTimeoutError

from .endpoints.advertising import ClassAdvertising
from .endpoints.catalog import ClassCatalog
from .endpoints.general import ClassGeneral
from .endpoints.geolocation import ClassGeolocation


@dataclass
class PyaterochkaAPI(ApiParent):
    """Клиент Пятёрочки."""

    timeout_ms: float = 20000.0
    """Время ожидания ответа от сервера в миллисекундах."""
    headless: bool = False
    """Запускать браузер в headless режиме?"""
    proxy: str | dict | Proxy | None = field(default_factory=Proxy.from_env)
    """Прокси для всех запросов. По умолчанию берётся из окружения."""
    browser_opts: dict[str, Any] = field(default_factory=dict)
    """Дополнительные опции браузера (см. https://camoufox.com/python/installation/)."""

    CATALOG_URL: str = "https://5d.5ka.ru/api"
    """URL для работы с каталогом."""
    SECOND_API_URL: str = "https://api.5ka.ru/api"
    """Дополнительный API для части публичных данных."""
    MAIN_SITE_URL: str = "https://5ka.ru"
    """URL главной страницы сайта."""

    session: HumanBrowser = field(init=False, repr=False)
    """Внутренняя сессия браузера для выполнения HTTP-запросов."""
    ctx: HumanContext = field(init=False, repr=False)
    """Внутренний контекст сессии браузера."""
    page: HumanPage = field(init=False, repr=False)
    """Внутренняя страница сессии браузера."""

    unstandard_headers: dict[str, str] = field(init=False, repr=False)
    """Нестандартные заголовки, собранные при прогреве."""

    Geolocation: ClassGeolocation = api_child_field(ClassGeolocation)
    """API для работы с геолокацией."""
    Catalog: ClassCatalog = api_child_field(ClassCatalog)
    """API для работы с каталогом товаров."""
    Advertising: ClassAdvertising = api_child_field(ClassAdvertising)
    """API для работы с рекламой."""
    General: ClassGeneral = api_child_field(ClassGeneral)
    """API для общих функций."""

    async def __aenter__(self) -> "PyaterochkaAPI":
        await self._warmup()
        return self

    async def _warmup(self) -> None:
        """Прогрев сессии через браузер для захвата обязательных заголовков."""
        px = self.proxy if isinstance(self.proxy, Proxy) else Proxy(self.proxy)
        br = await AsyncCamoufox(
            locale="ru-RU",
            headless=self.headless,
            proxy=px.as_dict(),
            block_images=False,
            **self.browser_opts,
        ).start()

        self.session = HumanBrowser.replace(br)
        self.ctx = await self.session.new_context()
        self.page = await self.ctx.new_page()
        self.page.on_error_screenshot_path = "screenshot.png"

        sniffer = HeaderAnomalySniffer(
            include_subresources=True,
            url_filter=lambda u: u.startswith(self.CATALOG_URL),
        )
        await sniffer.start(self.ctx)

        await self.page.goto(self.MAIN_SITE_URL, wait_until="networkidle")

        async def _click_robot_if_present() -> None:
            try:
                await self.page.locator('label[for="is-robot"].captcha-label').click(
                    timeout=self.timeout_ms,
                )
            except (PWTimeoutError, PWError):
                # captcha опциональна: ошибки клика не должны останавливать warmup
                return

        app_ready = asyncio.create_task(
            self.page.wait_for_selector("#app", timeout=self.timeout_ms)
        )
        captcha_click = asyncio.create_task(_click_robot_if_present())

        done, _pending = await asyncio.wait(
            {app_ready, captcha_click},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if app_ready in done and not captcha_click.done():
            captcha_click.cancel()
            await asyncio.gather(captcha_click, return_exceptions=True)

        await app_ready

        await sniffer.wait(
            tasks=[
                WaitHeader(
                    source=WaitSource.REQUEST,
                    headers=["x-app-version", "x-device-id", "x-platform"],
                )
            ],
            timeout_ms=self.timeout_ms,
        )

        result_sniffer = await sniffer.complete()
        unique_headers: defaultdict[str, set[str]] = defaultdict(set)

        for _url, headers in result_sniffer["request"].items():
            for header, values in headers.items():
                unique_headers[header].update(values)

        self.unstandard_headers = {
            key: list(values)[0] for key, values in unique_headers.items()
        }

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    async def delivery_panel_store(self) -> dict[str, Any]:
        """Текущий выбранный магазин/адрес доставки."""
        raw = (await self.page.local_storage()).get("DeliveryPanelStore")
        return json.loads(raw or "{}")

    async def device_id(self) -> str:
        """Анонимный идентификатор устройства, отправляемый почти в каждом запросе."""
        value = (await self.page.local_storage()).get("deviceId")
        return str(value)

    async def _request(
        self,
        method: HttpMethod,
        url: str,
        *,
        json_body: Any | None = None,
        add_unstandard_headers: bool = True,
        credentials: bool = True,
    ) -> FetchResponse:
        """Выполнить HTTP-запрос через внутреннюю браузерную сессию."""
        return await self.page.fetch(
            url=url,
            method=method,
            body=json_body,
            mode="cors",
            credentials="include" if credentials else "omit",
            timeout_ms=self.timeout_ms,
            referrer=self.MAIN_SITE_URL,
            headers={"Accept": "application/json, text/plain, */*"}
            | (self.unstandard_headers if add_unstandard_headers else {}),
        )
