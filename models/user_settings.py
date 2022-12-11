from typing import List, Optional

from pydantic import BaseModel


class UserSettingsPatch(BaseModel):
    symbols: Optional[List[str]] = None
    end_of_day_exit: Optional[bool] = None
    enable_automated_trading: Optional[bool] = None
    trading_frequency_seconds: Optional[int] = None
    position_size: Optional[float] = None
