import datetime
import typing as t

from fastapi import APIRouter, HTTPException

from common.config import UserSettings
from models.brokerage import FrequencyType, PeriodType, PriceHistory
from models.exceptions import InvalidInput
from services.authentication import AuthenticationService
from services.brokerage import get_brokerage_service

router = APIRouter(prefix="/priceHistory", tags=["Price History"])


@router.get("/", response_model=t.List[PriceHistory])
def get_price_histories(
    period_type: t.Optional[PeriodType] = None,
    periods: t.Optional[int] = None,
    frequency_type: t.Optional[FrequencyType] = None,
    frequency: t.Optional[int] = None,
    start_date: t.Optional[datetime.datetime] = None,
    end_date: t.Optional[datetime.datetime] = None,
) -> t.List[PriceHistory]:
    active_brokerage = AuthenticationService().active_brokerage
    if not active_brokerage:
        raise HTTPException(
            status_code=422, detail="Cannot get proce history without active brokerage"
        )
    brokerage_service = get_brokerage_service(active_brokerage)
    try:
        return brokerage_service.get_price_histories(
            UserSettings().symbols,
            period_type,
            periods,
            frequency_type,
            frequency,
            start_date,
            end_date,
        )
    except InvalidInput as e:
        raise HTTPException(status_code=422, detail=e)


@router.get("/{symbol}", response_model=PriceHistory)
def get_price_history(
    symbol: str,
    period_type: t.Optional[PeriodType] = None,
    periods: t.Optional[int] = None,
    frequency_type: t.Optional[FrequencyType] = None,
    frequency: t.Optional[int] = None,
    start_date: t.Optional[datetime.datetime] = None,
    end_date: t.Optional[datetime.datetime] = None,
) -> PriceHistory:
    active_brokerage = AuthenticationService().active_brokerage
    if not active_brokerage:
        raise HTTPException(
            status_code=422, detail="Cannot get proce history without active brokerage"
        )
    brokerage_service = get_brokerage_service(active_brokerage)
    try:
        return brokerage_service.get_price_histories(
            [symbol],
            period_type,
            periods,
            frequency_type,
            frequency,
            start_date,
            end_date,
        )[0]
    except InvalidInput as e:
        raise HTTPException(status_code=422, detail=e)
