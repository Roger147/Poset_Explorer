"""Transitive-closure backend helpers.

This module keeps closure computation on integer indices. The public analyzer
can map results back to element labels, while a future Rust implementation can
replace this backend without changing analyzer-facing behavior.
"""

from collections.abc import Iterable

DEFAULT_LINEAR_EXTENSION_STATE_LIMIT = 1_000_000

try:
    from _poset_explorer_rust import (
        interval_summary_data as _rust_interval_summary_data,
        lattice_layer_sizes as _rust_lattice_layer_sizes,
        linear_extension_count_data as _rust_linear_extension_count_data,
        mobius_matrix_data as _rust_mobius_matrix_data,
        principal_ideal_filter_sizes as _rust_principal_ideal_filter_sizes,
        strict_zeta_transform_data as _rust_strict_zeta_transform_data,
        transitive_successor_closure as _rust_transitive_successor_closure,
        width_data as _rust_width_data,
        zeta_summary_data as _rust_zeta_summary_data,
        zeta_transform_data as _rust_zeta_transform_data,
    )
except ImportError:
    _rust_interval_summary_data = None
    _rust_lattice_layer_sizes = None
    _rust_linear_extension_count_data = None
    _rust_mobius_matrix_data = None
    _rust_principal_ideal_filter_sizes = None
    _rust_strict_zeta_transform_data = None
    _rust_transitive_successor_closure = None
    _rust_width_data = None
    _rust_zeta_summary_data = None
    _rust_zeta_transform_data = None


