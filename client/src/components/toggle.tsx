import React from 'react';
import './toggle.css';

interface ToggleProps {
    onChange: (value: boolean) => void;
    checked: boolean;
    label: string;
}

export default class Toggle extends React.Component<ToggleProps> {
    constructor(props: ToggleProps) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event: React.FormEvent<HTMLInputElement>): void {
        this.props.onChange(event.currentTarget.checked);
    }

    render(): React.ReactNode {
        return <div>
            <label>{this.props.label}</label>
            <label className="switch">
                <input type="checkbox" onChange={this.handleChange}/>
                <span className="toggle round"></span>
            </label>
        </div>
    }
}
