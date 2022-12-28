import React from 'react';
import { UserSettings } from '../common/models';
import { Box, FormControlLabel, IconButton, Stack, Switch, TextField, Tooltip } from '@mui/material';
import MaterialReactTable from 'material-react-table';
import { Delete } from '@mui/icons-material';

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

    wrappedSymbols(): Record<string, unknown>[] {
        return this.props.symbols.map((val: string) => { return { symbol: val }; });
    }

    handleDeleteSymbol(symbol: string): void {
        const symbols = this.props.symbols.filter((val: string) => val !== symbol);
        this.handleChange("symbols", symbols);
    }

    render(): React.ReactNode {
        return <Stack direction='column' spacing={1} justifyContent='flex-start' alignItems='baseline'>
            <FormControlLabel
                label='Enable Automated Trading'
                style={{ margin: 0 }}
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
            <MaterialReactTable
                columns={[{ accessorKey: 'symbol', header: 'Symbols' }]}
                data={this.wrappedSymbols()}
                enableRowActions
                renderRowActions={({ row, table }) => (
                    <Box sx={{ display: 'flex', gap: '1rem' }}>
                        <Tooltip arrow placement="right" title="Delete">
                            <IconButton color="error" onClick={() => this.handleDeleteSymbol(row.getValue('symbol'))}>
                                <Delete />
                            </IconButton>
                        </Tooltip>
                    </Box>
                )} />
        </Stack>;
    }
}
