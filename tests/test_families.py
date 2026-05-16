import pytest

from families import antichain, asymmetric_convergence, chain, crown, diamond, n_poset


def test_chain_factory_builds_cover_relations():
    poset = chain(4)

    assert poset.elements == {"x1", "x2", "x3", "x4"}
    assert poset.children_of("x1") == ["x2"]
    assert poset.parents_of("x4") == ["x3"]
    assert poset.minimals() == ["x1"]
    assert poset.maximals() == ["x4"]


def test_antichain_factory_has_no_relations():
    poset = antichain(3)

    assert poset.elements == {"x1", "x2", "x3"}
    assert all(poset.children_of(x) == [] for x in poset.elements)
    assert all(poset.parents_of(x) == [] for x in poset.elements)


def test_diamond_factory_builds_fork_join_shape():
    poset = diamond()

    assert poset.minimals() == ["A"]
    assert poset.maximals() == ["D"]
    assert poset.children_of("A") == ["B", "C"]
    assert poset.parents_of("D") == ["B", "C"]


def test_n_poset_factory_builds_asymmetric_overlap():
    poset = n_poset()

    assert poset.minimals() == ["A", "C"]
    assert poset.maximals() == ["B", "D"]
    assert poset.parents_of("B") == ["A", "C"]
    assert poset.children_of("C") == ["B", "D"]


def test_asymmetric_convergence_factory_builds_unequal_chains_into_z():
    poset = asymmetric_convergence([1, 3])

    assert poset.minimals() == ["c1_1", "c2_1"]
    assert poset.maximals() == ["z"]
    assert poset.parents_of("z") == ["c1_1", "c2_3"]
    assert poset.children_of("c2_1") == ["c2_2"]
    assert poset.children_of("c2_3") == ["z"]


@pytest.mark.parametrize("lengths", [[], [2], [0, 1], [2, 2]])
def test_asymmetric_convergence_rejects_non_family_parameters(lengths):
    with pytest.raises(ValueError):
        asymmetric_convergence(lengths)


def test_crown_factory_builds_height_two_exclusion_pattern():
    poset = crown(3)

    assert poset.minimals() == ["b1", "b2", "b3"]
    assert set(poset.maximals()) == {"a1", "a2", "a3"}
    assert poset.parents_of("a1") == ["b2", "b3"]
    assert poset.parents_of("a2") == ["b1", "b3"]
    assert poset.parents_of("a3") == ["b1", "b2"]


def test_crown_rejects_too_few_pairs():
    with pytest.raises(ValueError):
        crown(2)
