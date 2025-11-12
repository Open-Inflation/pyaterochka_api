from pyaterochka_api import PyaterochkaAPI
from pprint import pprint

async def main():
    # RUS: Использование проксирования опционально. Вы можете создать несколько агентов с разными прокси для ускорения парса.
    # ENG: Proxy usage is optional. You can create multiple agents with different proxies for faster parsing.
    async with PyaterochkaAPI(headless=False) as API:
        # RUS: Выводит активные предложения магазина
        # ENG: Outputs active offers of the store
        pprint((await API.Catalog.tree(sap_code_store_id="35XY", subcategories=False)).json())

import asyncio
asyncio.run(main())