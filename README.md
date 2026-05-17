# Poset Explorer

A lightweight exploratory framework for studying finite partially
ordered sets (posets), dependency structures, and their combinatorial
behavior.

The project focuses on linear extensions, order ideals, workflow
families, and traversal structure in constrained systems modeled as
directed acyclic graphs (DAGs). 

> This project is currently an exploratory research-oriented
> implementation under active development.

## Purpose, AI use & Conceptual ownership

This project doubles as a self-apprenticeship in algorithmic thinking, software architecture, and best practices. This project is also being used to test how well I can leverage AI's strengths without losing cognitive agency.

All algorithms are reconstructed through first principles, then sent to AI to speed up cross-checking against known and verified algorithms, and help provide both formal vocabulary and relevant literature. Mathematical reasoning originates from my own understanding, and final architectural decisions are done by me. 

## Current Capabilities

- **Poset construction and validation**  
  Hasse diagram representation with cycle detection and parent/child adjacency maps.

- **Poset factories for known families**  
  Built-in constructors for well-known benchmark poset families

- **Exact linear-extension enumeration**  
  Memoized recursion over dual order ideals (O(2^n) worst-case).

- **Order-ideal traversal and lattice-layer analysis**  
  Groups ideals by rank to visualize the structure of the distributive lattice J(P).

- **Mobius function and inversion utilities**  
  Computes interval Mobius values and supports zeta transforms with Mobius inversion.

- **Compact interval and Mobius summaries**  
  Reports aggregate interval and Mobius statistics without returning full matrices by default.

## Research Focus

Current work centers on:

- exact linear-extension counting,
- traversal of order ideals,
- lattice-layer analysis,
- Mobius inversion and incidence-style poset invariants,
- structural memoization strategies for repeated subproblems,
- exploring canonical workflow families,
- and eventually providing ML-usable feature vectors.

## Running Tests

Activate the virtual environment and run:
```
pytest
```
## Documentation

See `docs/workflow_families.md` for canonical structural benchmark families and motivating examples.
See `docs/logs` for session summaries and `docs/transcripts` for raw curated transcripts of sessions. 

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
