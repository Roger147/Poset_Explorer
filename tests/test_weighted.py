import pytest

from families import antichain, chain, crown, diamond, n_poset
from ideal import Ideal
from weighted import WeightedPoset, WeightedPosetAnalyzer


def test_weighted_poset_stores_sparse_element_and_edge_weights():
    poset = diamond()
    weighted = WeightedPoset(
        poset,
        element_weights={"A": 2, "D": 5},
        edge_weights={("A", "B"): 1.5},
    )

    assert weighted.poset is poset
    assert weighted.element_weight("A") == 2
    assert weighted.element_weight("D") == 5
    assert weighted.edge_weight("A", "B") == 1.5

    with pytest.raises(KeyError):
        weighted.element_weight("B")

    with pytest.raises(KeyError):
        weighted.edge_weight("A", "C")


def test_element_function_generates_weights_in_canonical_order():
    weighted = WeightedPoset.from_element_function(
        chain(3),
        lambda element: int(element.removeprefix("x")),
    )

    assert weighted.element_weights == {"x1": 1, "x2": 2, "x3": 3}
    assert weighted.element_weight_vector() == [1, 2, 3]


def test_edge_function_generates_cover_edge_weights_in_canonical_order():
    weighted = WeightedPoset.from_edge_function(
        chain(3),
        lambda source, target: int(source.removeprefix("x")) + int(target.removeprefix("x")),
    )

    assert weighted.cover_edges() == [("x1", "x2"), ("x2", "x3")]
    assert weighted.edge_weights == {
        ("x1", "x2"): 3,
        ("x2", "x3"): 5,
    }
    assert weighted.edge_weight_vector() == [3, 5]


def test_reweighting_returns_new_wrapper_over_same_poset():
    poset = chain(2)
    weighted = WeightedPoset.from_element_function(poset, lambda element: 1)

    reweighted = weighted.with_element_weights(lambda element: 10)

    assert reweighted is not weighted
    assert reweighted.poset is poset
    assert weighted.element_weight_vector() == [1, 1]
    assert reweighted.element_weight_vector() == [10, 10]


def test_reweighting_copies_existing_weight_mappings():
    element_weights = {"x1": 1}
    edge_weights = {("x1", "x2"): 2}
    weighted = WeightedPoset(chain(2), element_weights, edge_weights)

    element_weights["x2"] = 99
    edge_weights[("x2", "x3")] = 99

    assert weighted.element_weights == {"x1": 1}
    assert weighted.edge_weights == {("x1", "x2"): 2}


def test_weighted_poset_rejects_unknown_element_and_edge_keys():
    poset = chain(2)

    with pytest.raises(KeyError):
        WeightedPoset(poset, element_weights={"missing": 1})

    with pytest.raises(KeyError):
        WeightedPoset(poset, edge_weights={("x1", "missing"): 1})

    with pytest.raises(KeyError):
        WeightedPoset(poset).edge_weight("x1", "missing")


def test_weighted_analyzer_max_chain_weight_defaults_to_element_weights():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 3, "B": 10, "C": 1, "D": 5},
        edge_weights={
            ("A", "B"): 100,
            ("A", "C"): 1,
            ("B", "D"): 1,
            ("C", "D"): 100,
        },
    )

    analyzer = WeightedPosetAnalyzer(weighted)

    assert analyzer.max_chain_weight() == 18


def test_weighted_analyzer_max_chain_weight_supports_edge_and_combined_modes():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 3, "B": 10, "C": 1, "D": 5},
        edge_weights={
            ("A", "B"): 100,
            ("A", "C"): 1,
            ("B", "D"): 1,
            ("C", "D"): 100,
        },
    )

    analyzer = WeightedPosetAnalyzer(weighted)

    assert analyzer.max_chain_weight(mode="edges") == 101
    assert analyzer.max_chain_weight(mode="both") == 119


def test_weighted_analyzer_rejects_unknown_chain_weight_mode():
    analyzer = WeightedPosetAnalyzer(WeightedPoset.from_element_function(chain(1), lambda element: 1))

    with pytest.raises(ValueError):
        analyzer.max_chain_weight(mode="unknown")


def test_max_chain_weight_rejects_negative_measurement_weights():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 3, "B": -10, "C": 1, "D": 5},
        edge_weights={
            ("A", "B"): 100,
            ("A", "C"): 1,
            ("B", "D"): 1,
            ("C", "D"): 100,
        },
    )

    with pytest.raises(ValueError):
        WeightedPosetAnalyzer(weighted).max_chain_weight()


def test_max_chain_score_allows_negative_weights():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 3, "B": -10, "C": 1, "D": 5},
        edge_weights={
            ("A", "B"): -100,
            ("A", "C"): 1,
            ("B", "D"): 1,
            ("C", "D"): 100,
        },
    )

    analyzer = WeightedPosetAnalyzer(weighted)

    assert analyzer.max_chain_score() == 9
    assert analyzer.max_chain_score(mode="edges") == 101
    assert analyzer.max_chain_score(mode="both") == 110


