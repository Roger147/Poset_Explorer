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
        .map(|bitset| bitset.iter().map(|word| word.count_ones() as usize).sum::<usize>())
        .sum();
    let (ideal_sizes, filter_sizes) = principal_sizes_from_bitsets(num_elements, closure);

    (strict_comparability_count, ideal_sizes, filter_sizes)
}

pub fn interval_summary_data_from_bitsets(
    num_elements: usize,
    closure: &[Vec<u64>],
) -> (usize, usize, usize, usize, usize, usize, f64, Vec<(usize, usize)>) {
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

fn set_bit(bitset: &mut [u64], index: usize) {
    bitset[index / 64] |= 1_u64 << (index % 64);
}

fn bit_is_set(bitset: &[u64], index: usize) -> bool {
    (bitset[index / 64] & (1_u64 << (index % 64))) != 0
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
