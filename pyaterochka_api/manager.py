from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from camoufox.async_api import AsyncCamoufox
from human_requests import HumanBrowser, HumanContext, HumanPage
from human_requests.abstraction import FetchResponse, HttpMethod, Proxy
from human_requests.network_analyzer.anomaly_sniffer import (
    HeaderAnomalySniffer, WaitHeader, WaitSource)

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

    timeout_ms: float = 10000.0
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
    SECOND_API_URL: str = "https://api.5ka.ru/api"
    """Видимо старый эндпоинт на котором сохранилась небольшая функциональность."""
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

    unstandard_headers: dict[str, str] = field(init=False, repr=False)
    """Список нестандартных заголовков пойманных при инициализации"""

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

        sniffer = HeaderAnomalySniffer(
            # доп. вайтлист, если нужно
            extra_request_allow=["x-forwarded-for", "x-real-ip"],
            extra_response_allow=[],
            # нормализуем URL: без фрагмента, но с query
            # url_normalizer=lambda u: u.split("#", 1)[0],
            include_subresources=True,  # или False, если интересны только документы
            url_filter=lambda u: u.startswith("https://5d.5ka.ru/"),
        )
        await sniffer.start(self.ctx)

        ok = False
        try_count = 3
        while not ok or try_count <= 0:
            try_count -= 1
            try:
                await self.page.goto("https://5ka.ru", wait_until="load", timeout=self.timeout_ms)
                await self.page.wait_for_selector(
                    selector="next-route-announcer", state="attached", timeout=self.timeout_ms
                )
                await self.page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
                ok = True
            except TimeoutError:
                await self.page.reload()
        if not ok:
            raise RuntimeError(self.page.content)

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
        # Результат: {заголовок: [уникальные значения]}
        result = defaultdict(set)

        # Проходим по всем URL в 'request'
        for _url, headers in result_sniffer["request"].items():
            for header, values in headers.items():
                result[header].update(values)  # добавляем значения, set уберёт дубли

        # Преобразуем set обратно в list
        self.unstandard_headers = {k: list(v) for k, v in result.items()}

    async def __aexit__(self, *exc):
        """Выход из контекстного менеджера с закрытием сессии."""
        await self.close()

    async def close(self):
        """Закрыть HTTP-сессию и освободить ресурсы."""
        await self.session.close()

    async def delivery_panel_store(self) -> dict:
        """Текущий адрес доставке (при инициализации проставляется автоматически)"""
        return json.loads((await self.page.local_storage()).get("DeliveryPanelStore"))

    async def device_id(self) -> str:
        """Анонимный (так как в библиотеке нет возможности авторизации) индефекатор пользователя,
        который отправляется на сервер почти с каждым запросом (изменить нельзя)."""
        return str((await self.page.local_storage()).get("deviceId"))

    async def _request(
        self,
        method: HttpMethod,
        url: str,
        *,
        json_body: Any | None = None,
        add_unstandard_headers: bool = True,
        credentials: bool = True,
    ) -> FetchResponse:
        """Выполнить HTTP-запрос через внутреннюю сессию.

        Единая точка входа для всех HTTP-запросов библиотеки.
        """
        # Единая точка входа в чужую библиотеку для удобства
        resp: FetchResponse = await self.page.fetch(
            url=url,
            method=method,
            body=json_body,
            mode="cors",
            credentials="include" if credentials else "omit",
            timeout_ms=self.timeout_ms,
            referrer=self.MAIN_SITE_URL,
            headers={"Accept": "application/json, text/plain, */*"}.update(
                self.unstandard_headers if add_unstandard_headers else {}
            ),
        )

        return resp
