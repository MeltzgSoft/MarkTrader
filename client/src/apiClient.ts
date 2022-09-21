interface AuthUri {
    id: string;
    name: string;
    uri: string;
}

async function getAuthUri(brokerageId: string): Promise<AuthUri> {
    const uri = new URL(`/api/v1/auth/${brokerageId}`, window.location.origin);
    const res = await fetch(uri);
    const res_1 = await res.json();
    return res_1 as AuthUri;
}

export {getAuthUri};
