import { AuthStatus, AuthUri, AuthSIgnInInfo } from "./models";

async function getAuthUri(brokerageId: string): Promise<AuthUri> {
    const uri = new URL(`/api/v1/auth/${brokerageId}`, window.location.origin);
    const res = await fetch(uri);
    const res_1 = await res.json();
    return res_1 as AuthUri;
}

async function getSignInStatus(): Promise<AuthStatus> {
    const uri = new URL(`/api/v1/auth/`, window.location.origin);
    const res = await fetch(uri);
    const res_1 = await res.json();
    return res_1 as AuthStatus;
}

async function signOut(): Promise<boolean> {
    const uri = new URL(`/api/v1/auth/`, window.location.origin);
    const res = await fetch(uri, {method: 'DELETE'});
    const status = res.status;
    return status == 200;
}

async function signIn(brokerageId: string, accessCode: string): Promise<boolean> {
    const signInInfo: AuthSIgnInInfo = {
        id: brokerageId,
        code: accessCode
    };
    const uri = new URL(`/api/v1/auth/`, window.location.origin);
    const res = await fetch(uri, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(signInInfo)
    });
    const status = res.status;
    return status == 200
}

export {getAuthUri, getSignInStatus, signOut, signIn};
