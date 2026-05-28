#[path = "../src/ideals.rs"]
mod ideals;

use ideals::{lattice_layer_sizes, IdealError};

#[test]
fn lattice_layer_sizes_for_diamond_match_order_ideal_layers() {
    assert_eq!(
        lattice_layer_sizes(4, vec![(0, 1), (0, 2), (1, 3), (2, 3)]).unwrap(),
        vec![1, 1, 2, 1, 1],
    );
}

#[test]
fn lattice_layer_sizes_for_antichain_match_binomial_layers() {
    assert_eq!(
        lattice_layer_sizes(4, vec![]).unwrap(),
        vec![1, 4, 6, 4, 1],
    );
}

#[test]
fn lattice_layer_sizes_rejects_out_of_range_edges() {
    assert_eq!(
        lattice_layer_sizes(2, vec![(0, 2)]),
        Err(IdealError::OutOfRange),
    );
}

#[test]
fn lattice_layer_sizes_rejects_edges_outside_topological_order() {
    assert_eq!(
        lattice_layer_sizes(2, vec![(1, 0)]),
        Err(IdealError::NotTopological),
    );
}
