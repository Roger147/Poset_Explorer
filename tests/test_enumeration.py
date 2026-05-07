from poset import Poset
from enumeration import IdealEnumerator


def test_chain_has_one_linear_extension():

    elements = {"A", "B", "C"}

    relations = [
        ("A", "B"),
        ("B", "C")
    ]

    poset = Poset(elements, relations)

    enumerator = IdealEnumerator(poset)

    count = enumerator.count_linear_extensions()

    assert count == 1

def test_three_independent_elements():

    elements = {"A", "B", "C"}

    relations = []

    poset = Poset(elements, relations)

    enumerator = IdealEnumerator(poset)

    count = enumerator.count_linear_extensions()

    assert count == 6
def test_diamond_poset():

    elements = {"A", "B", "C", "D"}

    relations = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D")
    ]

    poset = Poset(elements, relations)

    enumerator = IdealEnumerator(poset)

    count = enumerator.count_linear_extensions()

    assert count == 2