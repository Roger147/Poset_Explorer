from families import diamond
from intervals import IntervalConfig, WeightedIntervalAnalyzer
from weighted import WeightedPoset


def test_weighted_interval_analyzer_sums_configured_element_intervals():
    analyzer = WeightedIntervalAnalyzer(
        WeightedPoset(
            diamond(),
            element_weights={"A": 2, "B": 3, "C": 5, "D": 7},
        )
    )

    assert analyzer.element_sum("A", "D") == 17
    assert analyzer.element_sum("A", "D", IntervalConfig.open()) == 8
    assert analyzer.element_sum("A", "D", IntervalConfig.left_open()) == 15
    assert analyzer.element_sum("A", "D", IntervalConfig.right_open()) == 10


def test_weighted_interval_analyzer_returns_zero_for_incomparable_endpoints():
    analyzer = WeightedIntervalAnalyzer(
        WeightedPoset(
            diamond(),
            element_weights={"A": 2, "B": 3, "C": 5, "D": 7},
        )
    )

    assert analyzer.element_sum("B", "C") == 0
