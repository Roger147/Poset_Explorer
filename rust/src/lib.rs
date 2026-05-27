mod closure;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use closure::{
    bitsets_to_index_lists, transitive_successor_closure_bitsets, ClosureError,
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

fn closure_error_to_py_value_error(error: ClosureError) -> PyErr {
    let message = match error {
        ClosureError::OutOfRange => "cover edge index is outside the element range",
        ClosureError::NotTopological => "cover edge indices must follow topological order",
    };
    PyValueError::new_err(message)
}

#[pymodule]
fn _poset_explorer_rust(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(transitive_successor_closure, module)?)?;
    Ok(())
}
