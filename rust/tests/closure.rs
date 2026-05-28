#[path = "../src/closure.rs"]
mod closure;

use closure::{
    bitsets_to_index_lists, interval_summary_data_from_bitsets, principal_sizes_from_bitsets,
    transitive_successor_closure_bitsets, zeta_summary_data_from_bitsets, ClosureError,
};

#[test]
fn closure_uses_bitsets_for_transitive_successors() {
    let closure = transitive_successor_closure_bitsets(
        4,
        vec![(0, 1), (0, 2), (1, 3), (2, 3)],
    )
    .unwrap();

    assert_eq!(
        bitsets_to_index_lists(4, &closure),
        vec![vec![1, 2, 3], vec![3], vec![3], vec![]],
    );
}

#[test]
fn closure_bitsets_span_multiple_words() {
    let closure = transitive_successor_closure_bitsets(66, vec![(0, 65)]).unwrap();

    assert_eq!(bitsets_to_index_lists(66, &closure)[0], vec![65]);
}

#[test]
fn closure_rejects_out_of_range_edges() {
    assert_eq!(
        transitive_successor_closure_bitsets(2, vec![(0, 2)]),
        Err(ClosureError::OutOfRange),
    );
}

#[test]
fn closure_rejects_edges_outside_topological_order() {
    assert_eq!(
        transitive_successor_closure_bitsets(2, vec![(1, 0)]),
        Err(ClosureError::NotTopological),
    );
}

#[test]
fn principal_sizes_count_reflexive_ideal_and_filter_members() {
    let closure = transitive_successor_closure_bitsets(
        4,
        vec![(0, 1), (0, 2), (1, 3), (2, 3)],
    )
    .unwrap();

    assert_eq!(
        principal_sizes_from_bitsets(4, &closure),
        (vec![1, 2, 2, 4], vec![4, 2, 2, 1]),
    );
}

#[test]
fn zeta_summary_data_counts_strict_comparabilities_and_principal_sizes() {
    let closure = transitive_successor_closure_bitsets(
        4,
        vec![(0, 1), (0, 2), (1, 3), (2, 3)],
    )
    .unwrap();

    assert_eq!(
        zeta_summary_data_from_bitsets(4, &closure),
        (5, vec![1, 2, 2, 4], vec![4, 2, 2, 1]),
    );
}

#[test]
fn interval_summary_data_counts_closed_interval_features() {
    let closure = transitive_successor_closure_bitsets(
        4,
        vec![(0, 1), (0, 2), (1, 3), (2, 3)],
    )
    .unwrap();

    assert_eq!(
        interval_summary_data_from_bitsets(4, &closure),
        (9, 4, 5, 4, 1, 4, 16.0 / 9.0, vec![(1, 4), (2, 4), (4, 1)]),
    );
}
