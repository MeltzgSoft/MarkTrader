import React from 'react';
import { UserSettings } from '../common/models';
import Slider from './toggle';

interface UserSettingsPanelProps extends UserSettings {
    onUpdate: (data: object) => void;
}
export default class UserSettingsPanel extends React.Component<UserSettingsPanelProps> {
    constructor(props: UserSettingsPanelProps) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(setting: string, value: boolean): void {
        const obj: Record<string, unknown> = {};
        obj[setting] = value;
        this.props.onUpdate(obj);
    }

    render(): React.ReactNode {
        return <div>
            <Slider label="Enable Automated Trading" onChange={(value: boolean) => this.handleChange('enableAutomatedTrading', value)} checked={this.props.enable_automated_trading}></Slider>
            <Slider label="Enable End of DayExit" onChange={(value: boolean) => this.handleChange('endOfDayExit', value)} checked={this.props.end_of_day_exit}></Slider>
        </div>;
    }
}
