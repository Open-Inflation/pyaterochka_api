from enum import Enum


class PurchaseMode(Enum):
    STORE = "store"
    DELIVERY = "delivery"


class Sorting(Enum):
    PRICE_DESC = "price_desc"
    """Сначала дороже"""
    PRICE_ASC = "price_asc"
    """Сначала дешевле"""
    DISCOUNT_DESC = "discount_desc"
    """По размеру скидки"""
    RATING_DESC = "rating_desc"
    """Сначала с высоким рейтингом"""
    POPULARITY = "popularity"
    """Сначала популярные"""
