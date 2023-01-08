import { Button, FormControl, FormControlLabel, InputLabel, MenuItem, Select, Switch, TextField } from '@mui/material';
import { Stack } from '@mui/system';
import { DateTimePicker } from '@mui/x-date-pickers';
import React from 'react';
import { getPriceHistories } from '../common/apiClient';
import getEnumKeys from '../common/helpers';
import { FrequencyType, PeriodType, PriceHistory } from '../common/models';

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
    useEndDate: boolean;
    periodType: PeriodType;
    periods: number;
    frequencyType: FrequencyType;
    frequency: number;
    startDate: Date;
    endDate: Date | null;
    priceData: PriceHistory[];
}
export default class PriceHistoryPanel extends React.Component<PriceHistoryProps, PriceHistoryState> {
    constructor(props: PriceHistoryProps) {
        super(props);

        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        this.state = {
            usePeriods: true,
            useEndDate: false,
            periodType: PeriodType.DAY,
            periods: 1,
            frequencyType: FrequencyType.MINUTE,
            frequency: 1,
            startDate: yesterday,
            endDate: null,
            priceData: []
        };

        this.refreshData = this.refreshData.bind(this);
    }

    refreshData() {
        let pricePromise: Promise<PriceHistory[]>;
        if (this.state.usePeriods) {
            pricePromise = getPriceHistories({
                periodType: this.state.periodType,
                periods: this.state.periods,
                frequencyType: this.state.frequencyType,
                frequency: this.state.frequency
            });
        } else {
            pricePromise = getPriceHistories({
                startDate: this.state.startDate,
                endDate: this.state.useEndDate ? this.state.endDate : null
            });
        }
        pricePromise.then(value => this.setState({priceData: value}));
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
            <DateTimePicker
                label="Start Time"
                value={new Date(this.state.startDate)}
                onChange={newDate => this.setState({ startDate: newDate as Date })}
                renderInput={(params) => <TextField {...params} />}
            />
            <FormControlLabel
                label={`End ${this.state.useEndDate ? 'At' : 'Now'}`}
                control={<Switch
                    checked={this.state.useEndDate}
                    onChange={event => this.setState({ useEndDate: event.target.checked })} />} />
            {this.state.useEndDate && <DateTimePicker
                label="End Time"
                value={new Date(this.state.endDate || new Date())}
                onChange={newDate => this.setState({ endDate: newDate as Date })}
                renderInput={(params) => <TextField {...params} />}
            />}
        </Stack>;
    }

    render(): React.ReactNode {
        return <div style={{ paddingTop: 30 }}>
            <Stack direction='row' spacing={1}>
                <FormControlLabel
                    label='Period/Frequency'
                    control={<Switch
                        checked={this.state.usePeriods}
                        onChange={event => this.setState({ usePeriods: event.target.checked })} />} />
                {this.state.usePeriods ? this.frequencyPeriodControl() : this.startEndControl()}
                <Button variant='contained' onClick={this.refreshData}>Refresh</Button>
            </Stack>
        </div>;
    }
}
