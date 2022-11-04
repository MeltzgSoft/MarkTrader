export interface AuthUri {
    id: string;
    name: string;
    uri: string;
}

export interface AuthStatus {
    id: string;
    name: string;
    signedIn: boolean;
}

export interface UserSettings {
    symbols: string[];
    endOfDayExit: boolean;
    enableAutomatedTrading: boolean;
    tradingFrequencySeconds: number;
    positionSize: number;
}