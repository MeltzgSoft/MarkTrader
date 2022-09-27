import React from 'react';
import {getAuthUri} from './apiClient';

export default class Authenticator extends React.Component {
    render(): React.ReactNode {
        return <button onClick={this.initiateAuth}>Sign In</button>;
    }

    initiateAuth(): void {
        getAuthUri('td-a').then(authInfo =>
            window.location.replace(authInfo.uri)
        );
    }
}
