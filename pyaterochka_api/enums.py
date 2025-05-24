from enum import Enum

class Patterns(Enum):
    # http(s)://user:pass@host:port
    PROXY = r'^(?:(?P<scheme>https?:\/\/))?(?:(?P<username>[^:@]+):(?P<password>[^@]+)@)?(?P<host>[^:\/]+)(?::(?P<port>\d+))?$'

class PurchaseMode(Enum):
    STORE    = "store"
    DELIVERY = "delivery"
