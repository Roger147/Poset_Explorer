use std::collections::HashMap;

#[derive(Debug, Eq, PartialEq)]
pub enum ExtensionError {
    TooManyElements,
    OutOfRange,
    NotTopological,
    CountOverflow,
    StateLimitExceeded,
}

pub fn linear_extension_count(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
    max_states: Option<usize>,
) -> Result<u128, ExtensionError> {
    if num_elements > 128 {
        return Err(ExtensionError::TooManyElements);
    }

    let predecessor_masks = predecessor_masks(num_elements, cover_edges)?;
    let remaining = mask_for_size(num_elements);
    let mut memo = HashMap::new();

    count_remaining(remaining, &predecessor_masks, &mut memo, max_states)
}

fn count_remaining(
    remaining: u128,
    predecessor_masks: &[u128],
    memo: &mut HashMap<u128, u128>,
    max_states: Option<usize>,
) -> Result<u128, ExtensionError> {
    if remaining == 0 {
        return Ok(1);
    }

    if let Some(count) = memo.get(&remaining) {
        return Ok(*count);
    }
    if let Some(limit) = max_states {
        if memo.len() >= limit {
            return Err(ExtensionError::StateLimitExceeded);
        }
    }

    let mut total = 0_u128;

    for element_index in 0..predecessor_masks.len() {
        let element_bit = 1_u128 << element_index;

        if remaining & element_bit == 0 {
            continue;
        }
        if predecessor_masks[element_index] & remaining != 0 {
            continue;
        }

        let next_remaining = remaining ^ element_bit;
        let branch_count = count_remaining(next_remaining, predecessor_masks, memo, max_states)?;
        total = total
            .checked_add(branch_count)
            .ok_or(ExtensionError::CountOverflow)?;
    }

    memo.insert(remaining, total);
    Ok(total)
}

fn predecessor_masks(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> Result<Vec<u128>, ExtensionError> {
    let mut predecessor_masks = vec![0_u128; num_elements];

    for (source, target) in cover_edges {
        if source >= num_elements || target >= num_elements {
            return Err(ExtensionError::OutOfRange);
        }
        if source >= target {
            return Err(ExtensionError::NotTopological);
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
