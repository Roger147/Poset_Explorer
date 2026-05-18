from collections.abc import Callable, Mapping


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
