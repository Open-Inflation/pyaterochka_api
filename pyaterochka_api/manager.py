from encodings.punycode import T
import os
from dataclasses import dataclass, field
from typing import Any, Literal
import human_requests
import json

import human_requests
import human_requests.abstraction.response
from human_requests.impersonation import ImpersonationConfig, Policy

import human_requests.abstraction
from .endpoints.advertising import ClassAdvertising
from .endpoints.catalog import ClassCatalog
from .endpoints.general import ClassGeneral
from .endpoints.geolocation import ClassGeolocation


# ---------------------------------------------------------------------------
# Главный клиент
# ---------------------------------------------------------------------------
def _pick_https_proxy() -> str | None:
    """Возвращает прокси из HTTPS_PROXY/https_proxy (если заданы)."""
    return os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

@dataclass
class PyaterochkaAPI:
    """Клиент Перекрёстка.
    """

    timeout: float          = 40.0
    browser: Literal["chromium", "webkit", "firefox", "camoufox"] = "camoufox"
    headless: bool          = False
    proxy: str | None       = field(default_factory=_pick_https_proxy)
    browser_opts: dict[str, Any] = field(default_factory=dict)

    MAIN_SITE_URL: str      = "https://5ka.ru"
    MAIN_SITE_API: str      = "https://api.5ka.ru"
    CATALOG_URL: str        = "https://5d.5ka.ru/api"

    # будет создана в __post_init__
    session: human_requests.Session = field(init=False, repr=False)

    # ───── lifecycle ─────
    def __post_init__(self) -> None:
        self.session = human_requests.Session(
            browser=self.browser,
            playwright_stealth=self.browser in ("chromium", "webkit", "firefox"),
            proxy=self.proxy,
            headless=self.headless,
            browser_launch_opts=self.browser_opts,
            spoof=ImpersonationConfig(
                policy=Policy.SYNC_WITH_BROWSER
            )
        )

        self.Geolocation: ClassGeolocation = ClassGeolocation(self, self.CATALOG_URL)
        """Методы для работы с геолокацией и выбором магазинов."""
        self.Catalog: ClassCatalog         = ClassCatalog(self, self.CATALOG_URL)
        """Методы для работы с каталогом товаров."""
        self.Advertising: ClassAdvertising = ClassAdvertising(self, self.CATALOG_URL, self.MAIN_SITE_API)
        """Методы для работы с рекламными материалами."""
        self.General: ClassGeneral         = ClassGeneral(self, self.CATALOG_URL)
        """Общие методы API."""

    async def __aenter__(self):
        """Вход в контекстный менеджер с автоматическим прогревом сессии."""
        await self._warmup()
        return self

    async def __aexit__(self, *exc):
        """Выход из контекстного менеджера с закрытием сессии."""
        await self.close()

    async def close(self):
        """Закрыть HTTP-сессию и освободить ресурсы."""
        await self.session.close()

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    async def _warmup(self) -> None:
        """Прогрев сессии через браузер для получения токена доступа.
        
        Открывает главную страницу сайта в headless браузере, получает cookie сессии
        и извлекает из неё access token для последующих API запросов.
        """
        await self.session.start()
        async with self.session.goto_page(self.MAIN_SITE_URL, wait_until="networkidle") as page:
            await page.wait_for_selector(
                selector="next-route-announcer",
                state="attached",
                timeout=self.timeout*1000
            )

    @property
    def default_store_location(self) -> str | None:
        return self.session.local_storage.get("https://5ka.ru", {}).get("DeliveryPanelStore")

    @property
    def default_sap_code(self) -> str | None:
        dsl = self.default_store_location
        if dsl:
            json_dsl = json.loads(dsl)
            return json_dsl['selectedAddress']['sapCode']
        return None
        
    @property
    def device_id(self) -> str | None:
        return self.session.local_storage.get("https://5ka.ru", {}).get("deviceId")

    def make_headers(self) -> dict[str, str]:
        headers = {
            "Origin": self.MAIN_SITE_URL,
            "X-PLATFORM": "webapp",
        }
        device_id = self.device_id
        if device_id:
            headers["X-DEVICE-ID"] = device_id
        headers.update({"X-APP-VERSION": "0.1.1.dev"})
        return headers

    async def _request(
        self,
        method: str,
        url: str,
        *,
        json_body: Any | None = None,
    ) -> human_requests.abstraction.response.Response:
        """Выполнить HTTP-запрос через внутреннюю сессию.
        
        Единая точка входа для всех HTTP-запросов библиотеки.
        Добавляет к ответу объект Request для совместимости.
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            json_body: Тело запроса в формате JSON (опционально)
        """
        # Единая точка входа в чужую библиотеку для удобства
        resp = await self.session.request(
            method=method.upper(),
            url=url,
            json=json_body,
            headers=self.make_headers(),
        )
        
        return resp

