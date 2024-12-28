import aiohttp
from fake_useragent import UserAgent
from enum import Enum
import re
from tqdm.asyncio import tqdm


class Patterns(Enum):
    JS = r'\s*let\s+n\s*=\s*({.*});\s*'
    STR = r'(\w+)\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"'
    DICT = r'(\w+)\s*:\s*{(.*?)}'
    LIST = r'(\w+)\s*:\s*\[([^\[\]]*(?:\[.*?\])*)\]'
    FIND = r'\{.*?\}|\[.*?\]'



async def main_fetch(url: str, debug: bool = False, is_json: bool = True) -> tuple[bool, dict | None]:
    async with aiohttp.ClientSession() as session:
        if debug:
            print(f"Requesting \"{url}\"...", flush=True)

        async with session.get(
                url=url,
                headers={"User-Agent": UserAgent().random},
        ) as response:
            if debug:
                print(f"Response status: {response.status}", flush=True)

            if response.status == 200: # 200 OK
                if debug:
                    print("Correct response", flush=True)
                return True, await response.json() if is_json else await response.text()
            elif response.status == 403: # 403 Forbidden (сервер воспринял как бота)
                if debug:
                    print("Anti-bot protection. Use Russia IP address and try again.", flush=True)
                return False, None
            else:
                if debug:
                    print(f"Please, create issue on GitHub", flush=True)
                raise Exception(f"Response status: {response.status} (unknown error/status code)")

async def download_hardcode_config(config_url: str, debug: bool = False) -> dict | None:
    is_success, js_code = await main_fetch(url=config_url, debug=debug, is_json=False)

    if not is_success:
        if debug:
            print("Failed to fetch JS code")
        return None
    elif debug:
        print("JS code fetched successfully")

    # Регулярное выражение для извлечения определения переменной n
    matches = re.finditer(Patterns.JS.value, js_code)

    match_list = list(matches)
    if debug:
        print(f"Found matches {len(match_list)}")

    if debug:
        progress_bar = tqdm(total=33, desc="Parsing JS", position=0) # примерно 33 операции

    async def parse_match(match: str) -> dict:
        result = {}

        if debug:
            # Обновление описания прогресса
            progress_bar.set_description("Parsing strings")

        # Парсинг строк
        string_matches = re.finditer(Patterns.STR.value, match)
        for m in string_matches:
            key, value = m.group(1), m.group(2)
            result[key] = value.replace('\"', '"').replace('\\\\', '\\')

        if debug:
            progress_bar.update(1)
            # Обновление описания прогресса
            progress_bar.set_description("Parsing dictionaries")

        # Парсинг словарей
        dict_matches = re.finditer(Patterns.DICT.value, match)
        for m in dict_matches:
            key, value = m.group(1), m.group(2)
            if not re.search(Patterns.STR.value, value):
                result[key] = await parse_match(value)

        if debug:
            progress_bar.update(1)
            # Обновление описания прогресса
            progress_bar.set_description("Parsing lists")

        # Парсинг списков
        list_matches = re.finditer(Patterns.LIST.value, match)
        for m in list_matches:
            key, value = m.group(1), m.group(2)
            if not re.search(Patterns.STR.value, value):
                result[key] = [await parse_match(item.group(0)) for item in re.finditer(Patterns.FIND.value, value)]

        if debug:
            # Обновление прогресса
            progress_bar.update(1)

        return result

    if match_list and len(match_list) >= 1:  # нужная переменная идет второй из трех
        if debug:
            print("Starting to parse match")
        result = await parse_match(match_list[1].group(0))
        if debug:
            progress_bar.close()
        return result
    else:
        if debug:
            progress_bar.close()
        raise Exception("N variable in JS code not found")

