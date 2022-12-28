import { AuthStatus, AuthUri, AuthSIgnInInfo as AuthSignInInfo, UserSettings } from './models';

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
    const res = await fetch(uri, {method: 'DELETE'});
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
        headers: {'Content-Type': 'application/json'},
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
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const resJson = await res.json();
    return resJson as UserSettings;
}

export {getAuthUri, getSignInStatus, signOut, signIn, getUserSettings, setUserSettings};
