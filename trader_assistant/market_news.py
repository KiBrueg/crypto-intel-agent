from __future__ import annotations

import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

DEFAULT_RSS_FEEDS = [
    ('Federal Reserve', 'https://www.federalreserve.gov/feeds/press_all.xml'),
    ('Reuters Business', 'https://feeds.reuters.com/reuters/businessNews'),
    ('CoinDesk', 'https://www.coindesk.com/arc/outboundfeeds/rss/'),
]

BULLISH_KEYWORDS = {
    'liquidity': ['rate cut', 'cuts rates', 'lower rates', 'dovish', 'easing', 'qe', 'stimulus', 'cooling inflation', 'soft landing'],
    'crypto_adoption': ['bitcoin etf', 'spot bitcoin etf', 'ethereum etf', 'inflows', 'adoption', 'regulation bill passes', 'clear rules', 'approval'],
    'risk_on': ['ceasefire', 'peace talks', 'de-escalation', 'growth rebounds', 'risk-on'],
}

BEARISH_KEYWORDS = {
    'rates': ['rate hike', 'higher for longer', 'hawkish', 'tightening', 'yields rise', 'bond yields rise'],
    'inflation': ['hot inflation', 'inflation accelerates', 'cpi hotter', 'ppi hotter'],
    'geopolitical': ['war escalation', 'missile strike', 'invasion', 'sanctions', 'blocked', 'shipping route blocked', 'oil shipping', 'red sea', 'strait', 'pipeline shut'],
    'crypto_risk': ['hack', 'exploit', 'lawsuit', 'sec sues', 'exchange collapse', 'outflows', 'ban crypto', 'restrict crypto'],
    'risk_off': ['recession fears', 'bank crisis', 'default risk', 'risk-off'],
}


def _text(item):
    return ' '.join(str(item.get(k, '') or '') for k in ('title', 'summary', 'description')).lower()


def _hits(text, mapping):
    drivers = []
    phrases = []
    for driver, words in mapping.items():
        for w in words:
            if w in text:
                drivers.append(driver)
                phrases.append(w)
                break
    return drivers, phrases


def classify_news_event(item):
    text = _text(item)
    bull_drivers, bull_phrases = _hits(text, BULLISH_KEYWORDS)
    bear_drivers, bear_phrases = _hits(text, BEARISH_KEYWORDS)
    score = len(bull_drivers) - len(bear_drivers)
    # macro/geopolitical shocks deserve extra weight because they can dominate crypto-native news
    if 'geopolitical' in bear_drivers:
        score -= 1
    if 'rates' in bear_drivers and 'inflation' in bear_drivers:
        score -= 1
    if 'liquidity' in bull_drivers and 'crypto_adoption' in bull_drivers:
        score += 1
    bias = 'neutral'
    if score > 0:
        bias = 'bullish'
    elif score < 0:
        bias = 'bearish'
    return {
        'title': item.get('title', ''),
        'source': item.get('source', ''),
        'url': item.get('url', ''),
        'published': item.get('published', ''),
        'bias': bias,
        'impact_score': score,
        'drivers': sorted(set(bull_drivers + bear_drivers)),
        'matched_phrases': bull_phrases + bear_phrases,
    }


def score_news_items(items):
    scored = [classify_news_event(i) for i in items]
    total = sum(i['impact_score'] for i in scored)
    bull = [i for i in scored if i['impact_score'] > 0]
    bear = [i for i in scored if i['impact_score'] < 0]
    if total > 1:
        net_bias = 'bullish'
        pressure = 'greed_up'
    elif total < -1:
        net_bias = 'bearish'
        pressure = 'fear_up'
    else:
        net_bias = 'mixed'
        pressure = 'mixed'
    scenarios = {
        'bullish': {
            'thesis': 'Liquidity/adoption/risk-on news dominates if bullish drivers persist.',
            'market_effect': 'Potential upside pressure on BTC/ETH and lower fear if confirmed by price reclaiming VWAP/levels.',
            'watch': [i['title'] for i in bull[:3]],
        },
        'base': {
            'thesis': 'Mixed news should be treated as context, not a signal; price structure decides.',
            'market_effect': 'Expect chop until macro/news impulse aligns with technical confirmation.',
            'watch': [i['title'] for i in scored[:3]],
        },
        'bearish': {
            'thesis': 'Hawkish rates, inflation, war/oil/logistics or crypto enforcement shocks dominate if bearish drivers persist.',
            'market_effect': 'Potential downside/risk-off pressure and fear increase, especially if BTC loses key levels.',
            'watch': [i['title'] for i in bear[:3]],
        },
    }
    return {
        'mode': 'market_news_impact',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'items_scored': len(scored),
        'net_score': total,
        'net_bias': net_bias,
        'fear_greed_pressure': pressure,
        'scored_items': scored,
        'scenarios': scenarios,
        'global_impact': build_global_news_impact(items),
    }


