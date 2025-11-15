<div align="center">

# Pyaterochka API *(not official)*

![Tests last run (ISO)](https://img.shields.io/badge/dynamic/json?label=Tests%20last%20run&query=%24.workflow_runs%5B0%5D.updated_at&url=https%3A%2F%2Fapi.github.com%2Frepos%2FOpen-Inflation%2Fpyaterochka_api%2Factions%2Fworkflows%2Ftests.yml%2Fruns%3Fper_page%3D1%26status%3Dcompleted&logo=githubactions&cacheSeconds=300)
[![Tests](https://github.com/Open-Inflation/pyaterochka_api/actions/workflows/tests.yml/badge.svg)](https://github.com/Open-Inflation/pyaterochka_api/actions/workflows/tests.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyaterochka_api)
![PyPI - Package Version](https://img.shields.io/pypi/v/pyaterochka_api?color=blue)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyaterochka_api?label=PyPi%20downloads)](https://pypi.org/project/pyaterochka-api/)
[![License](https://img.shields.io/github/license/Open-Inflation/pyaterochka_api)](https://github.com/Open-Inflation/pyaterochka_api/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)


Pyaterochka (Пятёрочка) - https://5ka.ru/

**[⭐ Star us on GitHub](https://github.com/Open-Inflation/pyaterochka_api)** | **[📚 Read the Docs](https://open-inflation.github.io/pyaterochka_api/quick_start)** | **[🐛 Report Bug](https://github.com/Open-Inflation/pyaterochka_api/issues)**

### Принцип работы

</div>

> Библиотека полностью повторяет сетевую работу обычного пользователя на сайте.

<div align="center">

## Usage:

</div>

```bash
pip install pyaterochka_api
python -m camoufox fetch
```

```py
from pyaterochka_api import PyaterochkaAPI
import asyncio
from PIL import Image

async def main():
    async with PyaterochkaAPI() as api:
        
        # 1. Получение информации о текущем выбранном магазине доставки
        store_info = await api.delivery_panel_store()
        sap_code = store_info["selectedStore"]["sapCode"]
        print(f"SAP код выбранного магазина: {sap_code}\n")

        # 2. Получение списка всех категорий
        tree_resp = await api.Catalog.tree(sap_code_store_id=sap_code)
        categories_data = tree_resp.json()
        first_category = categories_data[0]
        print(f"Первая категория: {first_category['name']!s:.50s}...\n")

        # 3. Получение списка товаров в первой категории
        products_resp = await api.Catalog.products_list(
            category_id=first_category["id"], sap_code_store_id=sap_code
        )
        products_data = products_resp.json()
        first_product_plu = products_data["products"][0]["plu"]
        print(f"Первый товар (PLU): {first_product_plu}\n")

        # 4. Получение подробной информации о первом товаре
        product_info_resp = await api.Catalog.Product.info(
            sap_code_store_id=sap_code, plu_id=first_product_plu
        )
        product_info_data = product_info_resp.json()
        print(f"Название первого товара: {product_info_data['name']!s:.50s}...\n")

        # 5. Примеры использования геолокации
        
        # Поиск адресов по запросу
        suggest_resp = await api.Geolocation.suggest("москва")
        print(f"Предложения по геолокации для 'москва': {suggest_resp.json()['results'][0]['address']['formatted_address']!s:.50s}...\n")

        # Определение текущей геолокации
        geocode_resp = await api.Geolocation.geocode()
        pos: str = geocode_resp.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        longitude, latitude = pos.split(" ")
        print(f"Выбранная геолокация (долгота, широта): {longitude}, {latitude}\n")
        
        # 6. Скачивание изображения (на примере изображения первой подкатегории)
        image_link = first_category["categories"][0]["image_link"]
        image_stream = await api.General.download_image(image_link)

        # Пример обработки изображения с помощью PIL
        with Image.open(image_stream) as img:
            print(f"Изображение скачано. Формат: {img.format}. Размер: {img.size}\n")
            # img.save("first_category_image.png") # Можно сохранить локально

# Запуск асинхронной функции main
if __name__ == "__main__":
    asyncio.run(main())
```

Для более подробной информации смотрите референсы [документации](https://open-inflation.github.io/pyaterochka_api/quick_start).

---

<div align="center">

### Report

If you have any problems using it / suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/pyaterochka_api/issues)!

</div>
