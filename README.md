# Pyaterochka API *(not official / не официальный)*

Pyaterochka (Пятёрочка) - https://5ka.ru/

### Usage / Использование:
```py
import pyaterochka_api
import asyncio


async def main():
    # RUS: Выводит список всех категорий на сайте
    # ENG: Outputs a list of all categories on the site
    catalog = await pyaterochka_api.categories_list(subcategories=True)
    print(f"Categories list output: {catalog!s:.100s}...\n")

    # RUS: Выводит список всех товаров выбранной категории (ограничение 100 элементов, если превышает - запрашивайте через дополнительные страницы)
    # ENG: Outputs a list of all items in the selected category (limiting to 100 elements, if exceeds - request through additional pages)
    # Страниц не сущетвует, использовать желаемый лимит (до 499) / Pages do not exist, use the desired limit (up to 499)
    print(f"Items list output: {await pyaterochka_api.products_list(catalog[0]['id'], limit=5)!s:.100s}...\n")

    # RUS: Выводит основной конфиг сайта (очень долгая функция, рекомендую сохранять в файл и переиспользовать)
    # ENG: Outputs the main config of the site (large function, recommend to save in a file and re-use it)
    # RUS: Если требуется, можно настроить вывод логов в консоль
    # ENG: If required, you can configure the output of logs in the console
    print(f"Main config: {await pyaterochka_api.get_config(debug=True)!s:.100s}...\n")


if __name__ == '__main__':
    asyncio.run(main())
```

### Report / Обратная связь

If you have any problems using it /suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/pyaterochka_api/issues)!

Если у вас возникнут проблемы в использовании / пожелания, не стесняйтесь писать на [GitHub проекта](https://github.com/Open-Inflation/pyaterochka_api/issues)!
