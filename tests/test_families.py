import pytest

from families import (
    antichain,
    boolean_lattice,
    chain,
    crown,
    diamond,
    n_poset,
    partition_lattice,
)


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


def test_boolean_lattice_factory_builds_subset_cover_relations():
    poset = boolean_lattice(2)

    assert poset.elements == {"{}", "{1}", "{2}", "{1, 2}"}
    assert poset.minimals() == ["{}"]
    assert poset.maximals() == ["{1, 2}"]
    assert set(poset.children_of("{}")) == {"{1}", "{2}"}
    assert poset.parents_of("{1, 2}") == ["{1}", "{2}"]


def test_boolean_lattice_rank_zero_has_single_empty_subset():
    poset = boolean_lattice(0)

    assert poset.elements == {"{}"}
    assert poset.minimals() == ["{}"]
    assert poset.maximals() == ["{}"]


def test_boolean_lattice_rejects_negative_rank():
    with pytest.raises(ValueError):
        boolean_lattice(-1)


def test_partition_lattice_rank_three_builds_refinement_covers():
    poset = partition_lattice(3)

    bottom = "{1}|{2}|{3}"
    top = "{1, 2, 3}"
    middles = {"{1, 2}|{3}", "{1, 3}|{2}", "{1}|{2, 3}"}

    assert len(poset.elements) == 5
    assert poset.minimals() == [bottom]
    assert poset.maximals() == [top]
    assert set(poset.children_of(bottom)) == middles
    assert all(poset.children_of(middle) == [top] for middle in middles)
    assert poset.parents_of(top) == ["{1, 2}|{3}", "{1, 3}|{2}", "{1}|{2, 3}"]


@pytest.mark.parametrize(
    ("rank", "expected_count"),
    [
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 5),
        (4, 15),
    ],
)
def test_partition_lattice_has_bell_number_element_counts(rank, expected_count):
    assert len(partition_lattice(rank).elements) == expected_count


def test_partition_lattice_rank_zero_has_single_empty_partition():
    poset = partition_lattice(0)

    assert poset.elements == {"{}"}
    assert poset.minimals() == ["{}"]
    assert poset.maximals() == ["{}"]


def test_partition_lattice_rejects_negative_rank():
    with pytest.raises(ValueError):
        partition_lattice(-1)
