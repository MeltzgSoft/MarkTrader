interface AuthUri {
    id: string;
    name: string;
    uri: string;
}

interface AuthStatus {
    id: string;
    name: string;
    signedIn: boolean;
}

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
    const status = await res.status;
    return status == 200
}

export {getAuthUri, getSignInStatus, signOut};
