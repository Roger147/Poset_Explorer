mod closure;
mod ideals;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use closure::{
    bitsets_to_index_lists, interval_summary_data_from_bitsets, principal_sizes_from_bitsets,
    transitive_successor_closure_bitsets, zeta_summary_data_from_bitsets, ClosureError,
};
use ideals::{lattice_layer_sizes as rust_lattice_layer_sizes, IdealError};

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
fn interval_summary_data(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<(usize, usize, usize, usize, usize, usize, f64, Vec<(usize, usize)>)> {
    let closure = transitive_successor_closure_bitsets(num_elements, cover_edges)
        .map_err(closure_error_to_py_value_error)?;
    Ok(interval_summary_data_from_bitsets(num_elements, &closure))
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

#[pymodule]
fn _poset_explorer_rust(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(transitive_successor_closure, module)?)?;
    module.add_function(wrap_pyfunction!(principal_ideal_filter_sizes, module)?)?;
    module.add_function(wrap_pyfunction!(zeta_summary_data, module)?)?;
    module.add_function(wrap_pyfunction!(interval_summary_data, module)?)?;
    module.add_function(wrap_pyfunction!(lattice_layer_sizes, module)?)?;
    Ok(())
}
