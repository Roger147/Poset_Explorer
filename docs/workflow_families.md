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

A → B → C → D

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

A   B   C   D

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

    A
   / \
  B   C
   \ /
    D

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