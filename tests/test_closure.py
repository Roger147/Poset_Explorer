import closure

from closure import (
    interval_summary_data,
    principal_ideal_filter_sizes,
    transitive_successor_closure,
    zeta_summary_data,
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
