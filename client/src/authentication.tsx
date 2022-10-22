import React from 'react';
import { getAuthUri, getSignInStatus } from './apiClient';
import './authentication.css'

interface AuthenticatorState {
    isSignedIn: boolean;
}

function AuthenticatorStatus(props: AuthenticatorState) {
    if (props.isSignedIn) {
        return <div className='signin-status signed-in'>Connected</div>;
    } else {
        return <div className='signin-status signed-out'>Disconnected</div>;
    }
}

export default class Authenticator extends React.Component<Record<string, unknown>, AuthenticatorState> {
    constructor(props: Record<string, unknown>) {
        super(props);
        this.state = {
            isSignedIn: false
        };
        getSignInStatus().then(authStatus => this.setState({["isSignedIn"]: authStatus.signedIn}))
    }

    render(): React.ReactNode {
        return <div style={{'display': 'inline-block'}}>
            <AuthenticatorStatus isSignedIn={this.state.isSignedIn}></AuthenticatorStatus>
            <div>
                <button onClick={this.initiateAuth}>Sign In</button>
                <button>Refresh Status</button>
                <button>Sign Out</button>
            </div>
        </div>;
    }

    initiateAuth(): void {
        getAuthUri('td-a').then(authInfo =>
            window.location.replace(authInfo.uri)
        );
    }
}