def transitive_successor_closure(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> list[set[int]]:
    """
    Return strict successor closure sets for an indexed DAG.

    Element indices are expected to follow a topological order, so every cover
    edge has source < target.
    """
    cover_edges = list(cover_edges)
    if _rust_transitive_successor_closure is not None:
        return [
            set(successors)
            for successors in _rust_transitive_successor_closure(
                num_elements,
                cover_edges,
            )
        ]

    return _python_transitive_successor_closure(num_elements, cover_edges)


def principal_ideal_filter_sizes(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> tuple[list[int], list[int]]:
    """Return reflexive principal ideal and filter sizes for an indexed DAG."""
    cover_edges = list(cover_edges)
    if _rust_principal_ideal_filter_sizes is not None:
        ideal_sizes, filter_sizes = _rust_principal_ideal_filter_sizes(
            num_elements,
            cover_edges,
        )
        return list(ideal_sizes), list(filter_sizes)

    closure = _python_transitive_successor_closure(num_elements, cover_edges)
    return principal_ideal_filter_sizes_from_closure(num_elements, closure)


def principal_ideal_filter_sizes_from_closure(
    num_elements: int,
    closure: list[set[int]],
) -> tuple[list[int], list[int]]:
    """Return reflexive principal ideal and filter sizes from strict closure."""
    ideal_sizes = [1] * num_elements
    filter_sizes = [1] * num_elements

    for source_index, successors in enumerate(closure):
        filter_sizes[source_index] += len(successors)
        for target_index in successors:
            ideal_sizes[target_index] += 1

    return ideal_sizes, filter_sizes


def zeta_summary_data(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> tuple[int, list[int], list[int]]:
    """
    Return strict comparability count and principal sizes for zeta summaries.
    """
    cover_edges = list(cover_edges)
    if _rust_zeta_summary_data is not None:
        strict_count, ideal_sizes, filter_sizes = _rust_zeta_summary_data(
            num_elements,
            cover_edges,
        )
        return strict_count, list(ideal_sizes), list(filter_sizes)

    closure = _python_transitive_successor_closure(num_elements, cover_edges)
    ideal_sizes, filter_sizes = principal_ideal_filter_sizes_from_closure(
        num_elements,
        closure,
    )
    return sum(len(successors) for successors in closure), ideal_sizes, filter_sizes


def zeta_transform_data(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
    values: Iterable[int | float],
) -> list[float]:
    """
    Return closed zeta transform totals through an f64-compatible data path.
    """
    cover_edges = list(cover_edges)
    value_vector = [float(value) for value in values]
    if len(value_vector) != num_elements:
        raise ValueError("value vector length must match the element count")

    if _rust_zeta_transform_data is not None:
        return list(_rust_zeta_transform_data(num_elements, cover_edges, value_vector))

    closure = _python_transitive_successor_closure(num_elements, cover_edges)
    return _python_zeta_transform(num_elements, closure, value_vector)


def strict_zeta_transform_data(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
    values: Iterable[int | float],
) -> list[float]:
    """
    Return strict zeta transform totals through an f64-compatible data path.
    """
    cover_edges = list(cover_edges)
    value_vector = [float(value) for value in values]
    if len(value_vector) != num_elements:
        raise ValueError("value vector length must match the element count")

    if _rust_strict_zeta_transform_data is not None:
        return list(
            _rust_strict_zeta_transform_data(num_elements, cover_edges, value_vector)
        )

    closure = _python_transitive_successor_closure(num_elements, cover_edges)
    return _python_strict_zeta_transform(num_elements, closure, value_vector)


def lattice_layer_sizes(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> list[int]:
    """Return order-ideal lattice layer sizes for an indexed DAG."""
    cover_edges = list(cover_edges)
    if _rust_lattice_layer_sizes is not None:
        return list(_rust_lattice_layer_sizes(num_elements, cover_edges))

    return _python_lattice_layer_sizes(num_elements, cover_edges)


def width_data(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> int:
    """Return poset width from strict transitive comparability matching."""
    cover_edges = list(cover_edges)
    if _rust_width_data is not None:
        return _rust_width_data(num_elements, cover_edges)

    closure = _python_transitive_successor_closure(num_elements, cover_edges)
    return _python_width(num_elements, closure)


def linear_extension_count_data(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
    max_states: int | None = DEFAULT_LINEAR_EXTENSION_STATE_LIMIT,
) -> int:
    """Return the number of linear extensions using bitmask memoization."""
    cover_edges = list(cover_edges)
    if num_elements > 128:
        raise ValueError(
            "linear extension counting currently supports at most 128 elements"
        )

    if _rust_linear_extension_count_data is not None:
        return _rust_linear_extension_count_data(num_elements, cover_edges, max_states)

    return _python_linear_extension_count(num_elements, cover_edges, max_states)


def interval_summary_data(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> dict:
    """Return compact closed-interval summary data for an indexed DAG."""
    cover_edges = list(cover_edges)
    if _rust_interval_summary_data is not None:
        (
            num_intervals,
            num_trivial,
            num_nontrivial,
            num_cover,
            min_size,
            max_size,
            mean_size,
            histogram,
        ) = _rust_interval_summary_data(num_elements, cover_edges)
        return _format_interval_summary(
            num_intervals,
            num_trivial,
            num_nontrivial,
            num_cover,
            min_size,
            max_size,
            mean_size,
            dict(histogram),
        )

    closure = _python_transitive_successor_closure(num_elements, cover_edges)
    interval_sizes = _python_interval_sizes(num_elements, closure)
    return _interval_summary_from_sizes(interval_sizes)


def mobius_matrix_data(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> list[list[int]]:
    """Return indexed Mobius values for every ordered pair in an indexed DAG."""
    cover_edges = list(cover_edges)
    if _rust_mobius_matrix_data is not None:
        return [
            list(row)
            for row in _rust_mobius_matrix_data(num_elements, cover_edges)
        ]

    closure = _python_transitive_successor_closure(num_elements, cover_edges)
    return _python_mobius_matrix(num_elements, closure)


def _python_transitive_successor_closure(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> list[set[int]]:
    children: list[list[int]] = [[] for _ in range(num_elements)]
    for source, target in cover_edges:
        children[source].append(target)

    closure: list[set[int]] = [set() for _ in range(num_elements)]
    for source in reversed(range(num_elements)):
        for child in children[source]:
            closure[source].add(child)
            closure[source].update(closure[child])

    return closure


def _python_lattice_layer_sizes(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
) -> list[int]:
    predecessor_sets = [set() for _ in range(num_elements)]
    for source, target in cover_edges:
        predecessor_sets[target].add(source)

    layer_sizes = []
    current_layer = {frozenset()}

    while current_layer:
        layer_sizes.append(len(current_layer))
        next_layer = set()

        for ideal in current_layer:
            for element_index in range(num_elements):
                if element_index in ideal:
                    continue
                if not predecessor_sets[element_index].issubset(ideal):
                    continue

                next_layer.add(frozenset((*ideal, element_index)))

        current_layer = next_layer

    return layer_sizes


def _python_zeta_transform(
    num_elements: int,
    closure: list[set[int]],
    values: list[float],
) -> list[float]:
    transformed = []

    for target in range(num_elements):
        total = values[target] + sum(
            values[source]
            for source in range(target)
            if target in closure[source]
        )
        transformed.append(total)

    return transformed


def _python_strict_zeta_transform(
    num_elements: int,
    closure: list[set[int]],
    values: list[float],
) -> list[float]:
    transformed = []

    for target in range(num_elements):
        total = sum(
            values[source]
            for source in range(target)
            if target in closure[source]
        )
        transformed.append(total)

    return transformed


def _python_width(
    num_elements: int,
    closure: list[set[int]],
) -> int:
    matched_right_to_left: dict[int, int] = {}

    def can_match(left: int, visited_right: set[int]) -> bool:
        for right in sorted(closure[left]):
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
    for left in range(num_elements):
        if can_match(left, set()):
            matching_size += 1

    return num_elements - matching_size


def _python_linear_extension_count(
    num_elements: int,
    cover_edges: Iterable[tuple[int, int]],
    max_states: int | None,
) -> int:
    predecessor_masks = [0 for _ in range(num_elements)]
    for source, target in cover_edges:
        if source >= num_elements or target >= num_elements:
            raise ValueError("cover edge index is outside the element range")
        if source >= target:
            raise ValueError("cover edge indices must follow topological order")

        predecessor_masks[target] |= 1 << source

    memo: dict[int, int] = {}
    remaining = (1 << num_elements) - 1

    def count(remaining_mask: int) -> int:
        if remaining_mask == 0:
            return 1

        if remaining_mask in memo:
            return memo[remaining_mask]
        if max_states is not None and len(memo) >= max_states:
            raise ValueError("linear extension state limit was exceeded")

        total = 0
        for element_index in range(num_elements):
            element_bit = 1 << element_index
            if remaining_mask & element_bit == 0:
                continue
            if predecessor_masks[element_index] & remaining_mask != 0:
                continue

            total += count(remaining_mask ^ element_bit)

        if total > (1 << 128) - 1:
            raise ValueError("linear extension count exceeded u128")

        memo[remaining_mask] = total
        return total

    return count(remaining)


def _python_interval_sizes(
    num_elements: int,
    closure: list[set[int]],
) -> list[int]:
    interval_sizes = []

    for left in range(num_elements):
        interval_sizes.append(1)

        for right in sorted(closure[left]):
            size = sum(
                (middle == left or middle in closure[left])
                and (middle == right or right in closure[middle])
                for middle in range(num_elements)
            )
            interval_sizes.append(size)

    return interval_sizes


def _python_mobius_matrix(
    num_elements: int,
    closure: list[set[int]],
) -> list[list[int]]:
    matrix = [[0 for _ in range(num_elements)] for _ in range(num_elements)]

    for left in range(num_elements):
        matrix[left][left] = 1

        for right in range(left + 1, num_elements):
            if right not in closure[left]:
                continue

            total = sum(
                matrix[left][middle]
                for middle in range(left, right)
                if (
                    (middle == left or middle in closure[left])
                    and right in closure[middle]
                )
            )
            matrix[left][right] = -total

    return matrix


def _interval_summary_from_sizes(interval_sizes: list[int]) -> dict:
    if not interval_sizes:
        return _format_interval_summary(0, 0, 0, 0, 0, 0, 0, {})

    return _format_interval_summary(
        len(interval_sizes),
        sum(size == 1 for size in interval_sizes),
        sum(size > 1 for size in interval_sizes),
        sum(size == 2 for size in interval_sizes),
        min(interval_sizes),
        max(interval_sizes),
        sum(interval_sizes) / len(interval_sizes),
        _histogram(interval_sizes),
    )


def _format_interval_summary(
    num_intervals: int,
    num_trivial: int,
    num_nontrivial: int,
    num_cover: int,
    min_size: int,
    max_size: int,
    mean_size: float,
    histogram: dict[int, int],
) -> dict:
    return {
        "num_intervals": num_intervals,
        "num_trivial_intervals": num_trivial,
        "num_nontrivial_intervals": num_nontrivial,
        "num_cover_intervals": num_cover,
        "min_interval_size": min_size,
        "max_interval_size": max_size,
        "mean_interval_size": mean_size,
        "interval_size_histogram": histogram,
    }


def _histogram(values: list[int]) -> dict[int, int]:
    return {
        value: values.count(value)
        for value in sorted(set(values))
    }
