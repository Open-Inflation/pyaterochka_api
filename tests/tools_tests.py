import pytest
from pyaterochka_api.tools import parse_proxy
import itertools
import logging

@pytest.mark.asyncio
async def test_parse_proxy():
    # Варианты параметров
    schemes = ['http://', 'https://', '']
    auths = [('', ''), ('user', 'pass')]
    hosts = ['127.0.0.1', 'example.com']
    ports = ['', '8080']

    logger = logging.getLogger("test_parse_proxy")

    for scheme, (username, password), host, port in itertools.product(schemes, auths, hosts, ports):
        # Формируем строку прокси
        auth_part = f"{username}:{password}@" if username else ""
        port_part = f":{port}" if port else ""
        proxy_str = f"{scheme}{auth_part}{host}{port_part}"

        expected = {'server': f"{scheme}{host}{port_part}"}
        if not scheme:
            expected['server'] = "http://"+expected['server']
        if username:
            expected['username'] = username
            expected['password'] = password

        assert parse_proxy(proxy_str, True, logger) == expected

