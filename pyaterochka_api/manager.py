import os
from dataclasses import dataclass, field
from typing import Any
import hrequests
from requests import Request
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

    timeout: float          = 15.0
    browser: str            = "firefox"
    headless: bool          = True
    proxy: str | None       = field(default_factory=_pick_https_proxy)
    browser_opts: dict[str, Any] = field(default_factory=dict)

    MAIN_SITE_URL: str      = "https://5ka.ru"
    CATALOG_URL: str        = "https://5d.5ka.ru/api"
    DEFAULT_STORE_ID: str   = "Y232"

    # будет создана в __post_init__
    session: hrequests.Session = field(init=False, repr=False)

    # ───── lifecycle ─────
    def __post_init__(self) -> None:
        self.session = hrequests.Session(
            self.browser,
            timeout=self.timeout,
        )

        self.Geolocation: ClassGeolocation = ClassGeolocation(self, self.CATALOG_URL)
        """Методы для работы с геолокацией и выбором магазинов."""
        self.Catalog: ClassCatalog         = ClassCatalog(self, self.CATALOG_URL, self.DEFAULT_STORE_ID)
        """Методы для работы с каталогом товаров."""
        self.Advertising: ClassAdvertising = ClassAdvertising(self, self.CATALOG_URL)
        """Методы для работы с рекламными материалами."""
        self.General: ClassGeneral         = ClassGeneral(self, self.CATALOG_URL)
        """Общие методы API."""

    def __enter__(self):
        """Вход в контекстный менеджер с автоматическим прогревом сессии."""
        self._warmup()
        return self

    def __exit__(self, *exc):
        """Выход из контекстного менеджера с закрытием сессии."""
        self.close()

    def close(self):
        """Закрыть HTTP-сессию и освободить ресурсы."""
        self.session.close()

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    def _warmup(self) -> None:
        """Прогрев сессии через браузер для получения токена доступа.
        
        Открывает главную страницу сайта в headless браузере, получает cookie сессии
        и извлекает из неё access token для последующих API запросов.
        """
        with hrequests.BrowserSession(
            session=self.session,
            browser=self.browser,
            headless=self.headless,
            proxy=self.proxy,
            **self.browser_opts,
        ) as page:
            page.goto(self.MAIN_SITE_URL)
            page.awaitSelector("next-route-announcer", timeout=self.timeout)
            print(page.cookies)
            import time
            time.sleep(50)

    def _request(
        self,
        method: str,
        url: str,
        *,
        json_body: Any | None = None,
    ) -> hrequests.Response:
        """Выполнить HTTP-запрос через внутреннюю сессию.
        
        Единая точка входа для всех HTTP-запросов библиотеки.
        Добавляет к ответу объект Request для совместимости.
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            json_body: Тело запроса в формате JSON (опционально)
        """
        # Единая точка входа в чужую библиотеку для удобства
        resp = self.session.request(method.upper(), url, json=json_body, timeout=self.timeout, proxy=self.proxy)
        if hasattr(resp, "request"):
            raise RuntimeError(
                "Response object does have `request` attribute. "
                "This may indicate an update in `hrequests` library."
            )
        
        resp.request = Request(
            method=method.upper(),
            url=url,
            json=json_body,
        )
        return resp

