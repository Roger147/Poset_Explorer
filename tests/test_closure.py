import closure

from closure import (
    interval_summary_data,
    linear_extension_count_data,
    mobius_matrix_data,
    principal_ideal_filter_sizes,
    strict_zeta_transform_data,
    transitive_successor_closure,
    width_data,
    zeta_summary_data,
    zeta_transform_data,
)


def test_transitive_successor_closure_uses_indexed_cover_edges():
    closure = transitive_successor_closure(
        4,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
    )

    assert closure == [
        {1, 2, 3},
        {3},
        {3},
        set(),
    ]


def test_transitive_successor_closure_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges):
        calls.append((num_elements, cover_edges))
        return [[1, 2], [2], []]

    monkeypatch.setattr(
        closure,
        "_rust_transitive_successor_closure",
        fake_rust_backend,
    )

    result = transitive_successor_closure(3, [(0, 1), (1, 2)])

    assert calls == [(3, [(0, 1), (1, 2)])]
    assert result == [{1, 2}, {2}, set()]


def test_principal_ideal_filter_sizes_reports_reflexive_counts():
    assert principal_ideal_filter_sizes(
        4,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
    ) == ([1, 2, 2, 4], [4, 2, 2, 1])


def test_principal_ideal_filter_sizes_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges):
        calls.append((num_elements, cover_edges))
        return [1, 2, 3], [3, 2, 1]

    monkeypatch.setattr(
        closure,
        "_rust_principal_ideal_filter_sizes",
        fake_rust_backend,
    )

    result = principal_ideal_filter_sizes(3, [(0, 1), (1, 2)])

    assert calls == [(3, [(0, 1), (1, 2)])]
    assert result == ([1, 2, 3], [3, 2, 1])


def test_zeta_summary_data_reports_strict_count_and_principal_sizes():
    assert zeta_summary_data(
        4,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
    ) == (5, [1, 2, 2, 4], [4, 2, 2, 1])


def test_zeta_summary_data_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges):
        calls.append((num_elements, cover_edges))
        return 2, [1, 2, 3], [3, 2, 1]

    monkeypatch.setattr(
        closure,
        "_rust_zeta_summary_data",
        fake_rust_backend,
    )

    result = zeta_summary_data(3, [(0, 1), (1, 2)])

    assert calls == [(3, [(0, 1), (1, 2)])]
    assert result == (2, [1, 2, 3], [3, 2, 1])


def test_zeta_transform_data_reports_float_principal_ideal_totals():
    assert zeta_transform_data(
        4,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
        [2, 3, 5, 7],
    ) == [2.0, 5.0, 7.0, 17.0]


def test_zeta_transform_data_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges, values):
        calls.append((num_elements, cover_edges, values))
        return [1.0, 3.0]

    monkeypatch.setattr(
        closure,
        "_rust_zeta_transform_data",
        fake_rust_backend,
    )

    result = zeta_transform_data(2, [(0, 1)], [1, 2])

    assert calls == [(2, [(0, 1)], [1.0, 2.0])]
    assert result == [1.0, 3.0]


def test_strict_zeta_transform_data_reports_float_strict_totals():
    assert strict_zeta_transform_data(
        4,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
        [2, 3, 5, 7],
    ) == [0.0, 2.0, 2.0, 10.0]


def test_strict_zeta_transform_data_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges, values):
        calls.append((num_elements, cover_edges, values))
        return [0.0, 1.0]

    monkeypatch.setattr(
        closure,
        "_rust_strict_zeta_transform_data",
        fake_rust_backend,
    )

    result = strict_zeta_transform_data(2, [(0, 1)], [1, 2])

    assert calls == [(2, [(0, 1)], [1.0, 2.0])]
    assert result == [0.0, 1.0]


def test_width_data_uses_transitive_comparability_matching():
    assert width_data(4, [(0, 1), (1, 2), (2, 3)]) == 1
    assert width_data(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) == 2
    assert width_data(4, []) == 4


def test_width_data_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges):
        calls.append((num_elements, cover_edges))
        return 2

    monkeypatch.setattr(
        closure,
        "_rust_width_data",
        fake_rust_backend,
    )

    result = width_data(3, [(0, 1), (1, 2)])

    assert calls == [(3, [(0, 1), (1, 2)])]
    assert result == 2


def test_linear_extension_count_data_counts_indexed_extensions():
    assert linear_extension_count_data(4, [(0, 1), (1, 2), (2, 3)]) == 1
    assert linear_extension_count_data(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) == 2
    assert linear_extension_count_data(4, []) == 24


def test_linear_extension_count_data_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges, max_states):
        calls.append((num_elements, cover_edges, max_states))
        return 5

    monkeypatch.setattr(
        closure,
        "_rust_linear_extension_count_data",
        fake_rust_backend,
    )

    result = linear_extension_count_data(3, [(0, 1), (1, 2)])

    assert calls == [(3, [(0, 1), (1, 2)], 1_000_000)]
    assert result == 5


def test_linear_extension_count_data_uses_configurable_state_limit():
    try:
        linear_extension_count_data(4, [], max_states=2)
    except ValueError as error:
        assert "state limit" in str(error)
    else:
        raise AssertionError("expected ValueError")

    assert linear_extension_count_data(4, [], max_states=None) == 24


def test_linear_extension_count_data_rejects_more_than_u128_bitmask_capacity():
    try:
        linear_extension_count_data(129, [])
    except ValueError as error:
        assert "at most 128 elements" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_interval_summary_data_reports_closed_interval_features():
    assert interval_summary_data(
        4,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
    ) == {
        "num_intervals": 9,
        "num_trivial_intervals": 4,
        "num_nontrivial_intervals": 5,
        "num_cover_intervals": 4,
        "min_interval_size": 1,
        "max_interval_size": 4,
        "mean_interval_size": 16 / 9,
        "interval_size_histogram": {1: 4, 2: 4, 4: 1},
    }


def test_interval_summary_data_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges):
        calls.append((num_elements, cover_edges))
        return 2, 1, 1, 1, 1, 2, 1.5, [(1, 1), (2, 1)]

    monkeypatch.setattr(
        closure,
        "_rust_interval_summary_data",
        fake_rust_backend,
    )

    result = interval_summary_data(2, [(0, 1)])

    assert calls == [(2, [(0, 1)])]
    assert result == {
        "num_intervals": 2,
        "num_trivial_intervals": 1,
        "num_nontrivial_intervals": 1,
        "num_cover_intervals": 1,
        "min_interval_size": 1,
        "max_interval_size": 2,
        "mean_interval_size": 1.5,
        "interval_size_histogram": {1: 1, 2: 1},
    }


def test_mobius_matrix_data_reports_indexed_incidence_inverse():
    assert mobius_matrix_data(
        4,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
    ) == [
        [1, -1, -1, 1],
        [0, 1, 0, -1],
        [0, 0, 1, -1],
        [0, 0, 0, 1],
    ]


def test_mobius_matrix_data_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges):
        calls.append((num_elements, cover_edges))
        return [[1, -1], [0, 1]]

    monkeypatch.setattr(
        closure,
        "_rust_mobius_matrix_data",
        fake_rust_backend,
    )

    result = mobius_matrix_data(2, [(0, 1)])

    assert calls == [(2, [(0, 1)])]
    assert result == [[1, -1], [0, 1]]
