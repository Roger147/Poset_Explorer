mod closure;
mod extensions;
mod ideals;
mod weighted;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use closure::{
    bitsets_to_index_lists, interval_summary_data_from_bitsets, mobius_matrix_from_bitsets,
    principal_sizes_from_bitsets, strict_zeta_transform_from_bitsets,
    transitive_successor_closure_bitsets, width_from_bitsets, zeta_summary_data_from_bitsets,
    zeta_transform_from_bitsets, ClosureError,
};
use extensions::{linear_extension_count as rust_linear_extension_count, ExtensionError};
use ideals::{lattice_layer_sizes as rust_lattice_layer_sizes, IdealError};
use weighted::{
    max_antichain_score_from_bitsets as rust_max_antichain_score_from_bitsets, WeightedError,
};

#[pyfunction]
fn transitive_successor_closure(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<Vec<Vec<usize>>> {
    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(bitsets_to_index_lists(num_elements, &closure))
}

#[pyfunction]
fn principal_ideal_filter_sizes(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<(Vec<usize>, Vec<usize>)> {
    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(principal_sizes_from_bitsets(num_elements, &closure))
}

#[pyfunction]
fn zeta_summary_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<(usize, Vec<usize>, Vec<usize>)> {
    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(zeta_summary_data_from_bitsets(num_elements, &closure))
}

#[pyfunction]
fn zeta_transform_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
    values: Vec<f64>,
) -> PyResult<Vec<f64>> {
    if values.len() != num_elements {
        return Err(PyValueError::new_err(
            "value vector length must match the element count",
        ));
    }

    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(zeta_transform_from_bitsets(num_elements, &closure, &values))
}

#[pyfunction]
fn strict_zeta_transform_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
    values: Vec<f64>,
) -> PyResult<Vec<f64>> {
    if values.len() != num_elements {
        return Err(PyValueError::new_err(
            "value vector length must match the element count",
        ));
    }

    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(strict_zeta_transform_from_bitsets(
        num_elements,
        &closure,
        &values,
    ))
}

#[pyfunction]
fn width_data(num_elements: usize, cover_edges: Vec<(usize, usize)>) -> PyResult<usize> {
    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(width_from_bitsets(num_elements, &closure))
}

#[pyfunction]
fn max_antichain_score_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
    element_scores: Vec<f64>,
) -> PyResult<f64> {
    if element_scores.len() != num_elements {
        return Err(PyValueError::new_err(
            "score vector length must match the element count",
        ));
    }

    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    rust_max_antichain_score_from_bitsets(num_elements, &closure, &element_scores)
        .map_err(weighted_error_to_py_value_error)
}

#[pyfunction(signature = (num_elements, cover_edges, max_states=None))]
fn linear_extension_count_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
    max_states: Option<usize>,
) -> PyResult<u128> {
    rust_linear_extension_count(num_elements, cover_edges, max_states)
        .map_err(extension_error_to_py_value_error)
}

#[pyfunction]
fn interval_summary_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<(
    usize,
    usize,
    usize,
    usize,
    usize,
    usize,
    f64,
    Vec<(usize, usize)>,
)> {
    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(interval_summary_data_from_bitsets(num_elements, &closure))
}

#[pyfunction]
fn mobius_matrix_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<Vec<Vec<i64>>> {
    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(mobius_matrix_from_bitsets(num_elements, &closure))
}

#[pyfunction]
fn lattice_layer_sizes(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<Vec<usize>> {
    rust_lattice_layer_sizes(num_elements, cover_edges).map_err(ideal_error_to_py_value_error)
}

fn closure_error_to_py_value_error(error: ClosureError) -> PyErr {
    let message = match error {
        ClosureError::OutOfRange => "cover edge index is outside the element range",
        ClosureError::NotTopological => "cover edge indices must follow topological order",
    };
    PyValueError::new_err(message)
}

fn ideal_error_to_py_value_error(error: IdealError) -> PyErr {
    let message = match error {
        IdealError::TooManyElements => {
            "Rust ideal layer generation currently supports at most 128 elements"
        }
        IdealError::OutOfRange => "cover edge index is outside the element range",
        IdealError::NotTopological => "cover edge indices must follow topological order",
    };
    PyValueError::new_err(message)
}

fn extension_error_to_py_value_error(error: ExtensionError) -> PyErr {
    let message = match error {
        ExtensionError::TooManyElements => {
            "Rust linear extension counting currently supports at most 128 elements"
        }
        ExtensionError::OutOfRange => "cover edge index is outside the element range",
        ExtensionError::NotTopological => "cover edge indices must follow topological order",
        ExtensionError::CountOverflow => "linear extension count exceeded u128",
        ExtensionError::StateLimitExceeded => "linear extension state limit was exceeded",
    };
    PyValueError::new_err(message)
}

fn weighted_error_to_py_value_error(error: WeightedError) -> PyErr {
    let message = match error {
        WeightedError::InvalidWeight => "element scores must be finite numbers",
    };
    PyValueError::new_err(message)
}

#[pymodule]
fn _poset_explorer_rust(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(transitive_successor_closure, module)?)?;
    module.add_function(wrap_pyfunction!(principal_ideal_filter_sizes, module)?)?;
    module.add_function(wrap_pyfunction!(zeta_summary_data, module)?)?;
    module.add_function(wrap_pyfunction!(zeta_transform_data, module)?)?;
    module.add_function(wrap_pyfunction!(strict_zeta_transform_data, module)?)?;
    module.add_function(wrap_pyfunction!(width_data, module)?)?;
    module.add_function(wrap_pyfunction!(max_antichain_score_data, module)?)?;
    module.add_function(wrap_pyfunction!(linear_extension_count_data, module)?)?;
    module.add_function(wrap_pyfunction!(interval_summary_data, module)?)?;
    module.add_function(wrap_pyfunction!(mobius_matrix_data, module)?)?;
    module.add_function(wrap_pyfunction!(lattice_layer_sizes, module)?)?;
    Ok(())
}