GLOBAL_NEWS_CATEGORIES = {
    'war_conflict': ['war', 'invasion', 'missile', 'strike', 'ceasefire', 'peace deal', 'peace talks', 'escalation', 'de-escalation', 'red sea', 'strait'],
    'sanctions_bans': ['sanction', 'sanctions', 'ban', 'banned', 'blocked', 'restrict', 'restrictions', 'export control', 'blacklist'],
    'regulation_policy': ['regulator', 'sec', 'cftc', 'law', 'bill', 'rules', 'approval', 'etf', 'tax', 'compliance'],
    'leaders_billionaires': ['president', 'minister', 'central bank', 'powell', 'trump', 'biden', 'putin', 'xi ', 'musk', 'billionaire', 'ceo', 'blackrock'],
    'energy_oil': ['oil', 'gas', 'pipeline', 'opec', 'energy', 'shipping route'],
    'macro_rates': ['fed', 'rates', 'rate cut', 'rate hike', 'inflation', 'cpi', 'ppi', 'yields', 'recession'],
}


def _global_categories(text):
    hits = []
    for category, words in GLOBAL_NEWS_CATEGORIES.items():
        if any(w in text for w in words):
            hits.append(category)
    return hits or ['general_market']


def _effect_from_score(score):
    if score > 0:
        return 'growth_pressure'
    if score < 0:
        return 'fall_pressure'
    return 'mixed'


def build_global_news_impact(items):
    cards = []
    category_counts = {}
    crypto_score = 0
    stocks_score = 0
    for item in items:
        classified = classify_news_event(item)
        text = _text(item)
        cats = _global_categories(text)
        for c in cats:
            category_counts[c] = category_counts.get(c, 0) + 1
        score = classified['impact_score']
        crypto_score += score
        stock_delta = score
        if 'crypto_risk' in classified.get('drivers', []) or 'crypto' in text or 'bitcoin' in text or 'ethereum' in text:
            stock_delta = 0 if score < 0 else max(0, score - 1)
        if any(c in cats for c in ('war_conflict', 'sanctions_bans', 'energy_oil', 'macro_rates')):
            stock_delta += -1 if score < 0 else (1 if score > 0 else 0)
        stocks_score += stock_delta
        if score or any(c != 'general_market' for c in cats):
            cards.append({
                'title': item.get('title', ''),
                'source': item.get('source', ''),
                'url': item.get('url', ''),
                'categories': cats,
                'crypto_effect': _effect_from_score(score),
                'stocks_effect': _effect_from_score(stock_delta),
                'impact_score': score,
                'why': _global_why(cats, classified),
            })
    crypto_bias = 'bullish' if crypto_score > 1 else ('bearish' if crypto_score < -1 else 'mixed')
    stocks_bias = 'bullish' if stocks_score > 1 else ('bearish' if stocks_score < -1 else 'mixed')
    headline = f'Crypto: {crypto_bias}; Stocks: {stocks_bias}; key risks: ' + (', '.join(sorted(category_counts)[:4]) if category_counts else 'no high-impact global driver')
    return {
        'mode': 'global_news_impact',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'headline': headline,
        'crypto_bias': crypto_bias,
        'stocks_bias': stocks_bias,
        'crypto_score': crypto_score,
        'stocks_score': stocks_score,
        'category_counts': category_counts,
        'cards': cards[:10],
        'what_to_watch': [
            'BTC/ETH reaction at VWAP and key support/resistance after headline shock.',
            'S&P/Nasdaq futures and DXY/yields for risk-on vs risk-off confirmation.',
            'Oil/gas spikes if war, sanctions or shipping routes are involved.',
            'Follow-up statements from regulators, presidents, central banks, major CEOs/billionaires.',
        ],
    }


def _global_why(categories, classified):
    cat_text = ', '.join(categories)
    drivers = ', '.join(classified.get('drivers') or ['headline context'])
    if classified['impact_score'] > 0:
        return f'Potential risk-on/growth pressure: {drivers}; categories: {cat_text}.'
    if classified['impact_score'] < 0:
        return f'Potential risk-off/fall pressure: {drivers}; categories: {cat_text}.'
    return f'Mixed/unclear until price confirms; categories: {cat_text}.'


def fetch_rss_items(feeds=DEFAULT_RSS_FEEDS, limit_per_feed=8, timeout=8):
    items = []
    for source, url in feeds:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'crypto-intel-agent/0.1'})
            data = urllib.request.urlopen(req, timeout=timeout).read()
            root = ET.fromstring(data)
            # RSS item or Atom entry support
            entries = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            for e in entries[:int(limit_per_feed)]:
                title = (e.findtext('title') or e.findtext('{http://www.w3.org/2005/Atom}title') or '').strip()
                link = (e.findtext('link') or '').strip()
                if not link:
                    link_el = e.find('{http://www.w3.org/2005/Atom}link')
                    link = link_el.get('href', '') if link_el is not None else ''
                summary = (e.findtext('description') or e.findtext('summary') or e.findtext('{http://www.w3.org/2005/Atom}summary') or '').strip()
                published = (e.findtext('pubDate') or e.findtext('published') or e.findtext('{http://www.w3.org/2005/Atom}published') or '').strip()
                if title:
                    items.append({'source': source, 'title': re.sub('<[^>]+>', '', title), 'summary': re.sub('<[^>]+>', '', summary), 'url': link, 'published': published})
        except Exception as exc:
            items.append({'source': source, 'title': f'RSS fetch failed: {source}', 'summary': str(exc), 'url': url, 'published': ''})
    return items
