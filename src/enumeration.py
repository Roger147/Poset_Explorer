 
from collections import defaultdict
from typing import Dict, FrozenSet

class IdealEnumerator:

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
        initial_ideal = frozenset(self.poset.elements)
        return compute_paths(initial_ideal)
    
    def get_lattice_layers(self):
        """
        Groups the Order Ideals by their size to visualize the 
        levels of the Distributive Lattice J(P).
        """
        memo = {}
        # We work with Order Ideals (completed tasks) for standard J(P) visualization
        def compute_paths(current_ideal: frozenset) -> int:
            if len(current_ideal) == len(self.poset.elements): return 1
            if current_ideal in memo: return memo[current_ideal]

            # Find elements whose parents are all in the current ideal
            remaining = set(self.elements) - current_ideal
            available = [
                n for n in remaining 
                if all(p in current_ideal for p in self.poset.parents[n])
            ]
            
            total = sum(compute_paths(current_ideal | {x}) for x in available)
            memo[current_ideal] = total
            return total

        total_count = compute_paths(frozenset())
        
        # Organize for visualization
        layers = defaultdict(list)
        for ideal, count in memo.items():
            layers[len(ideal)].append((sorted(list(ideal)), count))
            
        return layers, total_count