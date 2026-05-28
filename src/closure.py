"""Transitive-closure backend helpers.

This module keeps closure computation on integer indices. The public analyzer
can map results back to element labels, while a future Rust implementation can
replace this backend without changing analyzer-facing behavior.
"""

from collections.abc import Iterable

try:
    from _poset_explorer_rust import (
        principal_ideal_filter_sizes as _rust_principal_ideal_filter_sizes,
        transitive_successor_closure as _rust_transitive_successor_closure,
        zeta_summary_data as _rust_zeta_summary_data,
    )
except ImportError:
    _rust_principal_ideal_filter_sizes = None
    _rust_transitive_successor_closure = None
    _rust_zeta_summary_data = None


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
