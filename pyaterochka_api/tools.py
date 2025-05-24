from .enums import Patterns
import os
import re
from beartype import beartype
import logging

@beartype
def get_env_proxy() -> str | None:
    """
    Получает прокси из переменных окружения.
    :return: Прокси-строка или None.
    """
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    return proxy if proxy else None

@beartype
def parse_proxy(proxy_str: str | None, trust_env: bool, logger: logging.Logger) -> dict | None:
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
