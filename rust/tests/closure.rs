#[path = "../src/closure.rs"]
mod closure;

use closure::{
    bitsets_to_index_lists, transitive_successor_closure_bitsets, ClosureError,
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
