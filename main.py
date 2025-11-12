from pyaterochka_api import PyaterochkaAPI

async def main():
    # RUS: Использование проксирования опционально. Вы можете создать несколько агентов с разными прокси для ускорения парса.
    # ENG: Proxy usage is optional. You can create multiple agents with different proxies for faster parsing.
    async with PyaterochkaAPI(headless=False) as API:
        # RUS: Выводит активные предложения магазина
        # ENG: Outputs active offers of the store
        print(f"Active offers output: {(await API.Advertising.active_inout()).json()!s:.100s}...\n")

import asyncio
asyncio.run(main())