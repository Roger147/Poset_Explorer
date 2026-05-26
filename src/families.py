"""Constructors for canonical benchmark poset families.

Future benchmark metadata, such as family names and construction parameters,
should live near these factories. Structural measurements should still be
computed by analyzers from the resulting Poset so custom posets are comparable.
"""

from itertools import combinations

from poset import Poset


def _indexed_labels(prefix: str, n: int) -> list[str]:
    if n < 0:
        raise ValueError("n must be nonnegative.")
    return [f"{prefix}{i}" for i in range(1, n + 1)]


def chain(n: int, prefix: str = "x") -> Poset:
    """Return the n-element chain x1 < x2 < ... < xn."""
    labels = _indexed_labels(prefix, n)
    relations = list(zip(labels, labels[1:]))
    return Poset(set(labels), relations)


def antichain(n: int, prefix: str = "x") -> Poset:
    """Return the n-element antichain with no comparability relations."""
    return Poset(set(_indexed_labels(prefix, n)), [])


def diamond() -> Poset:
    """Return the four-element diamond A < B,C < D."""
    return Poset(
        {"A", "B", "C", "D"},
        [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "D"),
        ],
    )


def n_poset() -> Poset:
    """Return the four-element N-poset with A < B, C < B, and C < D."""
    return Poset(
        {"A", "B", "C", "D"},
        [
            ("A", "B"),
            ("C", "B"),
            ("C", "D"),
        ],
    )


def crown(n: int) -> Poset:
    """
    Return the 2n-element crown poset with b_j < a_i exactly when i != j.
    """
    if n < 3:
        raise ValueError("crown posets require n >= 3.")

    lower = _indexed_labels("b", n)
    upper = _indexed_labels("a", n)
    relations = [
        (lower[j], upper[i])
        for i in range(n)
        for j in range(n)
        if i != j
    ]
    return Poset(set(lower + upper), relations)


def boolean_lattice(n: int) -> Poset:
    """Return the Boolean lattice B_n ordered by subset inclusion."""
    if n < 0:
        raise ValueError("Boolean lattice rank must be nonnegative.")

    coordinates = list(range(1, n + 1))
    subsets = [
        frozenset(combo)
        for size in range(n + 1)
        for combo in combinations(coordinates, size)
    ]
    labels = {subset: _subset_label(subset) for subset in subsets}
    relations: list[tuple[str, str]] = []

    for subset in subsets:
        for coordinate in coordinates:
            if coordinate not in subset:
                superset = frozenset(set(subset) | {coordinate})
                relations.append((labels[subset], labels[superset]))

    return Poset(set(labels.values()), relations)


def partition_lattice(n: int) -> Poset:
    """
    Return the partition lattice Pi_n ordered by refinement.

    Elements are set partitions of {1, ..., n}. Covers merge exactly two
    blocks, so the discrete partition is minimal and the one-block partition
    is maximal.
    """
    if n < 0:
        raise ValueError("Partition lattice rank must be nonnegative.")

    partitions = _set_partitions(n)
    labels = {
        partition: _partition_label(partition)
        for partition in partitions
    }
    relations: list[tuple[str, str]] = []

    for partition in partitions:
        for left_index, right_index in combinations(range(len(partition)), 2):
            merged = _merge_partition_blocks(partition, left_index, right_index)
            relations.append((labels[partition], labels[merged]))

    return Poset(set(labels.values()), relations)


def _subset_label(subset: frozenset[int]) -> str:
    if not subset:
        return "{}"
    return "{" + ", ".join(str(x) for x in sorted(subset)) + "}"


def _set_partitions(n: int) -> list[tuple[tuple[int, ...], ...]]:
    partitions = [()]

    for element in range(1, n + 1):
        next_partitions = set()

        for partition in partitions:
            next_partitions.add(_canonical_partition((*partition, (element,))))

            for block_index, block in enumerate(partition):
                blocks = list(partition)
                blocks[block_index] = tuple(sorted((*block, element)))
                next_partitions.add(_canonical_partition(blocks))

        partitions = sorted(next_partitions, key=_partition_key)

    return partitions


def _merge_partition_blocks(
    partition: tuple[tuple[int, ...], ...],
    left_index: int,
    right_index: int,
) -> tuple[tuple[int, ...], ...]:
    blocks = [
        block
        for index, block in enumerate(partition)
        if index not in {left_index, right_index}
    ]
    blocks.append(tuple(sorted((*partition[left_index], *partition[right_index]))))
    return _canonical_partition(blocks)


def _canonical_partition(
    partition,
) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted((tuple(sorted(block)) for block in partition), key=_block_key))


def _partition_key(partition: tuple[tuple[int, ...], ...]):
    return (len(partition), partition)


def _block_key(block: tuple[int, ...]) -> tuple[int, int, tuple[int, ...]]:
    return (block[0], len(block), block)


def _partition_label(partition: tuple[tuple[int, ...], ...]) -> str:
    if not partition:
        return "{}"

    return "|".join(_subset_label(frozenset(block)) for block in partition)
