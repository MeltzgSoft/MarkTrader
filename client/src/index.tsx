import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Authenticator from './authentication';

class Application extends React.Component {
    constructor(props: Record<string, unknown>) {
        super(props);
        this.state = {
            isSignedIn: false
        }
    }

    render(): React.ReactNode {
        if (window.location.search) {
            window.location.replace(window.location.origin);
        }
        return <div>
            <Authenticator/>
        </div>
    }
}

// ========================================

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<Application />);
