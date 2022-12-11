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
