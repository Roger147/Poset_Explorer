from collections import Counter, defaultdict
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

    def interval_summary(self) -> dict[str, Any]:
        """
        Return compact statistics over all closed intervals [x, y].

        This summarizes the bounded local subposets without materializing a
        large interval table in the public result.
        """
        interval_sizes = [
            len(self.interval(x, y))
            for x, y in self._interval_pairs()
        ]

        if not interval_sizes:
            return {
                "num_intervals": 0,
                "num_trivial_intervals": 0,
                "num_nontrivial_intervals": 0,
                "num_cover_intervals": 0,
                "min_interval_size": 0,
                "max_interval_size": 0,
                "mean_interval_size": 0,
                "interval_size_histogram": {},
            }

        return {
            "num_intervals": len(interval_sizes),
            "num_trivial_intervals": sum(size == 1 for size in interval_sizes),
            "num_nontrivial_intervals": sum(size > 1 for size in interval_sizes),
            "num_cover_intervals": sum(size == 2 for size in interval_sizes),
            "min_interval_size": min(interval_sizes),
            "max_interval_size": max(interval_sizes),
            "mean_interval_size": sum(interval_sizes) / len(interval_sizes),
            "interval_size_histogram": self._histogram(interval_sizes),
        }

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
        """
        Return mu(x, y) for every ordered pair of elements.

        This is the incidence-algebra inverse of zeta_matrix().
        """
        return {
            (x, y): self.mobius(x, y)
            for x in self.poset.order
            for y in self.poset.order
        }

    def zeta_matrix(self) -> dict[tuple[str, str], int]:
        """Return zeta(x, y) for every ordered pair of elements."""
        return {
            (x, y): int(self.is_less_equal(x, y))
            for x in self.poset.order
            for y in self.poset.order
        }

    def zeta_summary(self) -> dict[str, Any]:
        """
        Return compact zeta/comparability statistics.

        The zeta matrix is the transitive reflexive closure of the stored
        cover/dependency relations. This summary emphasizes that closure by
        reporting how many strict comparabilities are implied beyond the
        stored cover relations.
        """
        num_elements = self.num_elements()
        total_ordered_pairs = num_elements * num_elements
        strict_comparability_count = len(self.comparability_edges())
        cover_relation_count = self.num_relations()
        comparable_ordered_pair_count = num_elements + strict_comparability_count
        incomparable_ordered_pair_count = (
            total_ordered_pairs - comparable_ordered_pair_count
        )
        principal_ideal_sizes = [
            sum(1 for x in self.poset.order if self.is_less_equal(x, y))
            for y in self.poset.order
        ]
        principal_filter_sizes = [
            sum(1 for y in self.poset.order if self.is_less_equal(x, y))
            for x in self.poset.order
        ]

        return {
            "num_zeta_values": total_ordered_pairs,
            "zeta_one_count": comparable_ordered_pair_count,
            "zeta_zero_count": incomparable_ordered_pair_count,
            "zeta_density": (
                comparable_ordered_pair_count / total_ordered_pairs
                if total_ordered_pairs
                else 0
            ),
            "diagonal_count": num_elements,
            "strict_comparability_count": strict_comparability_count,
            "cover_relation_count": cover_relation_count,
            "transitive_closure_extra_count": (
                strict_comparability_count - cover_relation_count
            ),
            "principal_ideal_size_histogram": self._histogram(principal_ideal_sizes),
            "principal_filter_size_histogram": self._histogram(principal_filter_sizes),
        }

    def mobius_summary(self) -> dict[str, Any]:
        """
        Return compact Mobius statistics over comparable intervals.

        The full Mobius matrix is intentionally exposed only through
        mobius_matrix(), because it grows quadratically with the poset size.
        """
        values = [
            self.mobius(x, y)
            for x, y in self._interval_pairs()
        ]
        abs_values = [abs(value) for value in values]
        ranks = self._rank_levels_if_ranked()
        by_rank_distance: dict[int, list[int]] = defaultdict(list)

        if ranks is not None:
            for x, y in self._interval_pairs():
                by_rank_distance[ranks[y] - ranks[x]].append(self.mobius(x, y))

        if not values:
            return {
                "num_mobius_values": 0,
                "mobius_zero_count": 0,
                "mobius_nonzero_count": 0,
                "mobius_positive_count": 0,
                "mobius_negative_count": 0,
                "mobius_min": 0,
                "mobius_max": 0,
                "mobius_abs_sum": 0,
                "mobius_value_histogram": {},
                "is_ranked": ranks is not None,
                "mobius_value_histogram_by_rank_distance": {},
            }

        return {
            "num_mobius_values": len(values),
            "mobius_zero_count": sum(value == 0 for value in values),
            "mobius_nonzero_count": sum(value != 0 for value in values),
            "mobius_positive_count": sum(value > 0 for value in values),
            "mobius_negative_count": sum(value < 0 for value in values),
            "mobius_min": min(values),
            "mobius_max": max(values),
            "mobius_abs_sum": sum(abs_values),
            "mobius_value_histogram": self._histogram(values),
            "is_ranked": ranks is not None,
            "mobius_value_histogram_by_rank_distance": {
                distance: self._histogram(by_rank_distance[distance])
                for distance in sorted(by_rank_distance)
            },
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
        Invert a closed zeta transform: f(y) = sum_{x <= y} mu(x, y) g(x).
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

    def _interval_pairs(self) -> list[tuple[str, str]]:
        return [
            (x, y)
            for x in self.poset.order
            for y in self.poset.order
            if self.is_less_equal(x, y)
        ]

    def _rank_levels_if_ranked(self) -> dict[str, int] | None:
        ranks: dict[str, int] = {}

        for x in self.poset.order:
            parents = self.poset.parents_of(x)
            if not parents:
                ranks[x] = 0
                continue

            parent_ranks = {ranks[parent] for parent in parents}
            if len(parent_ranks) != 1:
                return None

            ranks[x] = parent_ranks.pop() + 1

        return ranks

    def _histogram(self, values: list[int]) -> dict[int, int]:
        counts = Counter(values)
        return {value: counts[value] for value in sorted(counts)}

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
