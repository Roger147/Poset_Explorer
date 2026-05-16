import pytest

from enumeration import PosetAnalyzer
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
