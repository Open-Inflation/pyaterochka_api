from enum import Enum

class Patterns(Enum):
    JS = r'\s*let\s+n\s*=\s*({.*});\s*'              # let n = {...};
    STR = r'(\w+)\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"'  # key: "value"
    DICT = r'(\w+)\s*:\s*{(.*?)}'                    # key: {...}
    LIST = r'(\w+)\s*:\s*\[([^\[\]]*(?:\[.*?\])*)\]' # key: [value]
    FIND = r'\{.*?\}|\[.*?\]'                        # {} or []
    # http(s)://user:pass@host:port
    PROXY = r'^(?:(?P<scheme>https?:\/\/))?(?:(?P<username>[^:@]+):(?P<password>[^@]+)@)?(?P<host>[^:\/]+)(?::(?P<port>\d+))?$'

class PurchaseMode(Enum):
    STORE    = "store"
    DELIVERY = "delivery"
