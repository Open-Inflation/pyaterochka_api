import aiohttp
from fake_useragent import UserAgent
from enum import Enum
import re
from tqdm.asyncio import tqdm
from camoufox import AsyncCamoufox


class PyaterochkaAPI:
    """
    Класс для загрузки JSON/image и парсинга JavaScript-конфигураций из удаленного источника.
    """

    class Patterns(Enum):
        JS = r'\s*let\s+n\s*=\s*({.*});\s*'              # let n = {...};
        STR = r'(\w+)\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"'  # key: "value"
        DICT = r'(\w+)\s*:\s*{(.*?)}'                    # key: {...}
        LIST = r'(\w+)\s*:\s*\[([^\[\]]*(?:\[.*?\])*)\]' # key: [value]
        FIND = r'\{.*?\}|\[.*?\]'                        # {} or []

    def __init__(self, debug: bool = False, proxy: str = None, autoclose_browser: bool = False):
        self._debug = debug
        self._proxy = proxy
        self._session = None
        self._autoclose_browser = autoclose_browser
        self._browser = None
        self._bcontext = None

    @property
    def proxy(self) -> str | None:
        return self._proxy if hasattr(self, '_proxy') else None

    @proxy.setter
    def proxy(self, value: str | None) -> None:
        self._proxy = value
    
    async def fetch(self, url: str) -> tuple[bool, dict | None | str, str]:
        """
        Выполняет HTTP-запрос к указанному URL и возвращает результат.

        :return: Кортеж (успех, данные или None).
        """
        if self._debug:
            print(f"Requesting \"{url}\"...", flush=True)

        async with self._session.get(url=url) as response:
            if self._debug:
                print(f"Response status: {response.status}", flush=True)

            if response.status == 200:
                if response.headers['content-type'] == 'application/json':
                    output_response = response.json()
                elif response.headers['content-type'] == 'image/jpeg':
                    output_response = response.read()
                else:
                    output_response = response.text()

                return True, await output_response, response.headers['content-type']
            elif response.status == 403:
                if self._debug:
                    print("Anti-bot protection. Use Russia IP address and try again.", flush=True)
                return False, None, ''
            else:
                if self._debug:
                    print(f"Unexpected error: {response.status}", flush=True)
                raise Exception(f"Response status: {response.status} (unknown error/status code)")

    async def _parse_js(self, js_code: str) -> dict | None:
        """
        Парсит JavaScript-код и извлекает данные из переменной "n".

        :param js_code: JS-код в виде строки.
        :return: Распарсенные данные в виде словаря или None.
        """
        matches = re.finditer(self.Patterns.JS.value, js_code)
        match_list = list(matches)

        if self._debug:
            print(f"Found matches {len(match_list)}")
            progress_bar = tqdm(total=33, desc="Parsing JS", position=0)

        async def parse_match(match: str) -> dict:
            result = {}

            if self._debug:
                progress_bar.set_description("Parsing strings")

            # Парсинг строк
            string_matches = re.finditer(self.Patterns.STR.value, match)
            for m in string_matches:
                key, value = m.group(1), m.group(2)
                result[key] = value.replace('\"', '"').replace('\\', '\\')

            if self._debug:
                progress_bar.update(1)
                progress_bar.set_description("Parsing dictionaries")

            # Парсинг словарей
            dict_matches = re.finditer(self.Patterns.DICT.value, match)
            for m in dict_matches:
                key, value = m.group(1), m.group(2)
                if not re.search(self.Patterns.STR.value, value):
                    result[key] = await parse_match(value)

            if self._debug:
                progress_bar.update(1)
                progress_bar.set_description("Parsing lists")

            # Парсинг списков
            list_matches = re.finditer(self.Patterns.LIST.value, match)
            for m in list_matches:
                key, value = m.group(1), m.group(2)
                if not re.search(self.Patterns.STR.value, value):
                    result[key] = [await parse_match(item.group(0)) for item in re.finditer(self.Patterns.FIND.value, value)]

            if self._debug:
                progress_bar.update(1)

            return result

        if match_list and len(match_list) >= 1:
            if self._debug:
                print("Starting to parse match")
            result = await parse_match(match_list[1].group(0))
            if self._debug:
                progress_bar.close()
            return result
        else:
            if self._debug:
                progress_bar.close()
            raise Exception("N variable in JS code not found")

    async def download_config(self, config_url: str) -> dict | None:
        """
        Загружает и парсит JavaScript-конфигурацию с указанного URL.

        :param config_url: URL для загрузки конфигурации.
        :return: Распарсенные данные в виде словаря или None.
        """
        is_success, js_code, _response_type = await self.fetch(url=config_url)

        if not is_success:
            if self._debug:
                print("Failed to fetch JS code")
            return None
        elif self._debug:
            print("JS code fetched successfully")

        return await self._parse_js(js_code=js_code)


    async def _browser_fetch(self, url: str, selector: str, state: str = 'attached') -> dict:
        if self._browser is None or self._bcontext is None:
            await self._new_session(include_aiohttp=False, include_browser=True)

        page = await self._bcontext.new_page()
        await page.goto(url, wait_until='commit')
        # Wait until the selector script tag appears
        await page.wait_for_selector(selector=selector, state=state)
        content = await page.content()
        await page.close()

        if self._autoclose_browser:
            await self.close(include_aiohttp=False, include_browser=True)
        return content

    def _parse_proxy(self, proxy_str: str | None) -> dict | None:
        if not proxy_str:
            return None

        # Example: user:pass@host:port or just host:port
        match = re.match(
            r'^(?:(?P<scheme>https?:\/\/))?(?:(?P<username>[^:@]+):(?P<password>[^@]+)@)?(?P<host>[^:]+):(?P<port>\d+)$',
            proxy_str,
        )

        proxy_dict = {}
        if not match:
            proxy_dict['server'] = proxy_str
            
            if not proxy_str.startswith('http://') and not proxy_str.startswith('https://'):
                proxy_dict['server'] = f"http://{proxy_str}"
            
            return proxy_dict
        else:
            match_dict = match.groupdict()
            proxy_dict['server'] = f"{match_dict['scheme'] or 'http://'}{match_dict['host']}:{match_dict['port']}"
            
            for key in ['username', 'password']:
                if match_dict[key]:
                    proxy_dict[key] = match_dict[key]
            
            return proxy_dict

    async def _new_session(self, include_aiohttp: bool = True, include_browser: bool = False) -> None:
        await self.close(include_aiohttp=include_aiohttp, include_browser=include_browser)

        if include_aiohttp:
            args = {"headers": {"User-Agent": UserAgent().random}}
            if self._proxy: args["proxy"] = self._proxy
            self._session = aiohttp.ClientSession(**args)
        
            if self._debug: print(f"A new connection aiohttp has been opened. Proxy used: {args.get('proxy')}")

        if include_browser:
            self._browser = await AsyncCamoufox(headless=not self._debug, proxy=self._parse_proxy(self.proxy), geoip=True).__aenter__()
            self._bcontext = await self._browser.new_context()
            
            if self._debug: print(f"A new connection browser has been opened. Proxy used: {self.proxy}")

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

        if not to_close:
            raise ValueError("No connections to close")

        checks = {
            "session": lambda a: a is not None and not a.closed,
            "browser": lambda a: a is not None,
            "bcontext": lambda a: a is not None
        }

        for name in to_close:
            attr = getattr(self, f"_{name}", None)
            if checks[name](attr):
                if "browser" in name:
                    await attr.__aexit__(None, None, None)
                else:
                    await attr.close()
                setattr(self, f"_{name}", None)
                if self._debug:
                    print(f"The {name} connection was closed")
            else:
                if self._debug:
                    print(f"The {name} connection was not open")


