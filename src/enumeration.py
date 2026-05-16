from collections import defaultdict
from typing import Any, Dict, FrozenSet, Mapping

from ideal import Ideal


class PosetAnalyzer:

    def __init__(self, poset):
        self.poset = poset
        self._successor_closure: dict[str, set[str]] | None = None

    def count_linear_extensions(self) -> int:
        """
        Count linear extensions using canonical minimal-element selection
        and memoization over dual order ideals.
        """
        memo: Dict[FrozenSet[str], int] = {}

        def compute_paths(current_subposet: FrozenSet[str]) -> int:
            if not current_subposet:
                return 1
                
            if current_subposet in memo:
                return memo[current_subposet]

            # Canonical minimal elements of the subposet
            minimal_nodes = self.poset.minimals_in_subposet(current_subposet)
            
            total_extensions = 0
            for x in minimal_nodes:
                next_state = current_subposet - {x}
                total_extensions += compute_paths(next_state)
            
            # Cache the structural capacity of this specific order ideal state
            memo[current_subposet] = total_extensions
            return total_extensions

        initial_subposet = frozenset(self.poset.elements)
        return compute_paths(initial_subposet)

    def num_elements(self) -> int:
        """Return the number of elements in the poset."""
        return len(self.poset.elements)

    def num_relations(self) -> int:
        """Return the number of stored dependency relations."""
        return sum(len(children) for children in self.poset.adj.values())

    def num_minimals(self) -> int:
        """Return the number of minimal elements."""
        return len(self.poset.minimals())

    def num_maximals(self) -> int:
        """Return the number of maximal elements."""
        return len(self.poset.maximals())

    def height(self) -> int:
        """Return the size of a largest chain."""
        longest_chain_ending_at = {x: 1 for x in self.poset.order}

        for x in self.poset.order:
            for child in self.poset.children_of(x):
                longest_chain_ending_at[child] = max(
                    longest_chain_ending_at[child],
                    longest_chain_ending_at[x] + 1,
                )

        return max(longest_chain_ending_at.values(), default=0)

    def comparable_successors(self, x: str) -> list[str]:
        """Return all elements greater than x, in canonical order."""
        self._validate_element(x)
        closure = self._transitive_successor_closure()
        return [y for y in self.poset.order if y in closure[x]]

    def comparability_edges(self) -> list[tuple[str, str]]:
        """Return all strict comparability pairs x < y."""
        edges = []
        for x in self.poset.order:
            edges.extend((x, y) for y in self.comparable_successors(x))
        return edges

    def is_less_equal(self, x: str, y: str) -> bool:
        """Return whether x <= y in the transitive order."""
        self._validate_element(x)
        self._validate_element(y)
        closure = self._transitive_successor_closure()
        return x == y or y in closure[x]

    def interval(self, x: str, y: str) -> list[str]:
        """Return the closed interval [x, y] in canonical order."""
        self._validate_element(x)
        self._validate_element(y)
        if not self.is_less_equal(x, y):
            return []

        return [
            z for z in self.poset.order
            if self.is_less_equal(x, z) and self.is_less_equal(z, y)
        ]

    def mobius(self, x: str, y: str) -> int:
        """
        Return the Mobius function value mu(x, y) of the poset.

        Values are computed from the recurrence:
        mu(x, x) = 1 and mu(x, y) = -sum(mu(x, z) for x <= z < y).
        Incomparable pairs have value 0.
        """
        self._validate_element(x)
        self._validate_element(y)

        if not self.is_less_equal(x, y):
            return 0

        memo: dict[tuple[str, str], int] = {}

        def compute(left: str, right: str) -> int:
            if left == right:
                return 1

            key = (left, right)
            if key in memo:
                return memo[key]

            total = 0
            for z in self.interval(left, right):
                if z != right:
                    total += compute(left, z)

            memo[key] = -total
            return memo[key]

        return compute(x, y)

    def mobius_matrix(self) -> dict[tuple[str, str], int]:
        """Return mu(x, y) for every ordered pair of elements."""
        return {
            (x, y): self.mobius(x, y)
            for x in self.poset.order
            for y in self.poset.order
        }

    def zeta_transform(
        self,
        values: Mapping[str, int | float],
    ) -> dict[str, int | float]:
        """
        Return g(y) = sum_{x <= y} f(x) for element-indexed values f.
        """
        self._validate_value_keys(values)
        return {
            y: sum(
                values[x]
                for x in self.poset.order
                if self.is_less_equal(x, y)
            )
            for y in self.poset.order
        }

    def mobius_inversion(
        self,
        values: Mapping[str, int | float],
    ) -> dict[str, int | float]:
        """
        Invert a zeta transform: f(y) = sum_{x <= y} mu(x, y) g(x).
        """
        self._validate_value_keys(values)
        return {
            y: sum(self.mobius(x, y) * values[x] for x in self.poset.order)
            for y in self.poset.order
        }

    def width(self) -> int:
        """
        Return the poset width via maximum compatible chain-link matching.

        The matching graph uses transitive comparability pairs, not only stored
        cover relations, because any x < y can serve as a chain-cover link.
        """
        matched_right_to_left: dict[str, str] = {}

        def can_match(left: str, visited_right: set[str]) -> bool:
            for right in self.comparable_successors(left):
                if right in visited_right:
                    continue
                visited_right.add(right)

                if right not in matched_right_to_left:
                    matched_right_to_left[right] = left
                    return True

                previous_left = matched_right_to_left[right]
                if can_match(previous_left, visited_right):
                    matched_right_to_left[right] = left
                    return True

            return False

        matching_size = 0
        for left in self.poset.order:
            if can_match(left, set()):
                matching_size += 1

        return self.num_elements() - matching_size

    def _validate_element(self, x: str) -> None:
        if x not in self.poset.elements:
            raise KeyError(f"Unknown poset element: {x}")

    def _validate_value_keys(self, values: Mapping[str, int | float]) -> None:
        missing = self.poset.elements - set(values)
        if missing:
            ordered_missing = [x for x in self.poset.order if x in missing]
            raise KeyError(f"Missing values for poset elements: {ordered_missing}")

    def _transitive_successor_closure(self) -> dict[str, set[str]]:
        if self._successor_closure is None:
            closure: dict[str, set[str]] = {x: set() for x in self.poset.order}

            for x in reversed(self.poset.order):
                for child in self.poset.children_of(x):
                    closure[x].add(child)
                    closure[x].update(closure[child])

            self._successor_closure = closure

        return self._successor_closure

    def get_lattice_layers(self):
        """
        Construct lattice layers of order ideals J(P) constructively,
        by growing ideals via parent-closed extensions.
        """
        elements = set(self.poset.elements)

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
                for x in self.poset.order:
                    if x not in I:
                        if all(p in I for p in self.poset.parents_of(x)):
                            J = Ideal(I | {x})
                            if J not in seen:
                                seen.add(J)
                                next_ideals.add(J)

            if not next_ideals:
                break

            layers[k + 1].extend(sorted(next_ideals, key=lambda s: [x for x in self.poset.order if x in s]))
            k += 1

        return dict(layers)

    def lattice_layer_sizes(self) -> list[int]:
        """Return the number of ideals at each rank of J(P)."""
        layers = self.get_lattice_layers()
        return [len(layers[k]) for k in sorted(layers)]

    def num_ideals(self) -> int:
        """Return the number of order ideals in J(P)."""
        return sum(self.lattice_layer_sizes())

    def summary(self) -> dict[str, Any]:
        """
        Return a structural summary computed from the actual poset.

        Family-specific labels or construction parameters belong near the
        factories, while this method measures any Poset instance uniformly.
        """
        layer_sizes = self.lattice_layer_sizes()

        return {
            "num_elements": self.num_elements(),
            "num_relations": self.num_relations(),
            "num_minimals": self.num_minimals(),
            "num_maximals": self.num_maximals(),
            "height": self.height(),
            "width": self.width(),
            "num_linear_extensions": self.count_linear_extensions(),
            "num_ideals": sum(layer_sizes),
            "lattice_layer_sizes": layer_sizes,
        }
