#[allow(dead_code)]
#[path = "../src/closure.rs"]
mod closure;
#[path = "../src/weighted.rs"]
mod weighted;

use closure::transitive_successor_closure_bitsets;
use weighted::{max_antichain_score_from_bitsets, WeightedError};

#[test]
fn max_antichain_score_finds_weighted_diamond_middle_layer() {
    let closure =
        transitive_successor_closure_bitsets(4, vec![(0, 1), (0, 2), (1, 3), (2, 3)]).unwrap();

    assert_eq!(
        max_antichain_score_from_bitsets(4, &closure, &[1.0, 10.0, 20.0, 1.0]).unwrap(),
        30.0,
    );
}

#[test]
fn max_antichain_score_uses_transitive_comparability() {
    let closure = transitive_successor_closure_bitsets(3, vec![(0, 1), (1, 2)]).unwrap();

    assert_eq!(
        max_antichain_score_from_bitsets(3, &closure, &[100.0, 1.0, 100.0]).unwrap(),
        100.0,
    );
}

#[test]
fn max_antichain_score_ignores_negative_scores() {
    let closure = transitive_successor_closure_bitsets(3, vec![]).unwrap();

    assert_eq!(
        max_antichain_score_from_bitsets(3, &closure, &[10.0, -100.0, 10.0]).unwrap(),
        20.0,
    );
    assert_eq!(
        max_antichain_score_from_bitsets(3, &closure, &[-1.0, -2.0, -3.0]).unwrap(),
        0.0,
    );
}

#[test]
fn max_antichain_score_rejects_nonfinite_scores() {
    let closure = transitive_successor_closure_bitsets(1, vec![]).unwrap();

    assert_eq!(
        max_antichain_score_from_bitsets(1, &closure, &[f64::NAN]),
        Err(WeightedError::InvalidWeight),
    );
}
