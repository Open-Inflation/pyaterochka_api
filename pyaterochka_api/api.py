import aiohttp
from fake_useragent import UserAgent
from camoufox import AsyncCamoufox
import logging
from .tools import parse_proxy, parse_js, get_env_proxy


class PyaterochkaAPI:
    """
    Класс для загрузки JSON/image и парсинга JavaScript-конфигураций из удаленного источника.
    """

    def __init__(self,
                 debug:             bool       = False,
                 proxy:             str | None = None,
                 autoclose_browser: bool       = False,
                 trust_env:         bool       = False,
                 timeout:           float      = 10.0
        ):
        self._debug = debug
        self._proxy = proxy
        self._session = None
        self._autoclose_browser = autoclose_browser
        self._browser = None
        self._bcontext = None
        self._trust_env = trust_env
        self._timeout = timeout

        self._logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        if not self._logger.hasHandlers():
            self._logger.addHandler(handler)

    async def fetch(self, url: str) -> tuple[bool, dict | None | str, str]:
        """
        Выполняет HTTP-запрос к указанному URL и возвращает результат.

        :return: Кортеж (успех, данные или None, тип данных или пустота).
        """
        args = {'url': url, 'timeout': aiohttp.ClientTimeout(total=self._timeout)}
        if self._proxy: args["proxy"] = self._proxy

        self._logger.info(f'Requesting "{url}" with proxy: "{args.get("proxy") or ("SYSTEM_PROXY" if get_env_proxy() else "WITHOUT")}", timeout: {self._timeout}...')
        
        async with self._session.get(**args) as response:
            self._logger.info(f'Response status: {response.status}')

            if response.status == 200:
                if response.headers['content-type'] == 'application/json':
                    output_response = response.json()
                elif response.headers['content-type'] == 'image/jpeg':
                    output_response = response.read()
                else:
                    output_response = response.text()

                return True, await output_response, response.headers['content-type']
            elif response.status == 403:
                self._logger.warning('Anti-bot protection. Use Russia IP address and try again.')
                return False, None, ''
            else:
                self._logger.error(f'Unexpected error: {response.status}')
                raise Exception(f"Response status: {response.status} (unknown error/status code)")

    async def download_config(self, config_url: str) -> dict | None:
        """
        Загружает и парсит JavaScript-конфигурацию с указанного URL.

        :param config_url: URL для загрузки конфигурации.
        :return: Распарсенные данные в виде словаря или None.
        """
        is_success, js_code, _response_type = await self.fetch(url=config_url)

        if not is_success:
            if self._debug:
                self._logger.error('Failed to fetch JS code')
            return None
        elif self._debug:
            self._logger.debug('JS code fetched successfully')

        return await parse_js(js_code=js_code, debug=self._debug, logger=self._logger)


    async def browser_fetch(self, url: str, selector: str, state: str = 'attached') -> dict:
        if self._browser is None or self._bcontext is None:
            await self.new_session(include_aiohttp=False, include_browser=True)

        page = await self._bcontext.new_page()
        await page.goto(url, wait_until='commit', timeout=self._timeout * 1000)
        # Wait until the selector script tag appears
        await page.wait_for_selector(selector=selector, state=state, timeout=self._timeout * 1000)
        content = await page.content()
        await page.close()

        if self._autoclose_browser:
            await self.close(include_aiohttp=False, include_browser=True)
        return content

    async def new_session(self, include_aiohttp: bool = True, include_browser: bool = False) -> None:
        await self.close(include_aiohttp=include_aiohttp, include_browser=include_browser)

        if include_aiohttp:
            args = {
                "headers": {
                    "User-Agent": UserAgent().random,
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "en-GB,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "X-PLATFORM": "webapp",
                    "Origin": "https://5ka.ru",
                    "Connection": "keep-alive",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache",
                    "TE": "trailers",
                },
                "trust_env": self._trust_env,
            }
            self._session = aiohttp.ClientSession(**args)
            self._logger.info(f"A new aiohttp connection has been opened. trust_env: {args.get('trust_env')}")

        if include_browser:
            prox = parse_proxy(self._proxy, self._trust_env, self._logger)
            self._logger.info(f"Opening new browser connection with proxy: {'SYSTEM_PROXY' if prox and not self._proxy else prox}")
            self._browser = await AsyncCamoufox(headless=not self._debug, proxy=prox, geoip=True).__aenter__()
            self._bcontext = await self._browser.new_context()
            self._logger.info(f"A new browser context has been opened.")

    async def close(
        self,
        include_aiohttp: bool = True,
        include_browser: bool = False
    ) -> None:
        """
        Close the aiohttp session and/or Camoufox browser if they are open.
        :param include_aiohttp: close aiohttp session if True
        :param include_browser: close browser if True
        """
        to_close = []
        if include_aiohttp:
            to_close.append("session")
        if include_browser:
            to_close.append("bcontext")
            to_close.append("browser")

        self._logger.info(f"Preparing to close: {to_close if to_close else 'nothing'}")

        if not to_close:
            self._logger.warning("No connections to close")
            return

        checks = {
            "session": lambda a: a is not None and not a.closed,
            "browser": lambda a: a is not None,
            "bcontext": lambda a: a is not None
        }

        for name in to_close:
            attr = getattr(self, f"_{name}", None)
            if checks[name](attr):
                self._logger.info(f"Closing {name} connection...")
                try:
                    if name == "browser":
                        await attr.__aexit__(None, None, None)
                    elif name in ["bcontext", "session"]:
                        await attr.close()
                    else:
                        raise ValueError(f"Unknown connection type: {name}")
                    
                    setattr(self, f"_{name}", None)
                    self._logger.info(f"The {name} connection was closed")
                except Exception as e:
                    self._logger.error(f"Error closing {name}: {e}")
            else:
                self._logger.warning(f"The {name} connection was not open")


