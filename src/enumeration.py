 
from collections import defaultdict
from typing import Dict, FrozenSet
from ideal import Ideal

class PosetAnalyzer:

    def __init__(self, poset):
        self.poset = poset

    def count_linear_extensions(self) -> int:
        """
        Executes the global enumeration over the distributive lattice of order ideals J(P).
        Utilizes a memoization dictionary (hash map cache) to bound complexity to O(2^n).
        """
        # The memoization repository (state cache)
        # Key: FrozenSet[str] (Dual Order Ideal) -> Value: int (Total Extension Paths)
        memo: Dict[FrozenSet[str], int] = {}

        def compute_paths(current_subposet: FrozenSet[str]) -> int:
            # Base Case 1: The empty set ideal signifies a completed maximal chain (terminal leaf execution)
            if not current_subposet:
                return 1
                
            # Base Case 2: State has already been evaluated via an alternative structural path
            if current_subposet in memo:
                return memo[current_subposet]

            # Find all elements qualified for immediate extraction
            minimal_nodes = self.poset._find_minimal_elements_in_subposet(current_subposet)
            
            total_extensions = 0
            for x in minimal_nodes:
                # Algebraic reduction: strip element x from the dual order ideal
                next_state = current_subposet - {x}
                total_extensions += compute_paths(next_state)
            
            # Cache the structural capacity of this specific order ideal state
            memo[current_subposet] = total_extensions
            return total_extensions

        # Initiate traversal passing the global poset elements (full project workload)
        initial_subposet = frozenset(self.poset.elements)
        return compute_paths(initial_subposet)

    def get_lattice_layers(self):
        """
        Construct lattice layers of order ideals J(P) constructively,
        by growing ideals via parent-closed extensions.
        """
        elements = set(self.poset.elements)
        parents = self.poset.parents  # dict: x -> set of parents

        layers: dict[int, list[Ideal]] = defaultdict(list)
        seen: set[Ideal] = set()

        # start with the empty ideal
        start = Ideal()
        layers[0].append(start)
        seen.add(start)

        k = 0
        while True:
            current_layer = layers.get(k, [])
            if not current_layer:
                break

            next_ideals: set[Ideal] = set()

            for I in current_layer:
                # candidates are elements not yet in the ideal
                for x in elements - I:
                # x can be added iff all its parents are already in I
                    if parents[x].issubset(I):
                        J = Ideal(I | {x})
                        if J not in seen:
                            seen.add(J)
                            next_ideals.add(J)

            if not next_ideals:
                break

            layers[k + 1].extend(sorted(next_ideals, key=lambda s: sorted(s)))
            k += 1

        return dict(layers)
   