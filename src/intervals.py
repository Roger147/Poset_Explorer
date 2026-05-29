from dataclasses import dataclass

from analysis import PosetAnalyzer


@dataclass(frozen=True)
class IntervalConfig:
    """Endpoint-inclusion settings for element-based interval interpretations."""

    include_left: bool = True
    include_right: bool = True

    @classmethod
    def closed(cls):
        """Return configuration for the closed interval [x, y]."""
        return cls(include_left=True, include_right=True)

    @classmethod
    def open(cls):
        """Return configuration for the open interval (x, y)."""
        return cls(include_left=False, include_right=False)

    @classmethod
    def left_open(cls):
        """Return configuration for the left-open interval (x, y]."""
        return cls(include_left=False, include_right=True)

    @classmethod
    def right_open(cls):
        """Return configuration for the right-open interval [x, y)."""
        return cls(include_left=True, include_right=False)


class WeightedIntervalAnalyzer:
    """Element-weighted interpretations over canonical poset intervals."""

    def __init__(self, weighted_poset):
        self.weighted_poset = weighted_poset
        self.base = PosetAnalyzer(weighted_poset.poset)

    def element_sum(
        self,
        x: str,
        y: str,
        config: IntervalConfig = IntervalConfig.closed(),
    ):
        """Return the element-weight sum over [x, y] with configured endpoints."""
        return sum(
            self.weighted_poset.element_weight(element)
            for element in self.base.interval(x, y)
            if self._includes_element(element, x, y, config)
        )

    def _includes_element(
        self,
        element: str,
        left: str,
        right: str,
        config: IntervalConfig,
    ) -> bool:
        if element == left and not config.include_left:
            return False
        if element == right and not config.include_right:
            return False
        return True
