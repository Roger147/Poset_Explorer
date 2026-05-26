use std::collections::BTreeSet;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
fn transitive_successor_closure(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> PyResult<Vec<Vec<usize>>> {
    let mut children = vec![Vec::new(); num_elements];

    for (source, target) in cover_edges {
        if source >= num_elements || target >= num_elements {
            return Err(PyValueError::new_err(
                "cover edge index is outside the element range",
            ));
        }
        if source >= target {
            return Err(PyValueError::new_err(
                "cover edge indices must follow topological order",
            ));
        }

        children[source].push(target);
    }

    let mut closure: Vec<BTreeSet<usize>> = vec![BTreeSet::new(); num_elements];

    for source in (0..num_elements).rev() {
        for child in children[source].iter().copied() {
            closure[source].insert(child);

            let child_successors: Vec<usize> = closure[child].iter().copied().collect();
            for successor in child_successors {
                closure[source].insert(successor);
            }
        }
    }

    Ok(closure
        .into_iter()
        .map(|successors| successors.into_iter().collect())
        .collect())
}

#[pymodule]
fn _poset_explorer_rust(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(transitive_successor_closure, module)?)?;
    Ok(())
}
