#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.scoring import score_market, rank_candidates
from trader_assistant.pair_trading import analyze_pair
from trader_assistant.trader_report import render_trader_report


def sample_market():
    return [
        {
            'symbol': 'SOLUSDT', 'price': 100.0, 'change_24h': 6.0,
            'volume_24h': 900_000_000, 'market_cap': 40_000_000_000,
            'range_pct': 4.0, 'vol_to_mcap': 0.0225,
            'spread_bps': 3.0, 'liquidity_usd': 20_000_000,
            'near_high_pct': 0.8, 'distance_from_mean_pct': 1.2,
            'trend_5': 1.1, 'trend_20': 3.5, 'volume_zscore': 2.2,
            'btc_relative_strength': 1.4,
        },
        {
            'symbol': 'DOGEUSDT', 'price': 0.2, 'change_24h': 18.0,
            'volume_24h': 500_000_000, 'market_cap': 20_000_000_000,
            'range_pct': 14.0, 'vol_to_mcap': 0.025,
            'spread_bps': 18.0, 'liquidity_usd': 2_000_000,
            'near_high_pct': 4.0, 'distance_from_mean_pct': 9.5,
            'trend_5': -0.4, 'trend_20': 12.0, 'volume_zscore': 3.5,
            'btc_relative_strength': 0.4,
        },
        {
            'symbol': 'MICROUSDT', 'price': 0.01, 'change_24h': 25.0,
            'volume_24h': 50_000, 'market_cap': 1_000_000,
            'range_pct': 35.0, 'vol_to_mcap': 0.05,
            'spread_bps': 90.0, 'liquidity_usd': 20_000,
            'near_high_pct': 0.2, 'distance_from_mean_pct': 20.0,
            'trend_5': 5.0, 'trend_20': 20.0, 'volume_zscore': 5.0,
            'btc_relative_strength': 3.0,
        },
    ]


def test_strategy_scoring_prefers_liquid_scalping_candidate():
    scored = score_market(sample_market())
    sol = next(x for x in scored if x['symbol'] == 'SOLUSDT')
    micro = next(x for x in scored if x['symbol'] == 'MICROUSDT')
    assert sol['scores']['scalping'] > micro['scores']['scalping']
    assert 'tight spread' in ' '.join(sol['reasons']['scalping']).lower()
    assert any('liquidity' in flag.lower() for flag in micro['risk_flags'])


def test_strategy_scoring_identifies_breakout_and_mean_reversion_candidates():
    scored = score_market(sample_market())
    top_breakout = rank_candidates(scored, 'breakout', limit=1)[0]
    top_reversion = rank_candidates(scored, 'mean_reversion', limit=1)[0]
    assert top_breakout['symbol'] == 'SOLUSDT'
    assert top_reversion['symbol'] == 'DOGEUSDT'
    assert top_breakout['setup']['confirmation']
    assert top_reversion['setup']['invalidation']


def test_pair_analysis_detects_spread_zscore_and_correlation_breakdown():
    base = [100, 101, 102, 103, 104, 105, 106, 108, 110, 111, 112, 113]
    quote = [50, 50.5, 51, 51.5, 52, 52.5, 53, 54, 55, 55.5, 50, 49]
    result = analyze_pair('SOL', 'ETH', base, quote, window=8)
    assert result['pair'] == 'SOL/ETH'
    assert abs(result['spread_zscore']) > 1.0
    assert 'correlation' in result
    assert result['risk_flags']


def test_trader_report_groups_candidates_by_strategy():
    scored = score_market(sample_market())
    report = render_trader_report(scored, pair_results=[], title='TEST REPORT')
    assert 'Top Scalping Candidates' in report
    assert 'Top Breakout Candidates' in report
    assert 'Top Mean Reversion Candidates' in report
    assert 'Risk Flags' in report
    assert 'not financial advice' in report.lower()


if __name__ == '__main__':
    test_strategy_scoring_prefers_liquid_scalping_candidate()
    test_strategy_scoring_identifies_breakout_and_mean_reversion_candidates()
    test_pair_analysis_detects_spread_zscore_and_correlation_breakdown()
    test_trader_report_groups_candidates_by_strategy()
    print('OK trader_assistant tests passed')
