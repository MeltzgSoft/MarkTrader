import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Authenticator from './components/authentication';
import UserSettingsPanel from './components/userSettingsPanel';
import { UserSettings } from './common/models';

class Application extends React.Component<Record<string, unknown>, UserSettings> {
    constructor(props: Record<string, unknown>) {
        super(props);
        this.state = {
            symbols: [],
            endOfDayExit: false,
            enableAutomatedTrading: false,
            tradingFrequencySeconds: 5,
            positionSize: 100
        }
        this.handleUpdateUserSettings = this.handleUpdateUserSettings.bind(this);
    }

    handleUpdateUserSettings(data: object) {
        console.log(data);
    }

    render(): React.ReactNode {
        if (window.location.search) {
            window.location.replace(window.location.origin);
        }
        return <div>
            <Authenticator/>
            <UserSettingsPanel onUpdate={this.handleUpdateUserSettings} symbols={this.state.symbols} endOfDayExit={this.state.endOfDayExit} enableAutomatedTrading={this.state.enableAutomatedTrading} tradingFrequencySeconds={this.state.tradingFrequencySeconds} positionSize={this.state.positionSize}/>
        </div>
    }
}

// ========================================

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<Application />);
