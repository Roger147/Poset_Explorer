from collections import Counter
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
        self._ideal_weights = None

    def max_chain_weight(self, mode: str = "elements") -> Number:
        """
        Return the maximum chain weight.

        Modes:
        - elements: sum element weights along the chain.
        - edges: sum stored cover-edge weights along the chain.
        - both: sum element weights and stored cover-edge weights.
        """
        valid_modes = {"elements", "edges", "both"}
        if mode not in valid_modes:
            raise ValueError(f"Unknown chain weight mode: {mode}")

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

    def get_lattice_layers(self):
        """Return base analyzer lattice layers, cached for reuse."""
        if self._lattice_layers is None:
            self._lattice_layers = self.base.get_lattice_layers()
        return self._lattice_layers

    def ideal_weight(self, ideal) -> Number:
        """Return the sum of element weights in an order ideal."""
        if self._ideal_weights is None:
            self._ideal_weights = {}

        if ideal not in self._ideal_weights:
            self._ideal_weights[ideal] = sum(
                self.weighted_poset.element_weight(element)
                for element in self.poset.order
                if element in ideal
            )

        return self._ideal_weights[ideal]

    def weighted_lattice_layer_summary(self) -> dict:
        """Return compact ideal-weight summaries grouped by lattice layer."""
        layers = self.get_lattice_layers()
        return {
            layer: self._weight_summary([self.ideal_weight(ideal) for ideal in ideals])
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

    def _weight_summary(self, weights: list[Number]) -> dict:
        if not weights:
            return {
                "num_ideals": 0,
                "min_ideal_weight": 0,
                "max_ideal_weight": 0,
                "mean_ideal_weight": 0,
                "ideal_weight_histogram": {},
            }

        counts = Counter(weights)
        return {
            "num_ideals": len(weights),
            "min_ideal_weight": min(weights),
            "max_ideal_weight": max(weights),
            "mean_ideal_weight": sum(weights) / len(weights),
            "ideal_weight_histogram": {
                weight: counts[weight]
                for weight in sorted(counts)
            },
        }
