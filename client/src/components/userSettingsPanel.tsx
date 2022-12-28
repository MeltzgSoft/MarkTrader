import React from 'react';
import { UserSettings } from '../common/models';
import { FormControlLabel, FormGroup, Stack, Switch, TextField } from '@mui/material';

interface UserSettingsPanelProps extends UserSettings {
    onUpdate: (data: Record<string, unknown>) => void;
}
export default class UserSettingsPanel extends React.Component<UserSettingsPanelProps> {
    constructor(props: UserSettingsPanelProps) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(setting: string, value: unknown): void {
        const obj: Record<string, unknown> = {};
        obj[setting] = value;
        this.props.onUpdate(obj);
    }

    render(): React.ReactNode {
        return <Stack direction='column' spacing={1} justifyContent='flex-start' alignItems='baseline'>
            <FormControlLabel
                label='Enable Automated Trading'
                style={{margin: 0}}
                control={<Switch
                    onChange={
                        (event: React.ChangeEvent<HTMLInputElement>) =>
                            this.handleChange('enable_automated_trading', event.target.checked)
                    }
                    checked={this.props.enable_automated_trading} />} />
            <FormControlLabel
                label='Enable End of Day Exit'
                control={<Switch
                    onChange={
                        (event: React.ChangeEvent<HTMLInputElement>) =>
                            this.handleChange('end_of_day_exit', event.target.checked)
                    }
                    checked={this.props.end_of_day_exit} />} />
            <TextField
                label='Trading Frequency (seconds)'
                type='number'
                InputProps={{ inputProps: { min: 1 } }}
                onChange={
                    (event: React.ChangeEvent<HTMLInputElement>) =>
                        this.handleChange('trading_frequency_seconds', event.target.valueAsNumber)
                }
                value={this.props.trading_frequency_seconds} />
            <TextField
                label='Position Size'
                type='number'
                InputProps={{ inputProps: { min: 0 } }}
                onChange={
                    (event: React.ChangeEvent<HTMLInputElement>) =>
                        this.handleChange('position_size', event.target.valueAsNumber)
                }
                value={this.props.position_size} />
        </Stack>;
    }
}
