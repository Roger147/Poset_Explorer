"""Transitive-closure backend helpers.

This module keeps closure computation on integer indices. The public analyzer
can map results back to element labels, while a future Rust implementation can
replace this backend without changing analyzer-facing behavior.
"""

from collections.abc import Iterable

try:
    from _poset_explorer_rust import (
        transitive_successor_closure as _rust_transitive_successor_closure,
    )
except ImportError:
    _rust_transitive_successor_closure = None


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
