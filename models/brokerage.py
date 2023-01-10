import typing as t
from enum import Enum

from pydantic import BaseModel


class BrokerageId(Enum):
    TD = "td-a"


class PeriodType(Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    YEAR_TO_DAY = "ytd"


class FrequencyType(Enum):
    MINUTE = "minute"
    DAILY = "day"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PriceCandle(BaseModel):
    open: float
    close: float
    high: float
    low: float
    volume: int
    datetime: int


class PriceHistory(BaseModel):
    symbol: str
    prices: t.List[PriceCandle]
