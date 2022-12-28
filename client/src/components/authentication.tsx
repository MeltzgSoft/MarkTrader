import { Button, Stack } from '@mui/material';
import React from 'react';
import { getAuthUri, getSignInStatus, signOut } from '../common/apiClient';
import './authentication.css';

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

        this.updateStatus = this.updateStatus.bind(this);
        this.signOut = this.signOut.bind(this);

        this.updateStatus();
    }

    render(): React.ReactNode {
        return <div style={{'display': 'inline-block'}}>
            <AuthenticatorStatus isSignedIn={this.state.isSignedIn}></AuthenticatorStatus>
            <div>
                {!this.state.isSignedIn ?
                    <Button variant='contained' onClick={this.initiateAuth}>Sign In</Button> :
                    <Stack spacing={0.5} direction='row'>
                        <Button variant='contained' onClick={this.updateStatus}>Refresh Status</Button>
                        <Button variant='contained' onClick={this.signOut}>Sign Out</Button>
                    </Stack>}
            </div>
        </div>;
    }

    initiateAuth(): void {
        getAuthUri('td-a').then(authInfo =>
            window.location.replace(authInfo.uri)
        );
    }

    updateStatus(): void {
        getSignInStatus().then(authStatus => this.setState({['isSignedIn']: authStatus.signed_in}));
    }

    signOut(): void {
        signOut().then(this.updateStatus);
    }
}
