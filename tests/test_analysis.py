import pytest

from analysis import PosetAnalyzer
from families import antichain, asymmetric_convergence, chain, crown, diamond, n_poset
from ideal import Ideal 


@pytest.mark.parametrize(
    ("family", "expected_count"),
    [
        (chain(3), 1),
        (antichain(3), 6),
        (diamond(), 2),
        (n_poset(), 5),
    ],
)
def test_named_families_have_expected_linear_extension_counts(family, expected_count):
    analyzer = PosetAnalyzer(family)

    assert analyzer.count_linear_extensions() == expected_count


def test_diamond_lattice_layers():
    analyzer = PosetAnalyzer(diamond())

    layers = analyzer.get_lattice_layers()

    assert set(layers[0]) == {Ideal()}  # Empty set
    assert set(layers[1]) == {Ideal("A")}  # {A}
    assert set(layers[2]) == {Ideal({"A", "B"}), Ideal({"A", "C"})}  # {A,B}, {A,C}
    assert set(layers[3]) == {Ideal({"A", "B", "C"})}  # {A,B,C}
    assert set(layers[4]) == {Ideal({"A", "B", "C", "D"})}  # {A,B,C,D}


def test_diamond_summary_reports_structural_measurements():
    analyzer = PosetAnalyzer(diamond())

    assert analyzer.summary() == {
        "num_elements": 4,
        "num_relations": 4,
        "num_minimals": 1,
        "num_maximals": 1,
        "height": 3,
        "width": 2,
        "num_linear_extensions": 2,
        "num_ideals": 6,
        "lattice_layer_sizes": [1, 1, 2, 1, 1],
    }


def test_structural_summary_keeps_large_mobius_objects_explicit():
    summary = PosetAnalyzer(diamond()).summary()

    assert "mobius_matrix" not in summary
    assert "mobius_summary" not in summary
    assert "interval_summary" not in summary


def test_basic_family_heights():
    assert PosetAnalyzer(chain(4)).height() == 4
    assert PosetAnalyzer(antichain(4)).height() == 1


@pytest.mark.parametrize(
    ("family", "expected_width"),
    [
        (chain(4), 1),
        (antichain(4), 4),
        (diamond(), 2),
        (n_poset(), 2),
        (crown(3), 3),
        (asymmetric_convergence([1, 3]), 2),
    ],
)
def test_named_families_have_expected_widths(family, expected_width):
    assert PosetAnalyzer(family).width() == expected_width


def test_width_uses_transitive_comparability_not_only_cover_relations():
    analyzer = PosetAnalyzer(chain(3))

    assert analyzer.comparability_edges() == [
        ("x1", "x2"),
        ("x1", "x3"),
        ("x2", "x3"),
    ]
    assert analyzer.width() == 1


def test_comparable_successors_reuse_transitive_closure_cache():
    analyzer = PosetAnalyzer(chain(3))

    assert analyzer.comparable_successors("x1") == ["x2", "x3"]
    assert analyzer.comparable_successors("x1") == ["x2", "x3"]
    assert analyzer.is_less_equal("x1", "x3")


def test_chain_mobius_values_use_closed_intervals():
    analyzer = PosetAnalyzer(chain(3))

    assert analyzer.mobius("x1", "x1") == 1
    assert analyzer.mobius("x1", "x2") == -1
    assert analyzer.mobius("x2", "x3") == -1
    assert analyzer.mobius("x1", "x3") == 0
    assert analyzer.mobius("x3", "x1") == 0


def test_diamond_mobius_values_include_branch_reconvergence():
    analyzer = PosetAnalyzer(diamond())

    assert analyzer.interval("A", "D") == ["A", "B", "C", "D"]
    assert analyzer.mobius("A", "B") == -1
    assert analyzer.mobius("A", "C") == -1
    assert analyzer.mobius("B", "D") == -1
    assert analyzer.mobius("C", "D") == -1
    assert analyzer.mobius("A", "D") == 1
    assert analyzer.mobius("B", "C") == 0


def test_diamond_interval_summary_reports_compact_interval_features():
    summary = PosetAnalyzer(diamond()).interval_summary()

    assert summary == {
        "num_intervals": 9,
        "num_trivial_intervals": 4,
        "num_nontrivial_intervals": 5,
        "num_cover_intervals": 4,
        "min_interval_size": 1,
        "max_interval_size": 4,
        "mean_interval_size": pytest.approx(16 / 9),
        "interval_size_histogram": {1: 4, 2: 4, 4: 1},
    }


def test_mobius_matrix_reports_every_ordered_pair():
    matrix = PosetAnalyzer(chain(2)).mobius_matrix()

    assert matrix == {
        ("x1", "x1"): 1,
        ("x1", "x2"): -1,
        ("x2", "x1"): 0,
        ("x2", "x2"): 1,
    }


def test_mobius_summary_reports_compact_mobius_features():
    summary = PosetAnalyzer(diamond()).mobius_summary()

    assert summary == {
        "num_mobius_values": 9,
        "mobius_zero_count": 0,
        "mobius_nonzero_count": 9,
        "mobius_positive_count": 5,
        "mobius_negative_count": 4,
        "mobius_min": -1,
        "mobius_max": 1,
        "mobius_abs_sum": 9,
        "mobius_value_histogram": {-1: 4, 1: 5},
        "is_ranked": True,
        "mobius_value_histogram_by_rank_distance": {
            0: {1: 4},
            1: {-1: 4},
            2: {1: 1},
        },
    }


def test_mobius_summary_omits_rank_distance_histogram_for_non_ranked_posets():
    summary = PosetAnalyzer(asymmetric_convergence([1, 3])).mobius_summary()

    assert summary["is_ranked"] is False
    assert summary["mobius_value_histogram_by_rank_distance"] == {}


def test_zeta_transform_and_mobius_inversion_round_trip():
    analyzer = PosetAnalyzer(diamond())
    values = {"A": 2, "B": 3, "C": 5, "D": 7}

    transformed = analyzer.zeta_transform(values)

    assert transformed == {"A": 2, "B": 5, "C": 7, "D": 17}
    assert analyzer.mobius_inversion(transformed) == values


def test_mobius_transforms_require_values_for_all_elements():
    analyzer = PosetAnalyzer(diamond())

    with pytest.raises(KeyError):
        analyzer.zeta_transform({"A": 1})
