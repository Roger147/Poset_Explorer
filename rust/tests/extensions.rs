#[path = "../src/extensions.rs"]
mod extensions;

use extensions::{linear_extension_count, ExtensionError};

#[test]
fn linear_extension_count_handles_standard_shapes() {
    assert_eq!(
        linear_extension_count(4, vec![(0, 1), (1, 2), (2, 3)], None).unwrap(),
        1,
    );
    assert_eq!(linear_extension_count(4, vec![], None).unwrap(), 24);
    assert_eq!(
        linear_extension_count(4, vec![(0, 1), (0, 2), (1, 3), (2, 3)], None,).unwrap(),
        2,
    );
}

#[test]
fn linear_extension_count_rejects_too_many_elements() {
    assert_eq!(
        linear_extension_count(129, vec![], None),
        Err(ExtensionError::TooManyElements),
    );
}

#[test]
fn linear_extension_count_rejects_out_of_range_edges() {
    assert_eq!(
        linear_extension_count(2, vec![(0, 2)], None),
        Err(ExtensionError::OutOfRange),
    );
}

#[test]
fn linear_extension_count_rejects_edges_outside_topological_order() {
    assert_eq!(
        linear_extension_count(2, vec![(1, 0)], None),
        Err(ExtensionError::NotTopological),
    );
}

#[test]
fn linear_extension_count_rejects_excessive_state_counts() {
    assert_eq!(
        linear_extension_count(4, vec![], Some(2)),
        Err(ExtensionError::StateLimitExceeded),
    );
}
