from analysis import PosetAnalyzer
from closure import lattice_layer_sizes
from families import antichain, chain, diamond


def test_lattice_layer_sizes_backend_matches_generated_lattice_layers():
    analyzer = PosetAnalyzer(diamond())

    layer_sizes_from_layers = [
        len(ideals)
        for _, ideals in sorted(analyzer.get_lattice_layers().items())
    ]

    assert analyzer.lattice_layer_sizes() == layer_sizes_from_layers


def test_lattice_layer_sizes_backend_matches_named_family_summaries():
    assert PosetAnalyzer(chain(3)).lattice_layer_sizes() == [1, 1, 1, 1]
    assert PosetAnalyzer(antichain(3)).lattice_layer_sizes() == [1, 3, 3, 1]
    assert PosetAnalyzer(diamond()).lattice_layer_sizes() == [1, 1, 2, 1, 1]


def test_lattice_layer_sizes_adapter_uses_rust_backend_when_available(monkeypatch):
    calls = []

    def fake_rust_backend(num_elements, cover_edges):
        calls.append((num_elements, cover_edges))
        return [1, 2, 1]

    monkeypatch.setattr("closure._rust_lattice_layer_sizes", fake_rust_backend)

    assert lattice_layer_sizes(2, [(0, 1)]) == [1, 2, 1]
    assert calls == [(2, [(0, 1)])]
