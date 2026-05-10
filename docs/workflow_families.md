# Structural Workflow Families

This document catalogs recurring dependency structures used as benchmark
families and motivating examples throughout the project.

The goal is not to model real-world systems in full fidelity, but to study
structurally meaningful workflow patterns that arise in constrained task
systems. Each family highlights a canonical dependency motif and its
combinatorial behavior.

Each family includes:
- a structural description,
- a canonical dependency pattern,
- an intuitive interpretation,
- and notes about combinatorial behavior.

---

## Chains

### Canonical Structure

```
A → B → C → D
```

### Structural Meaning

Minimal scheduling flexibility.
Each task depends entirely on the previous one, yielding a single valid
execution order.

### Canonical Analogies
- Sequential manufacturing or staged chemical preparation.
- Fixed-route transit schedules where each stop must occur in sequence.

### Mathematical Notes
- Exactly one linear extension.
- Maximal dependency concentration.
- No branching behavior.

---

## Anti-Chains

### Canonical Structure

```
A   B   C   D
```
(no dependency relations)

### Structural Meaning
Maximum scheduling flexibility.  
All tasks are independent and may be completed in any order.

### Canonical Analogies
- Independent preprocessing jobs in distributed computing.
- Completing a checklist or recording attendance.

### Mathematical Notes
- Number of linear extensions grows factorially.
- Maximal symmetry.
- Serves as an upper-flexibility benchmark.

---

## Diamond Structures

### Canonical Structure
```
    A
   / \
  B   C
   \ /
    D
```
### Structural Meaning
A fork–join synchronization pattern.  
A single task branches into partially independent subtasks that later
reconverge.

### Canonical Analogies
- Parallel analyses that must both complete before final aggregation.
- Approval → parallel work → final report pipelines.

### Mathematical Notes
- Local branching with constrained reconvergence.
- Small but nontrivial flexibility.
- Useful benchmark for synchronization bottlenecks.

## N-Posets

### Canonical Structure

```
  A   C
   \ / \
    B   D
```

### Structural Meaning
An asymmetric dependency structure where a shared prerequisite participates
in multiple partially overlapping constraint paths. Unlike a diamond,
dependencies do not cleanly diverge and reconverge, producing more entangled
execution relationships.

### Canonical Analogies
- A required document or approval feeding multiple partially independent
  administrative chains.
- A signoff process where B depends on both A and C, while C must also
  complete D for a separate requirement.

### Mathematical Notes
- Related to zig-zag and fence-style posets.
- Exhibits alternating up–down dependency patterns.
- Minimal asymmetric motif with intertwined constraint paths.
- More entangled than chains, anti-chains, or symmetric diamonds.

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
- and at least one pair Cₓ, Cᵧ satisfies length(Cₓ) ≠ length(Cᵧ)
```

### Structural Meaning
Multiple upstream chains of unequal depth feed into a shared downstream
constraint. These structures highlight how uneven dependency interactions
influence traversal flexibility and ideal-growth behavior.

### Canonical Analogies
- Multi-stage approval processes where some prerequisite pipelines are
  substantially deeper than others.
- Workflows where a final task depends on several pipelines of differing
  complexity.

### Mathematical Notes
- Represents uneven convergence into a shared upper constraint.
- Useful for studying irregular ideal growth and memoization-sensitive
  traversal behavior.
- Demonstrates how globally complex behavior can emerge from simple local
  components.
- Related to convergent and layered dependency structures in finite posets.

## Crown Posets

### Canonical Structure

```text
 a₁    a₂    a₃
 |\    /\    /|
 | \  /  \  / |
 |  \/    \/  |
 |  /\    /\  |
 | /  \  /  \ |
 |/    \/    \|
 b₃    b₂    b₁
```

### Structural Meaning

Crown posets form a height‑2 structure where each maximal element depends on all but one minimal element, creating a dense web of overlapping constraints. Their alternating exclusion pattern produces a highly symmetric, non‑hierarchical dependency shape that resists simple decomposition.

### Canonical Analogies

- Peer review systems where each reviewer may evaluate every submission
  except their own.

### Mathematical Notes
- Non–series–parallel; canonical minimal example of a poset that cannot be decomposed into series or parallel components.
- High symmetry; strong automorphism structure with uniform behavior across all indices.
- Classical family; well‑studied benchmark object in combinatorics and extremal poset theory.