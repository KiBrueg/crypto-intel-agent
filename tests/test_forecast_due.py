#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.forecast_due import interval_seconds, forecast_due_status


def test_interval_seconds_parses_common_crypto_intervals():
    assert interval_seconds('15m') == 900
    assert interval_seconds('1h') == 3600
    assert interval_seconds('4h') == 14400
    assert interval_seconds('1d') == 86400


def test_forecast_due_status_marks_pending_due_from_start_ts_and_horizon():
    pending = forecast_due_status(start_ts=1_700_000_000_000, horizon_bars=4, interval='15m', verified_at=None, now_ts=1_700_000_000_000 + 1000)
    due = forecast_due_status(start_ts=1_700_000_000_000, horizon_bars=4, interval='15m', verified_at=None, now_ts=1_700_000_000_000 + 4 * 900 * 1000 + 1)
    verified = forecast_due_status(start_ts=1_700_000_000_000, horizon_bars=4, interval='15m', verified_at='2026-06-30T10:00:00+00:00', now_ts=1_700_000_000_000)
    assert pending['state'] == 'pending'
    assert pending['seconds_until_due'] > 0
    assert due['state'] == 'due'
    assert due['seconds_until_due'] <= 0
    assert verified['state'] == 'verified'


if __name__ == '__main__':
    test_interval_seconds_parses_common_crypto_intervals()
    test_forecast_due_status_marks_pending_due_from_start_ts_and_horizon()
    print('OK forecast due tests passed')
