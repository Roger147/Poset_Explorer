from collections import Counter, defaultdict
from typing import Any, Mapping

from closure import (
    interval_summary_data,
    lattice_layer_sizes as backend_lattice_layer_sizes,
    linear_extension_count_data,
    mobius_matrix_data,
    strict_zeta_transform_data,
    transitive_successor_closure,
    width_data,
    zeta_summary_data,
    zeta_transform_data,
)
from ideal import Ideal


class PosetAnalyzer:

    def __init__(self, poset):
        self.poset = poset
        self._indexed_successor_closure: list[set[int]] | None = None
        self._indexed_mobius_matrix: list[list[int]] | None = None
        self._successor_closure: dict[str, set[str]] | None = None
        self._lattice_layer_sizes: list[int] | None = None

    def count_linear_extensions(self, max_elements: int | None = 24) -> int:
        """
        Count linear extensions using bitmask memoization.

        This computation is exponential in general. Empty posets and chains
        return immediately; otherwise, max_elements guards the starting poset
        size. Pass max_elements=None only when you have checked the structure
        carefully: non-chain posets can exhaust time or memory very quickly,
        even with the Rust backend.
        """
        num_elements = self.num_elements()

        if num_elements == 0:
            return 1

        if self.width() == 1:
            return 1

        if max_elements is not None and num_elements > max_elements:
            raise ValueError(
                "Linear extension counting is exponential; pass "
                "max_elements=None to override the element-count guard."
            )

        return linear_extension_count_data(num_elements, self.poset.indexed_relations())

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
        closure = self._indexed_transitive_successor_closure()
        element_index = self.poset.element_to_index[x]
        return [
            self.poset.index_to_element[successor_index]
            for successor_index in sorted(closure[element_index])
        ]

    def comparability_edges(self) -> list[tuple[str, str]]:
        """Return all strict comparability pairs x < y."""
        closure = self._indexed_transitive_successor_closure()
        return [
            (
                self.poset.index_to_element[element_index],
                self.poset.index_to_element[successor_index],
            )
            for element_index, successors in enumerate(closure)
            for successor_index in sorted(successors)
        ]

    def is_less_equal(self, x: str, y: str) -> bool:
        """Return whether x <= y in the transitive order."""
        self._validate_element(x)
        self._validate_element(y)
        return self._is_less_equal_index(
            self.poset.element_to_index[x],
            self.poset.element_to_index[y],
        )

    def interval(self, x: str, y: str) -> list[str]:
        """Return the closed interval [x, y] in canonical order."""
        self._validate_element(x)
        self._validate_element(y)
        left_index = self.poset.element_to_index[x]
        right_index = self.poset.element_to_index[y]

        if not self._is_less_equal_index(left_index, right_index):
            return []

        return [
            self.poset.index_to_element[middle_index]
            for middle_index in range(self.num_elements())
            if (
                self._is_less_equal_index(left_index, middle_index)
                and self._is_less_equal_index(middle_index, right_index)
            )
        ]

    def interval_summary(self) -> dict[str, Any]:
        """
        Return compact statistics over all closed intervals [x, y].

        This summarizes the bounded local subposets without materializing a
        large interval table in the public result.
        """
        return interval_summary_data(self.num_elements(), self.poset.indexed_relations())

    def mobius(self, x: str, y: str) -> int:
        """
        Return the Mobius function value mu(x, y) of the poset.

        Values are computed from the recurrence:
        mu(x, x) = 1 and mu(x, y) = -sum(mu(x, z) for x <= z < y).
        Incomparable pairs have value 0.
        """
        self._validate_element(x)
        self._validate_element(y)

        return self._indexed_mobius_matrix_data()[
            self.poset.element_to_index[x]
        ][
            self.poset.element_to_index[y]
        ]

    def mobius_matrix(self) -> dict[tuple[str, str], int]:
        """
        Return mu(x, y) for every ordered pair of elements.

        This is the incidence-algebra inverse of zeta_matrix().
        """
        matrix = self._indexed_mobius_matrix_data()
        return {
            (
                self.poset.index_to_element[left_index],
                self.poset.index_to_element[right_index],
            ): matrix[left_index][right_index]
            for left_index in range(self.num_elements())
            for right_index in range(self.num_elements())
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
        strict_comparability_count, principal_ideal_sizes, principal_filter_sizes = (
            zeta_summary_data(num_elements, self.poset.indexed_relations())
        )
        cover_relation_count = self.num_relations()
        comparable_ordered_pair_count = num_elements + strict_comparability_count
        incomparable_ordered_pair_count = (
            total_ordered_pairs - comparable_ordered_pair_count
        )

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
        matrix = self._indexed_mobius_matrix_data()
        interval_pairs = self._interval_index_pairs()
        values = [matrix[left][right] for left, right in interval_pairs]
        abs_values = [abs(value) for value in values]
        ranks = self._rank_levels_if_ranked()
        by_rank_distance: dict[int, list[int]] = defaultdict(list)

        if ranks is not None:
            for left, right in interval_pairs:
                x = self.poset.index_to_element[left]
                y = self.poset.index_to_element[right]
                by_rank_distance[ranks[y] - ranks[x]].append(matrix[left][right])

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
    ) -> dict[str, float]:
        """
        Return g(y) = sum_{x <= y} f(x) for element-indexed values f.

        Transform totals are computed through an f64-compatible backend path,
        so results are returned as floats.
        """
        self._validate_value_keys(values)
        transformed = zeta_transform_data(
            self.num_elements(),
            self.poset.indexed_relations(),
            self._value_vector(values),
        )
        return {
            self.poset.index_to_element[index]: transformed[index]
            for index in range(self.num_elements())
        }

    def strict_zeta_transform(
        self,
        values: Mapping[str, int | float],
    ) -> dict[str, float]:
        """
        Return g(y) = sum_{x < y} f(x) for element-indexed values f.

        This uses the strict zeta relation, with the diagonal removed. It is
        not a standalone Mobius inversion target. Transform totals are computed
        through an f64-compatible backend path, so results are returned as
        floats.
        """
        self._validate_value_keys(values)
        transformed = strict_zeta_transform_data(
            self.num_elements(),
            self.poset.indexed_relations(),
            self._value_vector(values),
        )
        return {
            self.poset.index_to_element[index]: transformed[index]
            for index in range(self.num_elements())
        }

    def mobius_inversion(
        self,
        values: Mapping[str, int | float],
    ) -> dict[str, int | float]:
        """
        Invert a closed zeta transform: f(y) = sum_{x <= y} mu(x, y) g(x).
        """
        self._validate_value_keys(values)
        matrix = self._indexed_mobius_matrix_data()
        return {
            self.poset.index_to_element[right_index]: sum(
                matrix[left_index][right_index]
                * values[self.poset.index_to_element[left_index]]
                for left_index in range(self.num_elements())
            )
            for right_index in range(self.num_elements())
        }

    def width(self) -> int:
        """
        Return the poset width via maximum compatible chain-link matching.

        The matching graph uses transitive comparability pairs, not only stored
        cover relations, because any x < y can serve as a chain-cover link.
        """
        return width_data(self.num_elements(), self.poset.indexed_relations())

    def _validate_element(self, x: str) -> None:
        if x not in self.poset.elements:
            raise KeyError(f"Unknown poset element: {x}")

    def _validate_value_keys(self, values: Mapping[str, int | float]) -> None:
        missing = self.poset.elements - set(values)
        if missing:
            ordered_missing = [x for x in self.poset.order if x in missing]
            raise KeyError(f"Missing values for poset elements: {ordered_missing}")

    def _value_vector(self, values: Mapping[str, int | float]) -> list[int | float]:
        return [values[element] for element in self.poset.order]

    def _transitive_successor_closure(self) -> dict[str, set[str]]:
        if self._successor_closure is None:
            indexed_closure = self._indexed_transitive_successor_closure()
            self._successor_closure = {
                element: {
                    self.poset.index_to_element[successor_index]
                    for successor_index in indexed_closure[element_index]
                }
                for element_index, element in enumerate(self.poset.index_to_element)
            }

        return self._successor_closure

    def _indexed_transitive_successor_closure(self) -> list[set[int]]:
        if self._indexed_successor_closure is None:
            self._indexed_successor_closure = transitive_successor_closure(
                self.num_elements(),
                self.poset.indexed_relations(),
            )

        return self._indexed_successor_closure

    def _indexed_mobius_matrix_data(self) -> list[list[int]]:
        if self._indexed_mobius_matrix is None:
            self._indexed_mobius_matrix = mobius_matrix_data(
                self.num_elements(),
                self.poset.indexed_relations(),
            )

        return self._indexed_mobius_matrix

    def _is_less_equal_index(self, left_index: int, right_index: int) -> bool:
        if left_index == right_index:
            return True

        closure = self._indexed_transitive_successor_closure()
        return right_index in closure[left_index]

    def _interval_index_pairs(self) -> list[tuple[int, int]]:
        return [
            (left, right)
            for left in range(self.num_elements())
            for right in range(self.num_elements())
            if self._is_less_equal_index(left, right)
        ]

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
        if self._lattice_layer_sizes is None:
            self._lattice_layer_sizes = backend_lattice_layer_sizes(
                self.num_elements(),
                self.poset.indexed_relations(),
            )

        return list(self._lattice_layer_sizes)

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
