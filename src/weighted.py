from collections import Counter, deque
from collections.abc import Callable, Mapping

from analysis import PosetAnalyzer


Number = int | float
Edge = tuple[str, str]
ElementWeights = Mapping[str, Number] | Callable[[str], Number] | None
EdgeWeights = Mapping[Edge, Number] | Callable[[str, str], Number] | None


class WeightedPoset:
    """
    Lightweight value wrapper for attaching element and edge weights to a Poset.

    The underlying Poset is shared by reference. Reweighting methods return a
    new wrapper with copied weight dictionaries rather than mutating this one.
    """

    def __init__(
        self,
        poset,
        element_weights: ElementWeights = None,
        edge_weights: EdgeWeights = None,
    ):
        self.poset = poset
        self.element_weights = self._materialize_element_weights(element_weights)
        self.edge_weights = self._materialize_edge_weights(edge_weights)

    @classmethod
    def from_element_function(
        cls,
        poset,
        weight_function: Callable[[str], Number],
        edge_weights: EdgeWeights = None,
    ):
        """Return a weighted poset with element weights generated for every element."""
        return cls(poset, element_weights=weight_function, edge_weights=edge_weights)

    @classmethod
    def from_edge_function(
        cls,
        poset,
        weight_function: Callable[[str, str], Number],
        element_weights: ElementWeights = None,
    ):
        """Return a weighted poset with edge weights generated for every cover edge."""
        return cls(poset, element_weights=element_weights, edge_weights=weight_function)

    def with_element_weights(self, element_weights: ElementWeights):
        """Return a new wrapper over the same Poset with replaced element weights."""
        return type(self)(
            self.poset,
            element_weights=element_weights,
            edge_weights=self.edge_weights,
        )

    def with_edge_weights(self, edge_weights: EdgeWeights):
        """Return a new wrapper over the same Poset with replaced edge weights."""
        return type(self)(
            self.poset,
            element_weights=self.element_weights,
            edge_weights=edge_weights,
        )

    def cover_edges(self) -> list[Edge]:
        """Return stored cover/dependency edges in canonical source and target order."""
        return [
            (source, target)
            for source in self.poset.order
            for target in self.poset.children_of(source)
        ]

    def element_weight(self, element: str) -> Number:
        """Return the weight for an element, raising KeyError if it is unweighted."""
        self._validate_element(element)
        if element not in self.element_weights:
            raise KeyError(f"No weight assigned to poset element: {element}")
        return self.element_weights[element]

    def edge_weight(self, source: str, target: str) -> Number:
        """Return the weight for a cover edge, raising KeyError if it is unweighted."""
        self._validate_edge((source, target))
        if (source, target) not in self.edge_weights:
            raise KeyError(f"No weight assigned to cover edge: {(source, target)}")
        return self.edge_weights[(source, target)]

    def element_weight_vector(self) -> list[Number]:
        """Return element weights in canonical order. All elements must be weighted."""
        return [self.element_weight(element) for element in self.poset.order]

    def edge_weight_vector(self) -> list[Number]:
        """Return cover-edge weights in canonical edge order. All edges must be weighted."""
        return [self.edge_weight(source, target) for source, target in self.cover_edges()]

    def _materialize_element_weights(self, weights: ElementWeights) -> dict[str, Number]:
        if weights is None:
            return {}

        if callable(weights):
            return {element: weights(element) for element in self.poset.order}

        invalid = set(weights) - self.poset.elements
        if invalid:
            raise KeyError(f"Unknown weighted poset elements: {sorted(invalid)}")
        return dict(weights)

    def _materialize_edge_weights(self, weights: EdgeWeights) -> dict[Edge, Number]:
        if weights is None:
            return {}

        valid_edges = set(self.cover_edges())
        if callable(weights):
            return {
                (source, target): weights(source, target)
                for source, target in self.cover_edges()
            }

        invalid = set(weights) - valid_edges
        if invalid:
            raise KeyError(f"Unknown weighted cover edges: {sorted(invalid)}")
        return dict(weights)

    def _validate_element(self, element: str) -> None:
        if element not in self.poset.elements:
            raise KeyError(f"Unknown poset element: {element}")

    def _validate_edge(self, edge: Edge) -> None:
        if edge not in set(self.cover_edges()):
            raise KeyError(f"Unknown cover edge: {edge}")


