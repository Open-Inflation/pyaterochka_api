Quick Start
===========

.. code-block:: console

    pip install pyaterochka_api
    python -m camoufox fetch

.. code-block:: python
    
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

.. code-block:: console

    > SAP код выбранного магазина: 35XY
    > Первая категория: Пятёрочка выручает!...
    > Первый товар (PLU): 3395339
    > Название первого товара: Кофе Egoiste Noir молотый 250г...
    > Предложения по геолокации для 'москва': Москва, Красная площадь...
    > Текущая геолокация (долгота, широта): 37.637919, 55.812332
    > Изображение скачано. Формат: PNG. Размер: (345, 345)


Для более подробной информации смотрите референсы :class:`~pyaterochka_api.endpoints.catalog.ClassCatalog`, :class:`~pyaterochka_api.endpoints.geolocation.ClassGeolocation`, :class:`~pyaterochka_api.endpoints.general.ClassGeneral`, :class:`~pyaterochka_api.endpoints.advertising.ClassAdvertising` документации.
