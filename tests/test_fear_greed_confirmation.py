#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.fear_greed import classify_fear_greed, evaluate_fear_greed, render_fear_greed_report


def test_classify_fear_greed_thresholds():
    assert classify_fear_greed(10) == 'extreme fear'
    assert classify_fear_greed(30) == 'fear'
    assert classify_fear_greed(50) == 'neutral'
    assert classify_fear_greed(70) == 'greed'
    assert classify_fear_greed(90) == 'extreme greed'


def test_confirmed_fear_requires_market_confirmation_not_only_index():
    result = evaluate_fear_greed(
        index_value=12,
        btc_context={'trend': 'bearish', 'price_vs_vwap_pct': -3.0, 'rsi_14': 25, 'order_book_imbalance': -0.35, 'spread_bps': 3},
        eth_context={'trend': 'bearish', 'price_vs_vwap_pct': -2.0, 'rsi_14': 28, 'order_book_imbalance': -0.1, 'spread_bps': 4},
        breadth={'share_above_vwap': 0.2, 'median_24h_change': -4.5, 'risk_assets_outperform_btc': False},
    )
    assert result['label'] == 'extreme fear'
    assert result['confirmation'] == 'confirmed'
    assert result['score'] < 0
    assert any('btc below vwap' in x.lower() for x in result['evidence'])


def test_fake_fear_when_index_is_scared_but_market_structure_improves():
    result = evaluate_fear_greed(
        index_value=18,
        btc_context={'trend': 'bullish', 'price_vs_vwap_pct': 1.2, 'rsi_14': 52, 'order_book_imbalance': 0.45, 'spread_bps': 2},
        eth_context={'trend': 'bullish', 'price_vs_vwap_pct': 0.9, 'rsi_14': 50, 'order_book_imbalance': 0.25, 'spread_bps': 3},
        breadth={'share_above_vwap': 0.68, 'median_24h_change': 2.1, 'risk_assets_outperform_btc': True},
    )
    assert result['label'] == 'extreme fear'
    assert result['confirmation'] == 'contradicted'
    assert result['score'] > 0
    assert result['interpretation'].startswith('Index says fear, but')


def test_confirmed_greed_and_fake_greed():
    confirmed = evaluate_fear_greed(
        index_value=82,
        btc_context={'trend': 'bullish', 'price_vs_vwap_pct': 4.0, 'rsi_14': 76, 'order_book_imbalance': 0.3, 'spread_bps': 2},
        eth_context={'trend': 'bullish', 'price_vs_vwap_pct': 2.8, 'rsi_14': 72, 'order_book_imbalance': 0.2, 'spread_bps': 2},
        breadth={'share_above_vwap': 0.8, 'median_24h_change': 5.0, 'risk_assets_outperform_btc': True},
    )
    fake = evaluate_fear_greed(
        index_value=82,
        btc_context={'trend': 'bearish', 'price_vs_vwap_pct': -1.0, 'rsi_14': 48, 'order_book_imbalance': -0.2, 'spread_bps': 3},
        eth_context={'trend': 'mixed', 'price_vs_vwap_pct': -0.4, 'rsi_14': 45, 'order_book_imbalance': -0.1, 'spread_bps': 4},
        breadth={'share_above_vwap': 0.3, 'median_24h_change': -1.5, 'risk_assets_outperform_btc': False},
    )
    assert confirmed['confirmation'] == 'confirmed'
    assert fake['confirmation'] == 'contradicted'
    assert fake['score'] < confirmed['score']


def test_render_report_contains_no_buy_sell_language():
    result = evaluate_fear_greed(
        index_value=50,
        btc_context={'trend': 'mixed', 'price_vs_vwap_pct': 0, 'rsi_14': 50, 'order_book_imbalance': 0, 'spread_bps': 3},
        eth_context={'trend': 'mixed', 'price_vs_vwap_pct': 0, 'rsi_14': 50, 'order_book_imbalance': 0, 'spread_bps': 3},
        breadth={'share_above_vwap': 0.5, 'median_24h_change': 0, 'risk_assets_outperform_btc': False},
    )
    md = render_fear_greed_report(result)
    assert 'not financial advice' in md.lower()
    assert 'buy' not in md.lower()
    assert 'sell' not in md.lower()


if __name__ == '__main__':
    test_classify_fear_greed_thresholds()
    test_confirmed_fear_requires_market_confirmation_not_only_index()
    test_fake_fear_when_index_is_scared_but_market_structure_improves()
    test_confirmed_greed_and_fake_greed()
    test_render_report_contains_no_buy_sell_language()
    print('OK fear/greed confirmation tests passed')
