# Structural Workflow Families

This document catalogs recurring dependency structures used as benchmark
families and motivating examples throughout the project.

The goal is not to fully model real-world systems, but to study
structurally meaningful workflow patterns that appear in constrained
task systems.

Each family includes:
- a structural description,
- a canonical dependency pattern,
- an intuitive interpretation,
- and notes about combinatorial behavior.

---

## Chains

### Canonical Structure

```text
A → B → C → D
```

### Structural Meaning

Minimal scheduling flexibility.

Each task depends entirely on the completion of the previous task,
creating a single valid execution order.

### Canonical Analogy

- Sequential manufacturing pipelines or staged chemical preparation procedures.
- Basic train or bus schedule: in particular, a fixed route where each stop must occur in sequence. 

### Mathematical Notes

- Exactly one linear extension
- Maximal dependency concentration
- Minimal branching behavior

---

## Anti-Chains

### Canonical Structure

```text
A   B   C   D
```

(no dependency relations)

### Structural Meaning

Maximum scheduling flexibility.

All tasks may be completed in arbitrary order.

### Canonical Analogy

- Independent preprocessing jobs in a distributed compute environment.
- Recording attendance in a single classroom, or completing a grocery checklist.

### Mathematical Notes

- Number of linear extensions grows factorially
- Maximal symmetry
- Useful as an upper-flexibility benchmark

---

## Diamond Structures

### Canonical Structure
```text

    A
   / \
  B   C
   \ /
    D

```
### Structural Meaning

Fork-join synchronization structure.

A single task branches into partially independent subtasks that later
reconverge.

### Canonical Analogy

- Parallel experimental analyses that must both complete before final aggregation or reporting.
- The pipeline of approving funding, doing separate work or experiments, then combining into a final report.

### Mathematical Notes

- Local branching with constrained reconvergence
- Small but nontrivial flexibility
- Useful benchmark for synchronization bottlenecks

## N-Posets

### Canonical Structure

```text
  A   C
   \ / \
    B   D
```

### Structural Meaning

An asymmetric dependency structure where a shared prerequisite
participates in multiple partially overlapping constraint paths.
Unlike a diamond structure, the dependencies do not cleanly diverge
and reconverge, creating more entangled execution relationships.

### Canonical Analogies

- Bureaucratic approval systems where one office or document is required for multiple partially independent approval chains.
- A signoff process where approval B requires work from both A and C, while C must also independently complete approval D for a separate administrative requirement.

### Mathematical Notes

- Related to classical zig-zag and fence-style poset structures.
- Connected to up-down (alternating) dependency patterns in finite posets.
- Represents a minimal asymmetric dependency motif with intertwined constraint paths.
- Structurally more entangled than chains, anti-chains, or symmetric diamond structures.

## Asymmetric Convergence

### Canonical Structure

```text
C₁ → z
C₂ → z
⋮
Cᵢ → z

where:
- each Cᵢ is a chain,
- all chains converge into a shared upper element z,
- and there exists at least one pair Cₓ, Cᵧ such that:
length(Cₓ) ≠ length(Cᵧ)
```

### Structural Meaning

A convergent dependency structure in which multiple upstream chains of unequal depth feed into a shared downstream constraint.

Asymmetric convergence structures are useful for studying how uneven dependency interactions may influence traversal flexibility and ideal-growth behavior, particularly when multiple convergence regions overlap or interact.

### Canonical Analogies

- Bureaucratic approval systems where multiple independent approval paths converge into a final authorization step, but some approval chains require substantially more intermediate processing than others.
- Multi-stage workflows in which a shared downstream task depends on several prerequisite pipelines of differing complexity or depth.

### Mathematical Notes

- Represents uneven convergence into a shared upper constraint.
- Useful as a benchmark motif for studying irregular ideal growth and memoization-sensitive traversal behavior.
- Highlights how globally difficult traversal behavior can emerge from relatively simple local dependency components.
- Related to convergent and layered dependency structures in finite partial orders and DAGs.