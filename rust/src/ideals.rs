#[derive(Debug, Eq, PartialEq)]
pub enum IdealError {
    TooManyElements,
    OutOfRange,
    NotTopological,
}

pub fn lattice_layer_sizes(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> Result<Vec<usize>, IdealError> {
    if num_elements > 128 {
        return Err(IdealError::TooManyElements);
    }

    let predecessor_masks = predecessor_masks(num_elements, cover_edges)?;
    let full_mask = mask_for_size(num_elements);
    let mut layer_sizes = Vec::new();
    let mut current_layer = vec![0_u128];

    while !current_layer.is_empty() {
        layer_sizes.push(current_layer.len());
        let mut next_layer = Vec::new();

        for ideal in current_layer {
            for element_index in 0..num_elements {
                let element_bit = 1_u128 << element_index;

                if ideal & element_bit != 0 {
                    continue;
                }
                if predecessor_masks[element_index] & !ideal != 0 {
                    continue;
                }

                next_layer.push(ideal | element_bit);
            }
        }

        next_layer.sort_unstable();
        next_layer.dedup();
        next_layer.retain(|ideal| *ideal <= full_mask);
        current_layer = next_layer;
    }

    Ok(layer_sizes)
}

fn predecessor_masks(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> Result<Vec<u128>, IdealError> {
    let mut predecessor_masks = vec![0_u128; num_elements];

    for (source, target) in cover_edges {
        if source >= num_elements || target >= num_elements {
            return Err(IdealError::OutOfRange);
        }
        if source >= target {
            return Err(IdealError::NotTopological);
        }

        predecessor_masks[target] |= 1_u128 << source;
    }

    Ok(predecessor_masks)
}

fn mask_for_size(num_elements: usize) -> u128 {
    if num_elements == 128 {
        u128::MAX
    } else {
        (1_u128 << num_elements) - 1
    }
}
