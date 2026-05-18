from analysis import PosetAnalyzer
from families import boolean_lattice
from ideal import Ideal


def test_example_boolean_lattice_analysis_usage():
    poset = boolean_lattice(2)
    analyzer = PosetAnalyzer(poset)

    summary = analyzer.summary()
    mobius_matrix = analyzer.mobius_matrix()
    interval = analyzer.interval("{}", "{1, 2}")
    interval_summary = analyzer.interval_summary()
    mobius_summary = analyzer.mobius_summary()
    values = {"{}": 1, "{1}": 2, "{2}": 3, "{1, 2}": 5}
    zeta_values = analyzer.zeta_transform(values)

    assert poset.minimals() == ["{}"]
    assert poset.maximals() == ["{1, 2}"]
    assert poset.repr_ideal(Ideal({"{}", "{1}"})) == "ideal({}, {1})"
    assert analyzer.num_elements() == 4
    assert analyzer.num_relations() == 4
    assert analyzer.num_minimals() == 1
    assert analyzer.num_maximals() == 1
    assert analyzer.height() == 3
    assert analyzer.width() == 2
    assert analyzer.count_linear_extensions() == 2
    assert analyzer.num_ideals() == 6
    assert analyzer.lattice_layer_sizes() == [1, 1, 2, 1, 1]
    assert analyzer.comparable_successors("{}") == ["{1}", "{2}", "{1, 2}"]
    assert analyzer.comparability_edges() == [
        ("{}", "{1}"),
        ("{}", "{2}"),
        ("{}", "{1, 2}"),
        ("{1}", "{1, 2}"),
        ("{2}", "{1, 2}"),
    ]
    assert analyzer.is_less_equal("{}", "{1, 2}")
    assert interval == ["{}", "{1}", "{2}", "{1, 2}"]
    assert analyzer.mobius("{}", "{1, 2}") == 1
    assert zeta_values == {"{}": 1, "{1}": 3, "{2}": 4, "{1, 2}": 11}
    assert analyzer.mobius_inversion(zeta_values) == values
    assert analyzer.get_lattice_layers() == {
        0: [Ideal()],
        1: [Ideal({"{}"})],
        2: [Ideal({"{}", "{1}"}), Ideal({"{}", "{2}"})],
        3: [Ideal({"{}", "{1}", "{2}"})],
        4: [Ideal({"{}", "{1}", "{2}", "{1, 2}"})],
    }
    assert summary == {
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
    assert interval_summary == {
        "num_intervals": 9,
        "num_trivial_intervals": 4,
        "num_nontrivial_intervals": 5,
        "num_cover_intervals": 4,
        "min_interval_size": 1,
        "max_interval_size": 4,
        "mean_interval_size": 16 / 9,
        "interval_size_histogram": {1: 4, 2: 4, 4: 1},
    }
    assert mobius_summary == {
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
    assert mobius_matrix == {
        ("{}", "{}"): 1,
        ("{}", "{1}"): -1,
        ("{}", "{2}"): -1,
        ("{}", "{1, 2}"): 1,
        ("{1}", "{}"): 0,
        ("{1}", "{1}"): 1,
        ("{1}", "{2}"): 0,
        ("{1}", "{1, 2}"): -1,
        ("{2}", "{}"): 0,
        ("{2}", "{1}"): 0,
        ("{2}", "{2}"): 1,
        ("{2}", "{1, 2}"): -1,
        ("{1, 2}", "{}"): 0,
        ("{1, 2}", "{1}"): 0,
        ("{1, 2}", "{2}"): 0,
        ("{1, 2}", "{1, 2}"): 1,
    }
