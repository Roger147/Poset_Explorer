#[derive(Debug, Eq, PartialEq)]
pub enum ClosureError {
    OutOfRange,
    NotTopological,
}

pub fn transitive_successor_closure_bitsets(
    num_elements: usize,
    cover_edges: Vec<(usize, usize)>,
) -> Result<Vec<Vec<u64>>, ClosureError> {
    let mut children = vec![Vec::new(); num_elements];

    for (source, target) in cover_edges {
        if source >= num_elements || target >= num_elements {
            return Err(ClosureError::OutOfRange);
        }
        if source >= target {
            return Err(ClosureError::NotTopological);
        }

        children[source].push(target);
    }

    let num_words = num_elements.div_ceil(64);
    let mut closure = vec![vec![0_u64; num_words]; num_elements];

    for source in (0..num_elements).rev() {
        for child in children[source].iter().copied() {
            set_bit(&mut closure[source], child);

            for word_index in 0..num_words {
                closure[source][word_index] |= closure[child][word_index];
            }
        }
    }

    Ok(closure)
}

pub fn bitsets_to_index_lists(num_elements: usize, bitsets: &[Vec<u64>]) -> Vec<Vec<usize>> {
    bitsets
        .iter()
        .map(|bitset| {
            (0..num_elements)
                .filter(|index| bit_is_set(bitset, *index))
                .collect()
        })
        .collect()
}

pub fn principal_sizes_from_bitsets(
    num_elements: usize,
    closure: &[Vec<u64>],
) -> (Vec<usize>, Vec<usize>) {
    let mut ideal_sizes = vec![1; num_elements];
    let mut filter_sizes = vec![1; num_elements];

    for source in 0..num_elements {
        for target in 0..num_elements {
            if bit_is_set(&closure[source], target) {
                filter_sizes[source] += 1;
                ideal_sizes[target] += 1;
            }
        }
    }

    (ideal_sizes, filter_sizes)
}

pub fn zeta_summary_data_from_bitsets(
    num_elements: usize,
    closure: &[Vec<u64>],
) -> (usize, Vec<usize>, Vec<usize>) {
    let strict_comparability_count = closure
        .iter()
        .map(|bitset| {
            bitset
                .iter()
                .map(|word| word.count_ones() as usize)
                .sum::<usize>()
        })
        .sum();
    let (ideal_sizes, filter_sizes) = principal_sizes_from_bitsets(num_elements, closure);

    (strict_comparability_count, ideal_sizes, filter_sizes)
}

pub fn zeta_transform_from_bitsets(
    num_elements: usize,
    closure: &[Vec<u64>],
    values: &[f64],
) -> Vec<f64> {
    let mut transformed = vec![0.0; num_elements];

    for target in 0..num_elements {
        let mut total = values[target];

        for source in 0..target {
            if bit_is_set(&closure[source], target) {
                total += values[source];
            }
        }

        transformed[target] = total;
    }

    transformed
}

pub fn strict_zeta_transform_from_bitsets(
    num_elements: usize,
    closure: &[Vec<u64>],
    values: &[f64],
) -> Vec<f64> {
    let mut transformed = vec![0.0; num_elements];

    for target in 0..num_elements {
        let mut total = 0.0;

        for source in 0..target {
            if bit_is_set(&closure[source], target) {
                total += values[source];
            }
        }

        transformed[target] = total;
    }

    transformed
}

pub fn width_from_bitsets(num_elements: usize, closure: &[Vec<u64>]) -> usize {
    let mut matched_right_to_left = vec![None; num_elements];
    let mut matching_size = 0;

    for left in 0..num_elements {
        let mut visited_right = vec![false; num_elements];
        if can_match(
            left,
            num_elements,
            closure,
            &mut visited_right,
            &mut matched_right_to_left,
        ) {
            matching_size += 1;
        }
    }

    num_elements - matching_size
}

pub fn interval_summary_data_from_bitsets(
    num_elements: usize,
    closure: &[Vec<u64>],
) -> (
    usize,
    usize,
    usize,
    usize,
    usize,
    usize,
    f64,
    Vec<(usize, usize)>,
) {
    if num_elements == 0 {
        return (0, 0, 0, 0, 0, 0, 0.0, Vec::new());
    }

    let mut interval_sizes = Vec::new();

    for left in 0..num_elements {
        interval_sizes.push(1);

        for right in 0..num_elements {
            if !bit_is_set(&closure[left], right) {
                continue;
            }

            let size = (0..num_elements)
                .filter(|middle| {
                    (*middle == left || bit_is_set(&closure[left], *middle))
                        && (*middle == right || bit_is_set(&closure[*middle], right))
                })
                .count();
            interval_sizes.push(size);
        }
    }

    let num_intervals = interval_sizes.len();
    let num_trivial = interval_sizes.iter().filter(|size| **size == 1).count();
    let num_nontrivial = interval_sizes.iter().filter(|size| **size > 1).count();
    let num_cover = interval_sizes.iter().filter(|size| **size == 2).count();
    let min_size = *interval_sizes.iter().min().unwrap_or(&0);
    let max_size = *interval_sizes.iter().max().unwrap_or(&0);
    let mean_size = interval_sizes.iter().sum::<usize>() as f64 / num_intervals as f64;
    let histogram = histogram(&interval_sizes);

    (
        num_intervals,
        num_trivial,
        num_nontrivial,
        num_cover,
        min_size,
        max_size,
        mean_size,
        histogram,
    )
}

pub fn mobius_matrix_from_bitsets(num_elements: usize, closure: &[Vec<u64>]) -> Vec<Vec<i64>> {
    let mut matrix = vec![vec![0_i64; num_elements]; num_elements];

    for left in 0..num_elements {
        matrix[left][left] = 1;

        for right in (left + 1)..num_elements {
            if !bit_is_set(&closure[left], right) {
                continue;
            }

            let mut total = 0_i64;
            for middle in left..right {
                if (middle == left || bit_is_set(&closure[left], middle))
                    && bit_is_set(&closure[middle], right)
                {
                    total += matrix[left][middle];
                }
            }

            matrix[left][right] = -total;
        }
    }

    matrix
}

fn set_bit(bitset: &mut [u64], index: usize) {
    bitset[index / 64] |= 1_u64 << (index % 64);
}

fn bit_is_set(bitset: &[u64], index: usize) -> bool {
    (bitset[index / 64] & (1_u64 << (index % 64))) != 0
}

fn can_match(
    left: usize,
    num_elements: usize,
    closure: &[Vec<u64>],
    visited_right: &mut [bool],
    matched_right_to_left: &mut [Option<usize>],
) -> bool {
    for right in 0..num_elements {
        if !bit_is_set(&closure[left], right) || visited_right[right] {
            continue;
        }

        visited_right[right] = true;

        match matched_right_to_left[right] {
            None => {
                matched_right_to_left[right] = Some(left);
                return true;
            }
            Some(previous_left) => {
                if can_match(
                    previous_left,
                    num_elements,
                    closure,
                    visited_right,
                    matched_right_to_left,
                ) {
                    matched_right_to_left[right] = Some(left);
                    return true;
                }
            }
        }
    }

    false
}

fn histogram(values: &[usize]) -> Vec<(usize, usize)> {
    let mut histogram = Vec::new();

    for value in values {
        match histogram.binary_search_by_key(value, |(key, _)| *key) {
            Ok(index) => histogram[index].1 += 1,
            Err(index) => histogram.insert(index, (*value, 1)),
        }
    }

    histogram
}
