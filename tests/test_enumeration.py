from poset import Poset
from enumeration import PosetAnalyzer 

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

    assert layers[0] == [()]  # Empty set
    assert layers[1] == ['A',]  # {A}
    assert layers[2] == [("A", "B"), ("A", "C")]  # {A,B}, {A,C}
    assert layers[3] == [("A", "B", "C")]  # {A,B,C}
    assert layers[4] == [("A", "B", "C", "D")]  # {A,B,C,D}    