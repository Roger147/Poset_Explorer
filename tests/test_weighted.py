import pytest

from families import chain, diamond
from weighted import WeightedPoset


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
