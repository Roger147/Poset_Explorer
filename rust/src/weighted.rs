use std::collections::VecDeque;

const EPSILON: f64 = 1e-12;

#[derive(Debug, Eq, PartialEq)]
pub enum WeightedError {
    InvalidWeight,
}

#[derive(Clone)]
struct Edge {
    to: usize,
    reverse_index: usize,
    capacity: f64,
}

pub fn max_antichain_score_from_bitsets(
    num_elements: usize,
    closure: &[Vec<u64>],
    element_scores: &[f64],
) -> Result<f64, WeightedError> {
    if element_scores.iter().any(|score| !score.is_finite()) {
        return Err(WeightedError::InvalidWeight);
    }

    let positive_scores: Vec<f64> = element_scores.iter().map(|score| score.max(0.0)).collect();
    let total_score: f64 = positive_scores.iter().sum();

    if total_score <= EPSILON {
        return Ok(0.0);
    }

    let source = 2 * num_elements;
    let sink = source + 1;
    let mut graph = vec![Vec::new(); sink + 1];
    let infinite_capacity = total_score + 1.0;

    for element_index in 0..num_elements {
        let out_node = element_index;
        let in_node = num_elements + element_index;
        add_edge(&mut graph, source, out_node, positive_scores[element_index]);
        add_edge(&mut graph, in_node, sink, positive_scores[element_index]);

        for successor_index in 0..num_elements {
            if bit_is_set(&closure[element_index], successor_index) {
                add_edge(
                    &mut graph,
                    out_node,
                    num_elements + successor_index,
                    infinite_capacity,
                );
            }
        }
    }

    let minimum_vertex_cover_score = max_flow(&mut graph, source, sink);
    Ok((total_score - minimum_vertex_cover_score).max(0.0))
}

fn add_edge(graph: &mut [Vec<Edge>], from: usize, to: usize, capacity: f64) {
    let reverse_to = graph[to].len();
    let reverse_from = graph[from].len();

    graph[from].push(Edge {
        to,
        reverse_index: reverse_to,
        capacity,
    });
    graph[to].push(Edge {
        to: from,
        reverse_index: reverse_from,
        capacity: 0.0,
    });
}

fn max_flow(graph: &mut [Vec<Edge>], source: usize, sink: usize) -> f64 {
    let mut flow = 0.0;

    loop {
        let levels = levels(graph, source);
        if levels[sink] < 0 {
            return flow;
        }

        let mut next_edge_indices = vec![0; graph.len()];
        loop {
            let pushed = push_flow(
                source,
                sink,
                f64::INFINITY,
                &levels,
                &mut next_edge_indices,
                graph,
            );
            if pushed <= EPSILON {
                break;
            }

            flow += pushed;
        }
    }
}

fn levels(graph: &[Vec<Edge>], source: usize) -> Vec<i32> {
    let mut levels = vec![-1; graph.len()];
    let mut queue = VecDeque::new();
    levels[source] = 0;
    queue.push_back(source);

    while let Some(current) = queue.pop_front() {
        for edge in &graph[current] {
            if edge.capacity > EPSILON && levels[edge.to] < 0 {
                levels[edge.to] = levels[current] + 1;
                queue.push_back(edge.to);
            }
        }
    }

    levels
}

fn push_flow(
    current: usize,
    sink: usize,
    flow: f64,
    levels: &[i32],
    next_edge_indices: &mut [usize],
    graph: &mut [Vec<Edge>],
) -> f64 {
    if current == sink {
        return flow;
    }

    while next_edge_indices[current] < graph[current].len() {
        let edge_index = next_edge_indices[current];
        let edge = graph[current][edge_index].clone();

        if edge.capacity > EPSILON && levels[current] + 1 == levels[edge.to] {
            let pushed = push_flow(
                edge.to,
                sink,
                flow.min(edge.capacity),
                levels,
                next_edge_indices,
                graph,
            );

            if pushed > EPSILON {
                graph[current][edge_index].capacity -= pushed;
                graph[edge.to][edge.reverse_index].capacity += pushed;
                return pushed;
            }
        }

        next_edge_indices[current] += 1;
    }

    0.0
}

fn bit_is_set(bitset: &[u64], index: usize) -> bool {
    (bitset[index / 64] & (1_u64 << (index % 64))) != 0
}
