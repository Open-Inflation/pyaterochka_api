# Pyaterochka API *(not official / не официальный)*

Pyaterochka (Пятёрочка) - https://5ka.ru/

[![GitHub Actions](https://github.com/Open-Inflation/pyaterochka_api/workflows/API%20Tests%20Daily/badge.svg)](https://github.com/Open-Inflation/pyaterochka_api/actions?query=workflow%3A"API+Tests+Daily?query=branch%3Amain")
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyaterochka_api)
![PyPI - Package Version](https://img.shields.io/pypi/v/pyaterochka_api?color=blue)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyaterochka_api?label=PyPi%20downloads)](https://pypi.org/project/pyaterochka-api/)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)



## Installation / Установка:
1. Install package / Установка пакета:
```bash
pip install pyaterochka_api
```
2. ***Debian/Ubuntu Linux***: Install dependencies / Установка зависимостей:
```bash
sudo apt update && sudo apt install -y libgtk-3-0 libx11-xcb1
```
3. Install browser / Установка браузера:
```bash
camoufox fetch
```

### Usage / Использование:
```py
from pyaterochka_api import Pyaterochka
import asyncio


async def main():
    async with Pyaterochka(proxy="user:password@host:port", debug=False, autoclose_browser=False, trust_env=False) as API:
        # RUS: Вводим геоточку (самого магазина или рядом с ним) и получаем инфу о магазине
        # ENG: Enter a geolocation (of the store or near it) and get info about the store
        find_store = await API.find_store(longitude=37.63156, latitude=55.73768)
        print(f"Store info output: {find_store!s:.100s}...\n")

        # RUS: Выводит список всех категорий на сайте
        # ENG: Outputs a list of all categories on the site
        catalog = await API.categories_list(subcategories=True, mode=API.PurchaseMode.DELIVERY)
        print(f"Categories list output: {catalog!s:.100s}...\n")

        # RUS: Выводит список всех товаров выбранной категории (ограничение 100 элементов, если превышает - запрашивайте через дополнительные страницы)
        # ENG: Outputs a list of all items in the selected category (limiting to 100 elements, if exceeds - request through additional pages)
        # Страниц не сущетвует, использовать желаемый лимит (до 499) / Pages do not exist, use the desired limit (up to 499)
        items = await API.products_list(catalog[0]['id'], limit=5)
        print(f"Items list output: {items!s:.100s}...\n")

        # RUS: Выводит информацию о товаре (по его plu - id товара).
        # Функция в первый раз достаточно долгая, порядка 5-9 секунды, последующие запросы около 2 секунд (если браузер не был закрыт)
        # ENG: Outputs information about the product (by its plu - product id).
        # The function is quite long the first time, about 5-9 seconds, subsequent requests take about 2 seconds (if the browser was not closed)
        info = await API.product_info(43347)
        print(f"Product output: {info["props"]["pageProps"]["props"]['productStore']!s:.100s}...\n")

        # RUS: Влияет исключительно на функцию выше (product_info), если включено, то после отработки запроса браузер закроется и кеши очищаются.
        # Не рекомендую включать, если вам все же нужно освободить память, лучше использовать API.close(session=False, browser=True)
        # ENG: Affects only the function above (product_info), if enabled, the browser will close after the request is processed and caches are cleared.
        # I do not recommend enabling it, if you still need to free up memory, it is better to use API.close(session=False, browser=True)
        API.autoclose_browser = True

        # RUS: Напрямую передается в aiohttp, так же учитывается в браузере. В первую очередь нужен для использования системного `HTTPS_PROXY`.
        # Но системный прокси применяется, только если не указали иное напрямую в `API.proxy`.
        # ENG: Directly passed to aiohttp, also taken into account in the browser. Primarily needed for using the system `HTTPS_PROXY`.
        # But the system proxy is applied only if you did not specify otherwise directly in `API.proxy`.
        API.trust_env = True

        # RUS: Выводит список последних промо-акций/новостей (можно поставить ограничитель по количеству, опционально)
        # ENG: Outputs a list of the latest promotions/news (you can set a limit on the number, optionally)
        news = await API.get_news(limit=5)
        print(f"News output: {news!s:.100s}...\n")

        # RUS: Выводит основной конфиг сайта (очень долгая функция, рекомендую сохранять в файл и переиспользовать)
        # ENG: Outputs the main config of the site (large function, recommend to save in a file and re-use it)
        print(f"Main config: {await API.get_config()!s:.100s}...\n")

        # RUS: Если требуется, можно настроить вывод логов в консоль
        # ENG: If required, you can configure the output of logs in the console
        API.debug = True

        # RUS: Скачивает картинку товара (возвращает BytesIO или None)
        # ENG: Downloads the product image (returns BytesIO or None)
        image = await API.download_image(url=items['products'][0]['image_links']['normal'][0])
        with open(image.name, 'wb') as f:
            f.write(image.getbuffer())

        # RUS: Можно указать свой таймаут (браузер может его интерпретировать как x2 т.к. там 2 итерации скачивания)
        # ENG: You can specify your own timeout (the browser may interpret it as x2 since there are 2 iterations of downloading)
        API.timeout = 7

        # RUS: Так же как и debug, в рантайме можно переназначить прокси
        # ENG: As with debug, you can reassign the proxy in runtime
        API.proxy = "user:password@host:port"
        # RUS: Изменения происходят сразу же, кроме product_info, т.к. за него отвечает браузер
        # ENG: Changes take effect immediately, except for product_info, as it is handled by the browser
        await API.rebuild_connection(session=False, browser=True)
        await API.product_info(43347)


if __name__ == '__main__':
    asyncio.run(main())
```

### Report / Обратная связь

If you have any problems using it /suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/pyaterochka_api/issues)!

Если у вас возникнут проблемы в использовании / пожелания, не стесняйтесь писать на [GitHub проекта](https://github.com/Open-Inflation/pyaterochka_api/issues)!
