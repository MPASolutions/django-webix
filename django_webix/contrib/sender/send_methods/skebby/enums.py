from enum import Enum


class SkebbyBoolean(Enum):
    TRUE = "true"
    FALSE = "false"


class SkebbyMessageType(Enum):
    GP = "Classic+"
    TI = "Classic"
    SI = "Basic"


class SkebbyEncoding(Enum):
    GSM = "gsm"
    UCS2 = "ucs2"
