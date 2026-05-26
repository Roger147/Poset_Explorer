import closure

from closure import transitive_successor_closure


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
