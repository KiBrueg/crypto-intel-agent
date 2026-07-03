#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.market_news import classify_news_event, score_news_items, build_global_news_impact
from trader_assistant.simulation import calibrate_simulations
from web_dashboard import render_dashboard_html


def test_news_event_classifier_scores_hawkish_fed_as_bearish_for_crypto():
    item = {'title': 'Fed signals higher for longer interest rates after hot inflation report', 'source': 'Test'}
    scored = classify_news_event(item)
    assert scored['bias'] == 'bearish'
    assert scored['impact_score'] < 0
    assert 'rates' in scored['drivers'] or 'inflation' in scored['drivers']


def test_news_event_classifier_scores_rate_cut_and_etf_as_bullish():
    item = {'title': 'Fed rate cut hopes rise as spot Bitcoin ETF sees record inflows', 'source': 'Test'}
    scored = classify_news_event(item)
    assert scored['bias'] == 'bullish'
    assert scored['impact_score'] > 0
    assert 'liquidity' in scored['drivers'] or 'crypto_adoption' in scored['drivers']


def test_score_news_items_returns_market_indicator_with_bull_base_bear_cases():
    items = [
        {'title': 'Fed rate cut hopes rise after cooling inflation', 'source': 'Macro'},
        {'title': 'Oil shipping route blocked after new war escalation', 'source': 'Geo'},
        {'title': 'Crypto regulation bill passes with clearer exchange rules', 'source': 'Policy'},
    ]
    result = score_news_items(items)
    assert result['mode'] == 'market_news_impact'
    assert result['items_scored'] == 3
    assert result['scenarios']['bullish']['thesis']
    assert result['scenarios']['base']['thesis']
    assert result['scenarios']['bearish']['thesis']
    assert result['fear_greed_pressure'] in {'fear_up', 'greed_up', 'mixed'}


def test_global_news_impact_card_groups_war_sanctions_bans_deals_and_leaders():
    items = [
        {'title': 'New sanctions target oil shipping after war escalation', 'source': 'Geo'},
        {'title': 'President announces peace deal and ceasefire framework', 'source': 'Politics'},
        {'title': 'Regulator proposes ban on crypto staking services', 'source': 'Reg'},
        {'title': 'Billionaire CEO says Bitcoin is digital gold as ETF inflows rise', 'source': 'Markets'},
    ]
    result = build_global_news_impact(items)
    assert result['mode'] == 'global_news_impact'
    assert result['headline']
    assert result['crypto_bias'] in {'bullish', 'bearish', 'mixed'}
    assert result['stocks_bias'] in {'bullish', 'bearish', 'mixed'}
    assert 'war_conflict' in result['category_counts']
    assert 'sanctions_bans' in result['category_counts']
    assert 'leaders_billionaires' in result['category_counts']
    assert result['cards'][0]['crypto_effect'] in {'growth_pressure', 'fall_pressure', 'mixed'}
    assert result['cards'][0]['why']
    assert result['what_to_watch']


def test_calibration_report_contains_multiple_scenarios():
    sims = [
        {'predicted_status': 'clean', 'outcome': 'target'},
        {'predicted_status': 'clean', 'outcome': 'stopped'},
        {'predicted_status': 'not_clean', 'outcome': 'stopped'},
        {'predicted_status': 'watch', 'outcome': 'timeout'},
    ]
    report = calibrate_simulations(sims)
    assert 'scenarios' in report
    assert set(report['scenarios']) >= {'bullish', 'base', 'bearish'}
    assert report['scenarios']['bullish']['calibration_action']
    assert report['scenarios']['bearish']['calibration_action']


def test_dashboard_contains_news_impact_section():
    html = render_dashboard_html()
    assert 'Macro/RSS News Impact' in html
    assert 'Global News Impact' in html
    assert 'globalnewsimpact' in html
    assert 'scanGlobalNewsImpact' in html
    assert 'War / sanctions / bans / leaders' in html


if __name__ == '__main__':
    test_news_event_classifier_scores_hawkish_fed_as_bearish_for_crypto()
    test_news_event_classifier_scores_rate_cut_and_etf_as_bullish()
    test_score_news_items_returns_market_indicator_with_bull_base_bear_cases()
    test_global_news_impact_card_groups_war_sanctions_bans_deals_and_leaders()
    test_calibration_report_contains_multiple_scenarios()
    test_dashboard_contains_news_impact_section()
    print('OK macro news calibration tests passed')
