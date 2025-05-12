from .enums import Patterns
import os
import re
from tqdm import tqdm

def get_env_proxy() -> str | None:
    """
    Получает прокси из переменных окружения.
    :return: Прокси-строка или None.
    """
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    return proxy if proxy else None

def parse_proxy(proxy_str: str | None, trust_env: bool, logger) -> dict | None:
    logger.debug(f"Parsing proxy string: {proxy_str}")

    if not proxy_str:
        if trust_env:
            logger.debug("Proxy string not provided, checking environment variables for HTTP(S)_PROXY")
            proxy_str = get_env_proxy()
        
        if not proxy_str:
            logger.info("No proxy string found, returning None")
            return None
        else:
            logger.info(f"Proxy string found in environment variables")

    # Example: user:pass@host:port or just host:port
    match = re.match(Patterns.PROXY.value, proxy_str)
    
    proxy_dict = {}
    if not match:
        logger.warning(f"Proxy string did not match expected pattern, using basic formating")
        proxy_dict['server'] = proxy_str
        
        if not proxy_str.startswith('http://') and not proxy_str.startswith('https://'):
            logger.warning("Proxy string missing protocol, prepending 'http://'")
            proxy_dict['server'] = f"http://{proxy_str}"
        
        logger.info(f"Proxy parsed as basic")
        return proxy_dict
    else:
        match_dict = match.groupdict()
        proxy_dict['server'] = f"{match_dict['scheme'] or 'http://'}{match_dict['host']}"
        if match_dict['port']:
            proxy_dict['server'] += f":{match_dict['port']}"
        
        for key in ['username', 'password']:
            if match_dict[key]:
                proxy_dict[key] = match_dict[key]
        
        logger.info(f"Proxy WITH{'OUT' if 'username' not in proxy_dict else ''} credentials")
        
        logger.info(f"Proxy parsed as regex")
        return proxy_dict

async def _parse_match(match: str, progress_bar: tqdm | None = None) -> dict:
    result = {}

    if progress_bar:
        progress_bar.set_description("Parsing strings")

    # Парсинг строк
    string_matches = re.finditer(Patterns.STR.value, match)
    for m in string_matches:
        key, value = m.group(1), m.group(2)
        result[key] = value.replace('\"', '"').replace('\\', '\\')

    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description("Parsing dictionaries")

    # Парсинг словарей
    dict_matches = re.finditer(Patterns.DICT.value, match)
    for m in dict_matches:
        key, value = m.group(1), m.group(2)
        if not re.search(Patterns.STR.value, value):
            result[key] = await _parse_match(value, progress_bar)

    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description("Parsing lists")

    # Парсинг списков
    list_matches = re.finditer(Patterns.LIST.value, match)
    for m in list_matches:
        key, value = m.group(1), m.group(2)
        if not re.search(Patterns.STR.value, value):
            result[key] = [await _parse_match(item.group(0), progress_bar) for item in re.finditer(Patterns.FIND.value, value)]

    if progress_bar:
        progress_bar.update(1)

    return result

async def parse_js(js_code: str, debug: bool, logger) -> dict | None:
    """
    Парсит JavaScript-код и извлекает данные из переменной "n".

    :param js_code: JS-код в виде строки.
    :return: Распарсенные данные в виде словаря или None.
    """
    matches = re.finditer(Patterns.JS.value, js_code)
    match_list = list(matches)

    logger.debug(f'Found matches {len(match_list)}')
    
    progress_bar = tqdm(total=33, desc="Parsing JS", position=0) if debug else None

    if match_list and len(match_list) >= 1:
        logger.info('Starting to parse match')
        result = await _parse_match(match_list[1].group(0), progress_bar)
        
        if progress_bar:
            progress_bar.close()
        logger.info('Complited parsing match')
        return result
    else:
        if progress_bar:
            progress_bar.close()
        raise Exception("N variable in JS code not found")
