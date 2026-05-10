import sys
from pathlib import Path

import poset

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from poset import Poset

def test_basic_poset():
    elements = { "A","B","C","D"}

    relations = [
    ("A", "B"),
    ("A", "C"),
    ("B", "D"),
    ("C", "D")
]

    poset = Poset(elements, relations)

    assert poset.adj["A"] == {"B", "C"}
    assert poset.parents["D"] == {"B", "C"}
    assert poset.global_in_degree["A"] == 0
    assert poset.global_in_degree["D"] == 2

    subset = frozenset({"A", "B", "C", "D"})

    minimal = poset._find_minimal_elements_in_subposet(subset)

    assert set(minimal) == {"A"}

    subsetup = frozenset({"B", "C", "D"})

    minimal = poset._find_minimal_elements_in_subposet(subsetup)

    assert set(minimal) == {"B", "C"}