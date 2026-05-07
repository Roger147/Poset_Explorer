# Workflow Dependency Structure Analyzer

A framework for analyzing how dependency constraints affect the flexibility and structure of possible workflows.

The project models workflows as dependency structures (partially ordered sets/DAGs) and studies valid execution orders through combinatorial enumeration techniques.

## Current status
- Poset construction and validation implemented
- Exact linear-extension enumeration implemented
- Order-ideal layer analysis implemented

## Current work focuses on:

- exact linear-extension counting,
- traversal of order ideals,
- lattice-layer analysis,
- and structural memoization strategies for repeated subproblems.

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
