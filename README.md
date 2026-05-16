# Poset Explorer

A lightweight exploratory framework for studying finite partially
ordered sets (posets), dependency structures, and their combinatorial
behavior.

The project focuses on linear extensions, order ideals, workflow
families, and traversal structure in constrained systems modeled as
directed acyclic graphs (DAGs).

> This project is currently an exploratory research-oriented
> implementation under active development.

## Current Capabilities

- **Poset construction and validation**  
  Hasse diagram representation with cycle detection and parent/child adjacency maps.

- **Exact linear-extension enumeration**  
  Memoized recursion over dual order ideals (O(2^n) worst-case).

- **Order-ideal traversal and lattice-layer analysis**  
  Groups ideals by rank to visualize the structure of the distributive lattice J(P).

## Research Focus

Current work centers on:

- exact linear-extension counting,
- traversal of order ideals,
- lattice-layer analysis,
- structural memoization strategies for repeated subproblems,
- and exploring canonical workflow families.

## Project Structure

```text
src/
    poset.py
    enumeration.py

tests/
    test_poset.py
    test_enumeration.py

docs/
    workflow_families.md
```

## Running Tests

Activate the virtual environment and run:

pytest

## Documentation

See `docs/workflow_families.md` for canonical structural benchmark families and motivating examples.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details
