import pytest

from families import diamond
from poset import Poset


def test_diamond_structure_and_minimals():
    poset = diamond()

    assert poset.adj["A"] == {"B", "C"}
    assert poset.parents["D"] == {"B", "C"}
    assert poset.global_in_degree["A"] == 0
    assert poset.global_in_degree["D"] == 2

    subset = frozenset({"A", "B", "C", "D"})

    minimal = poset.minimals_in_subposet(subset)

    assert set(minimal) == {"A"}

    subsetup = frozenset({"B", "C", "D"})

    minimal = poset.minimals_in_subposet(subsetup)

    assert set(minimal) == {"B", "C"}


def test_parent_and_child_accessors_use_canonical_order():
    elements = {"M", "Z", "A", "B"}

    relations = [
        ("M", "A"),
        ("M", "B"),
        ("Z", "A"),
    ]

    poset = Poset(elements, relations)

    assert poset.order == ["M", "B", "Z", "A"]
    assert poset.children_of("M") == ["B", "A"]
    assert poset.parents_of("A") == ["M", "Z"]
    assert poset.indexed_relations() == [(0, 1), (0, 3), (2, 3)]


def test_element_index_maps_follow_canonical_order():
    poset = Poset(
        {"task: build", "{1}|{2}", "deploy"},
        [
            ("task: build", "deploy"),
            ("{1}|{2}", "deploy"),
        ],
    )

    assert poset.index_to_element == ["task: build", "{1}|{2}", "deploy"]
    assert poset.element_to_index == {
        "task: build": 0,
        "{1}|{2}": 1,
        "deploy": 2,
    }


def test_duplicate_relations_are_normalized_with_warning():
    with pytest.warns(
        UserWarning,
        match="Removed 2 duplicate relation.*relations are set-valued",
    ):
        poset = Poset(
            {"A", "B", "C"},
            [
                ("A", "B"),
                ("A", "B"),
                ("B", "C"),
                ("A", "B"),
            ],
        )

    assert poset.children_of("A") == ["B"]
    assert poset.parents_of("B") == ["A"]
    assert poset.global_in_degree["B"] == 1
    assert poset.global_in_degree["C"] == 1
