"""Constructors for canonical benchmark poset families.

Future benchmark metadata, such as family names and construction parameters,
should live near these factories. Structural measurements should still be
computed by analyzers from the resulting Poset so custom posets are comparable.
"""

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


def asymmetric_convergence(lengths: list[int]) -> Poset:
    """
    Return disjoint chains of unequal positive lengths converging into z.

    A length-k branch has elements c{i}_1 < ... < c{i}_k < z.
    """
    if len(lengths) < 2:
        raise ValueError("asymmetric convergence requires at least two chains.")
    if any(length <= 0 for length in lengths):
        raise ValueError("chain lengths must be positive.")
    if len(set(lengths)) == 1:
        raise ValueError("at least two chain lengths must differ.")

    elements = {"z"}
    relations: list[tuple[str, str]] = []

    for branch_index, length in enumerate(lengths, start=1):
        labels = [f"c{branch_index}_{level}" for level in range(1, length + 1)]
        elements.update(labels)
        relations.extend(zip(labels, labels[1:]))
        relations.append((labels[-1], "z"))

    return Poset(elements, relations)


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