def test_max_chain_score_uses_nonempty_chain_when_elements_are_negative():
    weighted = WeightedPoset(
        chain(2),
        element_weights={"x1": -5, "x2": -1},
    )

    assert WeightedPosetAnalyzer(weighted).max_chain_score() == -1


@pytest.mark.parametrize(
    ("poset", "expected_width"),
    [
        (chain(4), 1),
        (antichain(4), 4),
        (diamond(), 2),
        (n_poset(), 2),
        (crown(3), 3),
    ],
)
def test_weighted_width_with_unit_weights_matches_structural_width(poset, expected_width):
    weighted = WeightedPoset.from_element_function(poset, lambda element: 1)

    assert WeightedPosetAnalyzer(weighted).weighted_width() == expected_width


def test_weighted_width_returns_maximum_antichain_element_weight():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 1, "B": 10, "C": 20, "D": 1},
    )

    assert WeightedPosetAnalyzer(weighted).weighted_width() == 30


def test_weighted_width_uses_transitive_comparability():
    weighted = WeightedPoset(
        chain(3),
        element_weights={"x1": 100, "x2": 1, "x3": 100},
    )

    assert WeightedPosetAnalyzer(weighted).weighted_width() == 100


def test_weighted_width_ignores_edge_weights():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 1, "B": 10, "C": 20, "D": 1},
        edge_weights={
            ("A", "B"): 1000,
            ("A", "C"): 1000,
            ("B", "D"): 1000,
            ("C", "D"): 1000,
        },
    )

    assert WeightedPosetAnalyzer(weighted).weighted_width() == 30


def test_weighted_width_rejects_negative_element_weights():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 1, "B": -1, "C": 2, "D": 1},
    )

    with pytest.raises(ValueError):
        WeightedPosetAnalyzer(weighted).weighted_width()


def test_max_antichain_score_allows_negative_element_scores():
    weighted = WeightedPoset(
        antichain(3),
        element_weights={"x1": 10, "x2": -100, "x3": 10},
    )

    assert WeightedPosetAnalyzer(weighted).max_antichain_score() == 20


def test_max_antichain_score_allows_empty_antichain():
    weighted = WeightedPoset(
        antichain(2),
        element_weights={"x1": -10, "x2": -5},
    )

    assert WeightedPosetAnalyzer(weighted).max_antichain_score() == 0


def test_weighted_analyzer_reuses_base_lattice_layers_for_ideal_weights():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 1, "B": 2, "C": 4, "D": 8},
    )

    analyzer = WeightedPosetAnalyzer(weighted)
    layers = analyzer.get_lattice_layers()

    assert layers is analyzer.get_lattice_layers()
    assert analyzer.ideal_weight(Ideal({"A", "C"})) == 5
    assert analyzer.weighted_lattice_layer_summary() == {
        0: {
            "num_ideals": 1,
            "min_ideal_weight": 0,
            "max_ideal_weight": 0,
            "mean_ideal_weight": 0,
            "ideal_weight_histogram": {0: 1},
        },
        1: {
            "num_ideals": 1,
            "min_ideal_weight": 1,
            "max_ideal_weight": 1,
            "mean_ideal_weight": 1,
            "ideal_weight_histogram": {1: 1},
        },
        2: {
            "num_ideals": 2,
            "min_ideal_weight": 3,
            "max_ideal_weight": 5,
            "mean_ideal_weight": 4,
            "ideal_weight_histogram": {3: 1, 5: 1},
        },
        3: {
            "num_ideals": 1,
            "min_ideal_weight": 7,
            "max_ideal_weight": 7,
            "mean_ideal_weight": 7,
            "ideal_weight_histogram": {7: 1},
        },
        4: {
            "num_ideals": 1,
            "min_ideal_weight": 15,
            "max_ideal_weight": 15,
            "mean_ideal_weight": 15,
            "ideal_weight_histogram": {15: 1},
        },
    }


def test_ideal_weight_rejects_negative_measurement_weights():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 1, "B": -2, "C": 4, "D": 8},
    )

    with pytest.raises(ValueError):
        WeightedPosetAnalyzer(weighted).ideal_weight(Ideal({"A", "B"}))


def test_ideal_score_and_layer_score_summary_allow_negative_values():
    weighted = WeightedPoset(
        diamond(),
        element_weights={"A": 1, "B": -2, "C": 4, "D": 8},
    )

    analyzer = WeightedPosetAnalyzer(weighted)

    assert analyzer.ideal_score(Ideal({"A", "B"})) == -1
    assert analyzer.weighted_lattice_layer_score_summary()[2] == {
        "num_ideals": 2,
        "min_ideal_score": -1,
        "max_ideal_score": 5,
        "mean_ideal_score": 2,
        "ideal_score_histogram": {-1: 1, 5: 1},
    }
