#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.forecast_outcomes import classify_forecast_outcome, outcome_badge


def test_outcome_badges_are_canonical_and_color_coded():
    cases = {
        None: ('pending', 'warn'),
        'target': ('target', 'good'),
        'stopped': ('stopped', 'bad'),
        'timeout': ('timeout', 'warn'),
        'failed': ('failed', 'bad'),
    }
    for raw, expected in cases.items():
        badge = outcome_badge(raw, correct_direction=None)
        assert (badge['key'], badge['class']) == expected
        assert badge['label']
        assert badge['color'].startswith('#')


def test_correct_direction_overrides_display_for_direction_result():
    good = outcome_badge('timeout', correct_direction=1)
    bad = outcome_badge('timeout', correct_direction=0)
    assert good['display_status'] == 'direction_correct'
    assert good['class'] == 'good'
    assert bad['display_status'] == 'direction_wrong'
    assert bad['class'] == 'bad'


def test_classify_forecast_outcome_extracts_result_context():
    outcome = classify_forecast_outcome({'verified_outcome': 'target', 'correct_direction': 1, 'result_json': '{"actual_direction":"up","bars_held":3}'})
    assert outcome['badge']['key'] == 'target'
    assert outcome['actual_direction'] == 'up'
    assert outcome['bars_held'] == 3


if __name__ == '__main__':
    test_outcome_badges_are_canonical_and_color_coded()
    test_correct_direction_overrides_display_for_direction_result()
    test_classify_forecast_outcome_extracts_result_context()
    print('OK forecast outcome tests passed')
