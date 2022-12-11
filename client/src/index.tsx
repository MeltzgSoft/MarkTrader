import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Authenticator from './components/authentication';
import UserSettingsPanel from './components/userSettingsPanel';
import { UserSettings } from './common/models';
import { signIn } from './common/apiClient';

class Application extends React.Component<Record<string, unknown>, UserSettings> {
    constructor(props: Record<string, unknown>) {
        super(props);
        this.state = {
            symbols: [],
            end_of_day_exit: false,
            enable_automated_trading: false,
            trading_frequency_seconds: 5,
            position_size: 100
        };
        this.handleUpdateUserSettings = this.handleUpdateUserSettings.bind(this);
    }

    handleUpdateUserSettings(data: object) {
        console.log(data);
    }

    render(): React.ReactNode {
        if (window.location.search) {
            const params = new URLSearchParams(window.location.search);
            signIn('td-a', params.get('code') as string).then(
                () => {
                    window.location.replace(window.location.origin);
                });
        }
        return <div>
            <Authenticator/>
            <UserSettingsPanel onUpdate={this.handleUpdateUserSettings} symbols={this.state.symbols} end_of_day_exit={this.state.end_of_day_exit} enable_automated_trading={this.state.enable_automated_trading} trading_frequency_seconds={this.state.trading_frequency_seconds} position_size={this.state.position_size}/>
        </div>;
    }
}

// ========================================

const root = ReactDOM.createRoot(document.getElementById('root') as Element);
root.render(<Application />);
