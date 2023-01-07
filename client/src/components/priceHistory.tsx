import { FormControl, FormControlLabel, InputLabel, MenuItem, Select, Switch } from '@mui/material';
import { Stack } from '@mui/system';
import React from 'react';
import internal from 'stream';
import getEnumKeys from '../common/helpers';

enum PeriodType {
    DAY = 'day',
    MONTH = 'month',
    YEAR = 'year',
    YEAR_TO_DAY = 'ytd',
}

enum FrequencyType {
    MINUTE = 'minute',
    DAILY = 'day',
    WEEKLY = 'weekly',
    MONTHLY = 'monthly',
}

const validPeriods = {
    [PeriodType.DAY]: [1, 2, 3, 4, 5, 10],
    [PeriodType.MONTH]: [1, 2, 3, 6],
    [PeriodType.YEAR]: [1, 2, 3, 5, 10, 15, 20],
    [PeriodType.YEAR_TO_DAY]: [1]
};

const validFrequencyTypeForPeriod = {
    [PeriodType.DAY]: [FrequencyType.MINUTE],
    [PeriodType.MONTH]: [FrequencyType.DAILY, FrequencyType.WEEKLY],
    [PeriodType.YEAR]: [FrequencyType.DAILY, FrequencyType.WEEKLY, FrequencyType.MONTHLY],
    [PeriodType.YEAR_TO_DAY]: [FrequencyType.DAILY, FrequencyType.WEEKLY]
};

const validFrequencyByType = {
    [FrequencyType.DAILY]: [1, 5, 10, 15, 30],
    [FrequencyType.MINUTE]: [1],
    [FrequencyType.MONTHLY]: [1],
    [FrequencyType.WEEKLY]: [1]
};

interface PriceHistoryProps {
    symbols: string[];
}
interface PriceHistoryState {
    usePeriods: boolean;
    periodType: PeriodType;
    periods: number;
    frequencyType: FrequencyType;
    frequency: number;
    startDate: Date;
    endDate: Date | null;
}
export default class PriceHistoryPanel extends React.Component<PriceHistoryProps, PriceHistoryState> {
    constructor(props: PriceHistoryProps) {
        super(props);

        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        this.state = {
            usePeriods: true,
            periodType: PeriodType.DAY,
            periods: 1,
            frequencyType: FrequencyType.MINUTE,
            frequency: 1,
            startDate: yesterday,
            endDate: null,
        };
    }

    frequencyPeriodControl() {
        return <Stack direction='row' spacing={1}>
            <FormControl sx={{ m: 1, minWidth: 180 }}>
                <InputLabel>Period Type</InputLabel>
                <Select
                    value={this.state.periodType}
                    label='Period Type'
                    onChange={event => this.setState({
                        periodType: event.target.value as PeriodType,
                        periods: validPeriods[event.target.value as PeriodType][0],
                        frequencyType: validFrequencyTypeForPeriod[event.target.value as PeriodType][0],
                        frequency: validFrequencyByType[validFrequencyTypeForPeriod[event.target.value as PeriodType][0]][0]
                    })}>
                    {getEnumKeys(PeriodType).map((key, index) => (
                        <MenuItem key={index} value={PeriodType[key]}>{key}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl sx={{ m: 1, minWidth: 90 }}>
                <InputLabel># Periods</InputLabel>
                <Select
                    value={this.state.periods}
                    label='# Periods'
                    onChange={event => this.setState({ periods: Number(event.target.value) })}>
                    {validPeriods[this.state.periodType].map((p) => (
                        <MenuItem key={p} value={p}>{p}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl sx={{ m: 1, minWidth: 180 }}>
                <InputLabel>Frequency Type</InputLabel>
                <Select
                    value={this.state.frequencyType}
                    label='Frequency Type'
                    onChange={event => this.setState({
                        frequencyType: event.target.value as FrequencyType,
                        frequency: validFrequencyByType[event.target.value as FrequencyType][0]
                    })}>
                    {validFrequencyTypeForPeriod[this.state.periodType].map((f) => (
                        <MenuItem key={f} value={f}>{f}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl sx={{ m: 1, minWidth: 90 }}>
                <InputLabel>Frequency</InputLabel>
                <Select
                    value={this.state.frequency}
                    label='Frequency'
                    onChange={event => this.setState({ frequency: Number(event.target.value) })}>
                    {validFrequencyByType[this.state.frequencyType].map((f) => (
                        <MenuItem key={f} value={f}>{f}</MenuItem>
                    ))}
                </Select>
            </FormControl>
        </Stack>;
    }

    startEndControl() {
        return <Stack direction='row' spacing={1}>
            
        </Stack>
    }

    render(): React.ReactNode {
        return <div style={{ paddingTop: 30 }}>
            <Stack direction='row' spacing={1}>
                <FormControlLabel
                    label='Period/Frequency'
                    control={<Switch
                        checked={this.state.usePeriods}
                        onChange={event => this.setState({ usePeriods: event.target.checked })} />} />
                {this.state.usePeriods && this.frequencyPeriodControl()}
                {!this.state.usePeriods && this.startEndControl()}
            </Stack>
        </div>;
    }
}
