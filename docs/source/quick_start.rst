Quick Start
===========

.. code-block:: console

    pip install chizhik_api
    python -m camoufox fetch

.. code-block:: python
    
    from chizhik_api import ChizhikAPI

    async def main():
        # RUS: Использование проксирования опционально. Вы можете создать несколько агентов с разными прокси для ускорения парса.
        # ENG: Proxy usage is optional. You can create multiple agents with different proxies for faster parsing.
        async with ChizhikAPI(proxy="user:password@host:port", headless=False) as API:
            # RUS: Выводит активные предложения магазина
            # ENG: Outputs active offers of the store
            print(f"Active offers output: {(await API.Advertising.active_inout()).json()!s:.100s}...\n")
            
            # RUS: Выводит список городов соответствующих поисковому запросу (только на русском языке)
            # ENG: Outputs a list of cities corresponding to the search query (only in Russian language)
            city_list = (await API.Geolocation.cities_list(search_name='ар', page=1)).json()
            print(f"Cities list output: {city_list!s:.100s}...\n")
            # Счет страниц с единицы / index starts from 1

            # RUS: Выводит список всех категорий на сайте
            # ENG: Outputs a list of all categories on the site
            catalog = (await API.Catalog.tree()).json()
            print(f"Categories list output: {catalog!s:.100s}...\n")

            # RUS: Выводит список всех товаров выбранной категории (ограничение 100 элементов, если превышает - запрашивайте через дополнительные страницы)
            # ENG: Outputs a list of all items in the selected category (limiting to 100 elements, if exceeds - request through additional pages)
            items = (await API.Catalog.products_list(category_id=catalog[0]['id'], page=1)).json()
            print(f"Items list output: {items!s:.100s}...\n")
            # Счет страниц с единицы / index starts from 1

            # RUS: Сохраняем изображение с сервера (в принципе, сервер отдал бы их и без обертки моего объекта, но лучше максимально претворяться обычным пользователем)
            # ENG: Saving an image from the server (in fact, the server gave them and without wrapping my object, but better to be as a regular user)
            image = await API.General.download_image(items['items'][0]['images'][0]['image'])
            with open(image.name, 'wb') as f:
                f.write(image.read())

    import asyncio
    asyncio.run(main())

.. code-block:: console

    > Active offers output: {'title': 'НАДО УСПЕТЬ', 'description': 'Новые товары каждую неделю.\r\nКоличество ограниченно!', 'i...
    > Cities list output: {'count': 14, 'next': None, 'previous': None, 'page_size': 30, 'total_pages': 1, 'items': [{'distanc...
    > Categories list output: [{'id': 133, 'name': 'Основной каталог', 'image': None, 'icon': None, 'depth': 1, 'is_adults': False...
    > Items list output: {'count': 3800, 'next': 2, 'previous': None, 'page_size': 100, 'total_pages': 38, 'items': [{'id': 2...


Для более подробной информации смотрите референсы :class:`~chizhik_api.endpoints.catalog.ClassCatalog`, :class:`~chizhik_api.endpoints.geolocation.ClassGeolocation`, :class:`~chizhik_api.endpoints.general.ClassGeneral`, :class:`~chizhik_api.endpoints.advertising.ClassAdvertising` документации.
