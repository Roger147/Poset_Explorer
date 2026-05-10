from poset import Poset
from enumeration import PosetAnalyzer 

def ideal(*args):
    return frozenset(args)

def test_chain_has_one_linear_extension():

    elements = {"A", "B", "C"}

    relations = [
        ("A", "B"),
        ("B", "C")
    ]

    poset = Poset(elements, relations)

    analyzer = PosetAnalyzer(poset)

    count = analyzer.count_linear_extensions()

    assert count == 1

def test_three_independent_elements():

    elements = {"A", "B", "C"}

    relations = []

    poset = Poset(elements, relations)

    analyzer = PosetAnalyzer(poset)

    count = analyzer.count_linear_extensions()

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

    analyzer = PosetAnalyzer(poset)

    count = analyzer.count_linear_extensions()

    assert count == 2
def test_N_poset():

    elements = {"A", "B", "C", "D"}

    relations = [
        ("A", "B"),
        ("C", "B"),
        ("C", "D")
    ]

    poset = Poset(elements, relations)

    analyzer = PosetAnalyzer(poset)

    count = analyzer.count_linear_extensions()

    assert count == 5    
def test_Lattice_Layers_diamond():

    elements = {"A", "B", "C", "D"}

    relations = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D")
    ]

    poset = Poset(elements, relations)

    analyzer = PosetAnalyzer(poset)

    layers = analyzer.get_lattice_layers()

    assert set(layers[0]) == {ideal()}  # Empty set
    assert set(layers[1]) == {ideal("A")}  # {A}
    assert set(layers[2]) == {ideal("A", "B"), ideal("A", "C")}  # {A,B}, {A,C}
    assert set(layers[3]) == {ideal("A", "B", "C")}  # {A,B,C}
    assert set(layers[4]) == {ideal("A", "B", "C", "D")}  # {A,B,C,D}    