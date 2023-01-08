export enum PeriodType {
    DAY = 'day',
    MONTH = 'month',
    YEAR = 'year',
    YEAR_TO_DAY = 'ytd',
}

export enum FrequencyType {
    MINUTE = 'minute',
    DAILY = 'day',
    WEEKLY = 'weekly',
    MONTHLY = 'monthly',
}

export interface AuthUri {
    id: string;
    name: string;
    uri: string;
}

export interface AuthStatus {
    id: string;
    name: string;
    signed_in: boolean;
}

export interface UserSettings {
    symbols: string[];
    end_of_day_exit: boolean;
    enable_automated_trading: boolean;
    trading_frequency_seconds: number;
    position_size: number;
}

export interface AuthSIgnInInfo {
    id: string;
    code: string;
}

export interface PriceCandle {
    open: number;
    close: number;
    high: number;
    low: number;
    volume: number;
    datetime: number;
}

export interface PriceHistory {
    symbol: string;
    prices: PriceCandle[]
}
