interface AuthUri {
    id: string;
    name: string;
    uri: string;
}

function getAuthUri(brokerageId: string): Promise<AuthUri> {
    const uri = new URL('/api/v1/auth/${brokerageId}', window.location.href);
    return fetch(uri)
        .then(res => res.json())
        .then(res => {
            return res as AuthUri;
        });
}

export {getAuthUri};