class WeightedPosetAnalyzer:
    """Analyzer for weight-aware measurements over a WeightedPoset."""

    def __init__(self, weighted_poset: WeightedPoset):
        self.weighted_poset = weighted_poset
        self.poset = weighted_poset.poset
        self.base = PosetAnalyzer(self.poset)
        self._lattice_layers = None
        self._ideal_scores = None

    def max_chain_weight(self, mode: str = "elements") -> Number:
        """
        Return the maximum nonnegative chain weight.

        Modes:
        - elements: sum element weights along the chain.
        - edges: sum stored cover-edge weights along the chain.
        - both: sum element weights and stored cover-edge weights.

        This is a measurement-style weighted height. It requires every weight
        used by the selected mode to be nonnegative. Use max_chain_score() for
        signed optimization over chains.

        Chains are scored along stored cover-edge paths. Element scoring
        includes every intermediate element on that path; it does not skip
        negative intermediate elements via transitive comparability.

        The combined "both" mode is meaningful only when element and edge
        weights are measured in the same units.
        """
        self._validate_chain_weight_mode(mode)
        self._validate_nonnegative_chain_weights(mode)
        return self.max_chain_score(mode)

    def max_chain_score(self, mode: str = "elements") -> Number:
        """
        Return the maximum signed chain score.

        This uses the same chain accumulation rules as max_chain_weight(), but
        allows negative weights. On a nonempty poset the optimized chain is
        nonempty; in edge-only mode, a singleton chain has score 0.

        Chains are scored along stored cover-edge paths. Element scoring
        includes every intermediate element on that path; it does not skip
        negative intermediate elements via transitive comparability. Future
        interval-native weighting can represent those skip-style interpretations
        explicitly.
        """
        self._validate_chain_weight_mode(mode)

        if not self.poset.elements:
            return 0

        best_ending_at = {
            element: self._chain_start_weight(element, mode)
            for element in self.poset.order
        }

        for source in self.poset.order:
            for target in self.poset.children_of(source):
                candidate = (
                    best_ending_at[source]
                    + self._chain_transition_weight(source, target, mode)
                )
                best_ending_at[target] = max(best_ending_at[target], candidate)

        return max(best_ending_at.values())

    def weighted_width(self) -> Number:
        """
        Return the maximum total element weight of an antichain.

        This is the element-weighted analogue of poset width. Edge weights are
        ignored: antichains are selected sets of elements, so this measurement
        only sums element weights. It requires nonnegative element weights. Use
        max_antichain_score() for signed optimization over antichains.
        """
        element_weights = {
            element: self.weighted_poset.element_weight(element)
            for element in self.poset.order
        }

        if any(weight < 0 for weight in element_weights.values()):
            raise ValueError("Weighted width requires nonnegative element weights.")

        return self.max_antichain_score()

    def max_antichain_score(self) -> Number:
        """
        Return the maximum signed score of an antichain.

        Negative element scores are allowed. The empty antichain is allowed, so
        the result is never below 0. Edge weights are ignored.
        """
        element_scores = {
            element: self.weighted_poset.element_weight(element)
            for element in self.poset.order
        }

        positive_scores = {
            element: max(score, 0)
            for element, score in element_scores.items()
        }
        total_weight = sum(positive_scores.values())
        if not self.poset.elements:
            return 0

        source = ("source", "s")
        sink = ("sink", "t")
        infinite_capacity = total_weight + 1
        capacities = {}

        for element, weight in positive_scores.items():
            left = ("out", element)
            right = ("in", element)
            capacities[(source, left)] = weight
            capacities[(right, sink)] = weight

            for successor in self.base.comparable_successors(element):
                capacities[(left, ("in", successor))] = infinite_capacity

        minimum_vertex_cover_weight = self._max_flow(capacities, source, sink)
        return total_weight - minimum_vertex_cover_weight

    def zeta_transform(self) -> dict[str, Number]:
        """
        Return element-weighted zeta totals over principal ideals.

        This computes g(y) = sum(w(x) for x <= y). Use the base analyzer's
        strict_zeta_transform() for the strict relation x < y.

        This uses element weights only. Interval-native or comparability-pair
        weights are a separate future extension from cover-edge weights.
        """
        return self.base.zeta_transform(self.weighted_poset.element_weights)

    def mobius_inversion(self, values: Mapping[str, Number]) -> dict[str, Number]:
        """
        Invert a closed element-weighted zeta transform.

        This delegates to the base poset's Mobius inversion because the
        weighted zeta transform still uses the ordinary zeta relation; only
        the element-indexed input values are weighted.
        """
        return self.base.mobius_inversion(values)

    def interval_weight(
        self,
        x: str,
        y: str,
    ) -> Number:
        """
        Return the total element weight over the closed interval [x, y].

        Incomparable endpoints have interval weight 0, matching the base
        analyzer's empty interval behavior.
        """
        return sum(
            self.weighted_poset.element_weight(element)
            for element in self.base.interval(x, y)
        )

    def open_interval_weight(self, x: str, y: str) -> Number:
        """Return the total element weight over the open interval (x, y)."""
        return sum(
            self.weighted_poset.element_weight(element)
            for element in self.base.interval(x, y)
            if element not in {x, y}
        )

    def get_lattice_layers(self):
        """Return base analyzer lattice layers, cached for reuse."""
        if self._lattice_layers is None:
            self._lattice_layers = self.base.get_lattice_layers()
        return self._lattice_layers

    def ideal_weight(self, ideal) -> Number:
        """
        Return the nonnegative total element weight of an order ideal.

        This is a measurement-style ideal weight. It requires the elements in
        the ideal to have nonnegative weights. Use ideal_score() for signed
        totals over ideals.
        """
        for element in self.poset.order:
            if element in ideal and self.weighted_poset.element_weight(element) < 0:
                raise ValueError("Ideal weight requires nonnegative element weights.")

        return self.ideal_score(ideal)

    def ideal_score(self, ideal) -> Number:
        """Return the signed total element score of an order ideal."""
        if self._ideal_scores is None:
            self._ideal_scores = {}

        if ideal not in self._ideal_scores:
            self._ideal_scores[ideal] = sum(
                self.weighted_poset.element_weight(element)
                for element in self.poset.order
                if element in ideal
            )

        return self._ideal_scores[ideal]

    def weighted_lattice_layer_summary(self) -> dict:
        """
        Return compact nonnegative ideal-weight summaries by lattice layer.

        This uses ideal_weight(), so negative element weights are rejected when
        they appear in an ideal. Use weighted_lattice_layer_score_summary() for
        signed summaries.
        """
        layers = self.get_lattice_layers()
        return {
            layer: self._weight_summary([self.ideal_weight(ideal) for ideal in ideals])
            for layer, ideals in layers.items()
        }

    def weighted_lattice_layer_score_summary(self) -> dict:
        """Return compact signed ideal-score summaries grouped by lattice layer."""
        layers = self.get_lattice_layers()
        return {
            layer: self._weight_summary(
                [self.ideal_score(ideal) for ideal in ideals],
                value_name="ideal_score",
            )
            for layer, ideals in layers.items()
        }

    def _chain_start_weight(self, element: str, mode: str) -> Number:
        if mode == "edges":
            return 0
        return self.weighted_poset.element_weight(element)

    def _chain_transition_weight(self, source: str, target: str, mode: str) -> Number:
        if mode == "elements":
            return self.weighted_poset.element_weight(target)
        if mode == "edges":
            return self.weighted_poset.edge_weight(source, target)
        return (
            self.weighted_poset.element_weight(target)
            + self.weighted_poset.edge_weight(source, target)
        )

    def _validate_chain_weight_mode(self, mode: str) -> None:
        valid_modes = {"elements", "edges", "both"}
        if mode not in valid_modes:
            raise ValueError(f"Unknown chain weight mode: {mode}")

    def _validate_nonnegative_chain_weights(self, mode: str) -> None:
        if mode in {"elements", "both"}:
            for element in self.poset.order:
                if self.weighted_poset.element_weight(element) < 0:
                    raise ValueError(
                        "Chain weight requires nonnegative element weights."
                    )

        if mode in {"edges", "both"}:
            for source, target in self.weighted_poset.cover_edges():
                if self.weighted_poset.edge_weight(source, target) < 0:
                    raise ValueError("Chain weight requires nonnegative edge weights.")

    def _max_flow(
        self,
        capacities: Mapping[tuple[object, object], Number],
        source,
        sink,
    ) -> Number:
        residual = {}
        adjacency = {}

        for (start, end), capacity in capacities.items():
            residual[(start, end)] = residual.get((start, end), 0) + capacity
            residual.setdefault((end, start), 0)
            adjacency.setdefault(start, set()).add(end)
            adjacency.setdefault(end, set()).add(start)

        flow = 0
        while True:
            parent = {source: None}
            queue = deque([source])

            while queue and sink not in parent:
                current = queue.popleft()
                for neighbor in adjacency.get(current, ()):
                    if neighbor not in parent and residual[(current, neighbor)] > 0:
                        parent[neighbor] = current
                        queue.append(neighbor)

            if sink not in parent:
                return flow

            path_capacity = None
            current = sink
            while current != source:
                previous = parent[current]
                edge_capacity = residual[(previous, current)]
                path_capacity = (
                    edge_capacity
                    if path_capacity is None
                    else min(path_capacity, edge_capacity)
                )
                current = previous

            current = sink
            while current != source:
                previous = parent[current]
                residual[(previous, current)] -= path_capacity
                residual[(current, previous)] += path_capacity
                current = previous

            flow += path_capacity

    def _weight_summary(
        self,
        weights: list[Number],
        value_name: str = "ideal_weight",
    ) -> dict:
        if not weights:
            return {
                "num_ideals": 0,
                f"min_{value_name}": 0,
                f"max_{value_name}": 0,
                f"mean_{value_name}": 0,
                f"{value_name}_histogram": {},
            }

        counts = Counter(weights)
        return {
            "num_ideals": len(weights),
            f"min_{value_name}": min(weights),
            f"max_{value_name}": max(weights),
            f"mean_{value_name}": sum(weights) / len(weights),
            f"{value_name}_histogram": {
                weight: counts[weight]
                for weight in sorted(counts)
            },
        }
