#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.simulation import simulate_trade_path, run_rolling_simulations, calibrate_simulations


def candle(open_, high, low, close):
    return {'open': open_, 'high': high, 'low': low, 'close': close, 'time': 0}


def test_simulate_trade_path_detects_target_before_stop_for_long():
    candles = [
        candle(100, 101, 99, 100),
        candle(100, 103, 99.5, 102),
        candle(102, 106, 101, 105),
    ]
    result = simulate_trade_path(candles, entry=100, stop=95, target=105, side='long', start_index=0, lookahead=3)
    assert result['outcome'] == 'target'
    assert result['bars_to_outcome'] == 2
    assert result['mfe'] >= 5
    assert result['mae'] <= 1


def test_simulate_trade_path_detects_stop_before_target_for_short():
    candles = [
        candle(100, 101, 99, 100),
        candle(100, 104, 98, 103),
        candle(103, 104, 94, 95),
    ]
    result = simulate_trade_path(candles, entry=100, stop=103, target=94, side='short', start_index=0, lookahead=3)
    assert result['outcome'] == 'stopped'
    assert result['bars_to_outcome'] == 1


def test_rolling_simulations_and_calibration_report():
    candles = [candle(100+i, 102+i, 99+i, 101+i) for i in range(40)]
    sims = run_rolling_simulations(candles, side='long', lookahead=4, stride=5)
    assert sims
    assert all('predicted_status' in s for s in sims)
    report = calibrate_simulations(sims)
    assert report['mode'] == 'simulation_calibration'
    assert report['total'] == len(sims)
    assert 'by_predicted_status' in report
    assert report['recommendations']


if __name__ == '__main__':
    test_simulate_trade_path_detects_target_before_stop_for_long()
    test_simulate_trade_path_detects_stop_before_target_for_short()
    test_rolling_simulations_and_calibration_report()
    print('OK simulation tests passed')
