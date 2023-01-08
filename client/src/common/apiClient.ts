import { AuthStatus, AuthUri, AuthSIgnInInfo as AuthSignInInfo, UserSettings, PriceCandle, PeriodType, FrequencyType, PriceHistory } from './models';

async function getAuthUri(brokerageId: string): Promise<AuthUri> {
    const uri = new URL(`/api/v1/auth/${brokerageId}`, window.location.origin);
    const res = await fetch(uri);
    const res_1 = await res.json();
    return res_1 as AuthUri;
}

async function getSignInStatus(): Promise<AuthStatus> {
    const uri = new URL('/api/v1/auth/', window.location.origin);
    const res = await fetch(uri);
    const res_1 = await res.json();
    return res_1 as AuthStatus;
}

async function signOut(): Promise<boolean> {
    const uri = new URL('/api/v1/auth/', window.location.origin);
    const res = await fetch(uri, { method: 'DELETE' });
    const status = res.status;
    return status === 200;
}

async function signIn(brokerageId: string, accessCode: string): Promise<boolean> {
    const signInInfo: AuthSignInInfo = {
        id: brokerageId,
        code: accessCode
    };
    const uri = new URL('/api/v1/auth/', window.location.origin);
    const res = await fetch(uri, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signInInfo)
    });
    const status = res.status;
    return status === 200;
}

async function getUserSettings(): Promise<UserSettings> {
    const uri = new URL('/api/v1/userSettings/', window.location.origin);
    const res = await fetch(uri);
    const resJson = await res.json();
    return resJson as UserSettings;
}

async function setUserSettings(data: Record<string, unknown>): Promise<UserSettings> {
    const uri = new URL('/api/v1/userSettings/', window.location.origin);
    const res = await fetch(uri, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const resJson = await res.json();
    return resJson as UserSettings;
}

interface PriceHistoryParameters {
    periodType?: PeriodType;
    periods?: number;
    frequencyType?: FrequencyType;
    frequency?: number;
    startDate?: Date;
    endDate?: Date | null;
}

async function getPriceHistories({
    periodType, periods, frequencyType, frequency, startDate, endDate
}: PriceHistoryParameters): Promise<PriceHistory[]> {
    const queryParams: Record<string, any> = {
        period_type: periodType,
        periods: periods,
        frequency_type: frequencyType,
        frequency: frequency,
        start_date: startDate ? startDate.toISOString() : null,
        end_date: endDate ? endDate.toISOString() : null
    };

    Object.keys(queryParams).forEach(param => {
        if (!queryParams[param]) {
            delete queryParams[param];
        }
    });

    const uri = new URL('/api/v1/priceHistory/', window.location.origin);
    Object.entries(queryParams).forEach(([key, value]) => uri.searchParams.append(key, value));

    const res = await fetch(uri);
    const resJson = await res.json();
    return resJson as PriceHistory[];
}

export { getAuthUri, getSignInStatus, signOut, signIn, getUserSettings, setUserSettings, getPriceHistories };
