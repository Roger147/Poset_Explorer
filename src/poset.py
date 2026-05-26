import warnings
from typing import Set, FrozenSet, List, Dict
from ideal import Ideal

class Poset:
    def __init__(self, elements: Set[str], relations: List[tuple[str, str]]):
        self.elements: Set[str] = elements
        relations = self._normalize_relations(relations)
        
        # Hasse diagram forward edges (adjacency list for child nodes)
        self.adj: Dict[str, set[str]] = {e: set() for e in elements}
        
        # Dual Hasse diagram backward edges (reverse adjacency list for parent prerequisites)
        self.parents: Dict[str, set[str]] = {e: set() for e in elements}
        
        # Global minimal element tracking (base in-degree map)
        self.global_in_degree: Dict[str, int] = {e: 0 for e in elements}
        
        # Population of structural relations
        for u, v in relations:
            self.adj[u].add(v)
            self.parents[v].add(u)
            self.global_in_degree[v] += 1
        self._check_for_cycles()
        self.order = self.canonical_order()
        

    def minimals(self) -> list[str]:
        mins = [x for x in self.elements if len(self.parents[x]) == 0]
        return [x for x in self.order if x in mins]

    def maximals(self) -> list[str]:
        maxs = [x for x in self.elements if len(self.adj[x]) == 0]
        return [x for x in self.order if x in maxs]    
    
    def parents_of(self, x: str) -> list[str]:
        """Return parents of x in canonical order."""
        return [parent for parent in self.order if parent in self.parents[x]]

    def children_of(self, x: str) -> list[str]:
        """Return children of x in canonical order."""
        return [child for child in self.order if child in self.adj[x]]

    def minimals_in_subposet(self, subset: FrozenSet[str]) -> List[str]:
        
        mins = []
        for x in subset:
            if all(p not in subset for p in self.parents_of(x)):
                mins.append(x)
        return [x for x in self.order if x in mins]

    def canonical_order(self) -> list[str]:
        """Return a canonical topological ordering using lexicographic tie-breaking."""
        # Copy in-degree so we don't mutate the global one
        in_degree = {x: len(self.parents[x]) for x in self.elements}

        # Start with all global minimal elements, sorted lexicographically
        available = sorted([x for x in self.elements if in_degree[x] == 0])
        order = []

        while available:
        # Pick the lexicographically smallest minimal element
            x = available.pop(0)
            order.append(x)

        # Remove x from the graph
            for child in sorted(self.adj[x]):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    available.append(child)
                    available.sort()

        return order
    
    def repr_ideal(self, ideal: Ideal) -> str:
        if not ideal:
            return "ideal()"
        ordered = [x for x in self.order if x in ideal]
        return "ideal(" + ", ".join(ordered) + ")"

    def _check_for_cycles(self):
        in_degree = dict(self.global_in_degree)
        queue = [n for n, deg in in_degree.items() if deg == 0]
        visited = 0

        while queue:
            u = queue.pop()
            visited += 1
            for v in self.adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if visited != len(self.elements):
            raise ValueError("Invalid poset: relations contain a cycle.")

    def _normalize_relations(
        self,
        relations: List[tuple[str, str]],
    ) -> list[tuple[str, str]]:
        normalized = list(dict.fromkeys(relations))
        num_duplicates = len(relations) - len(normalized)

        if num_duplicates:
            warnings.warn(
                (
                    f"Removed {num_duplicates} duplicate relation(s); "
                    "poset relations are set-valued, so each x < y pair is "
                    "stored once."
                ),
                stacklevel=2,
            )

        return normalized
    
