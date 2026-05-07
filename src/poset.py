from typing import Set, FrozenSet, List, Dict

class Poset:
    def __init__(self, elements: Set[str], relations: List[tuple[str, str]]):
        self.elements: Set[str] = elements
        
        # Hasse diagram forward edges (adjacency list for child nodes)
        self.adj: Dict[str, List[str]] = {e: [] for e in elements}
        
        # Dual Hasse diagram backward edges (reverse adjacency list for parent prerequisites)
        self.parents: Dict[str, List[str]] = {e: [] for e in elements}
        
        # Global minimal element tracking (base in-degree map)
        self.global_in_degree: Dict[str, int] = {e: 0 for e in elements}
        
        # Population of structural relations
        for u, v in relations:
            self.adj[u].append(v)
            self.parents[v].append(u)
            self.global_in_degree[v] += 1

    def _find_minimal_elements_in_subposet(self, subset: FrozenSet[str]) -> List[str]:
        
        minimal_elements = []
        for node in subset:
            # Optimization: If the node is a global minimal element (root source),
            # it can never have a remaining parent prerequisite inside any subset.
            if self.global_in_degree[node] == 0:
                minimal_elements.append(node)
                continue
                
            # Structural Verification: Check if any covered lower bound (parent node)
            # is still present within our dual order ideal (active work pool).
            is_minimal = True
            for parent in self.parents[node]:
                if parent in subset:
                    is_minimal = False
                    break  # Element is bounded below (blocked), terminate check
            
            if is_minimal:
                minimal_elements.append(node)
        return minimal_elements


