 
from collections import defaultdict
import itertools
from typing import Dict, FrozenSet

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
        layers = defaultdict(list)
    
        # Generate all possible subsets
        for r in range(len(self.poset.elements) + 1):
            for subset in itertools.combinations(self.poset.elements, r):
                # Check if it's a valid ideal
                if self._is_valid_ideal(set(subset)):
                    layers[len(subset)].append(subset)
    
        return dict(layers)

    def _is_valid_ideal(self, subset):
        for u in subset:
            for v in self.poset.parents[u]:
                if v not in subset:
                    return False
        return True