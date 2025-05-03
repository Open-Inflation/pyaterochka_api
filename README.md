# Pyaterochka API *(not official / не официальный)*

Pyaterochka (Пятёрочка) - https://5ka.ru/

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyaterochka_api)
![PyPI - Package Version](https://img.shields.io/pypi/v/pyaterochka_api?color=blue)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyaterochka_api?label=PyPi%20downloads)](https://pypi.org/project/pyaterochka-api/)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)



## Installation / Установка:
Install package / Установка пакета:
```bash
pip install pyaterochka_api
```

### Usage / Использование:
```py
from pyaterochka_api import Pyaterochka
import asyncio


async def main():
    async with Pyaterochka(proxy="user:password@host:port", debug=False) as API:
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

        # RUS: Так же как и debug, в рантайме можно переназначить прокси
        # ENG: As with debug, you can reassign the proxy in runtime
        API.proxy = "user:password@host:port"
        # RUS: Чтобы применить изменения, нужно пересоздать подключение
        # ENG: To apply changes, you need rebuild connection
        await API.rebuild_connection()
        await API.categories_list()


if __name__ == '__main__':
    asyncio.run(main())
```

### Report / Обратная связь

If you have any problems using it /suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/pyaterochka_api/issues)!

Если у вас возникнут проблемы в использовании / пожелания, не стесняйтесь писать на [GitHub проекта](https://github.com/Open-Inflation/pyaterochka_api/issues)!
