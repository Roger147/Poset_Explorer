# Poset Explorer

A lightweight exploratory framework for studying finite partially
ordered sets (posets), dependency structures, and their combinatorial
behavior.

Dependencies naturally occur in many contexts: tasks that must wait for others to finish before they begin or pre-requisites that must be satisfied before work can continue. These constraints can create bottlenecks by limiting what is available when. 

These dependencies can be represented mathematically using partially ordered sets, shortened to posets. Posets are collections where individual items can be ordered relative to each other, but not enough to reduce the entire system to a single clean ordering. Posets can be represented as directed acyclic graphs, which lets us study these dependencies using combinatorial and graph-theoretical methods. 

This library focuses on exploring finite posets through dependency analysis, linear-extension enumeration, order-ideal traversal, and related combinatorial methods. From there, related structures such as incidence algebras and residual graphs emerge naturally, exposing new perspectives on the underlying posets.

> This project is currently an exploratory research-oriented
> implementation under active development.

## Current Capabilities

- **Poset construction and validation**  
  Hasse diagram representation with cycle detection and parent/child adjacency maps.

- **Poset factories for known families**  
  Built-in constructors for well-known benchmark poset families

- **Exact linear-extension enumeration**  
  Memoized recursion over dual order ideals $\mathcal{O}(2^n)$ worst-case).

- **Order-ideal traversal and lattice-layer analysis**  
  Groups ideals by rank to visualize the structure of the distributive lattice $J(P)$.

- **Zeta and Mobius incidence utilities**  
  Computes zeta and Mobius matrices, supports zeta transforms with Mobius inversion,
  and reports transitive-closure comparability summaries.

- **Compact interval, zeta, and Mobius summaries**  
  Reports aggregate interval and incidence statistics without returning full matrices by default.

- **Weighted poset wrappers**  
  Attaches element and/or edge weights without modifying the underlying poset.
  Supports both measurement and signed-score style analyses, plus element-weighted
  zeta transforms over closed principal ideals and weighted interval totals.
  

## Example Summary

The following creates a Boolean Lattice $B_2$ and runs the main analyzer summary.

```python
from analysis import PosetAnalyzer
from families import boolean_lattice


poset = boolean_lattice(2)
analyzer = PosetAnalyzer(poset)

summary = analyzer.summary()
```    
For the Boolean lattice $B_2$, `PosetAnalyzer.summary()` returns:

```python
{
    "num_elements": 4,
    "num_relations": 4,
    "num_minimals": 1,
    "num_maximals": 1,
    "height": 3,
    "width": 2,
    "num_linear_extensions": 2,
    "num_ideals": 6,
    "lattice_layer_sizes": [1, 1, 2, 1, 1],
}
```

See `test_example_usage.py` for the full suite.

## Research Focus

Current work centers on:

- exact linear-extension counting,
- traversal of order ideals,
- lattice-layer analysis,
- Mobius inversion and incidence-style poset invariants,
- structural memoization strategies for repeated subproblems,
- exploring canonical workflow families,
- and eventually providing ML-usable feature vectors.

## Repo Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

This project includes a Rust-backed transitive-closure backend built through
Maturin/PyO3. To use it, install Rust/Cargo if needed, then build the extension
into the active virtual environment:

```bash
python -m maturin develop
```

If the Rust extension is not built, the Python closure backend is used as a
fallback.

## Running Tests

Activate the virtual environment and run:
```
pytest
```

## Development Philosophy

This project doubles as a self-apprenticeship in algorithmic thinking, software architecture, and best practices. This project is also being used to test how well I can leverage AI's strengths without losing cognitive agency.

All algorithms are reconstructed through first principles, then sent to AI to speed up cross-checking against known and verified algorithms, and help provide both formal vocabulary and relevant literature. Mathematical reasoning originates from my own understanding, and final architectural decisions are done by me. 

## Documentation

See `docs/workflow_families.md` for canonical structural benchmark families and motivating examples.

See `docs/logs` for session summaries and `docs/transcripts` for raw curated transcripts of sessions. 

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
