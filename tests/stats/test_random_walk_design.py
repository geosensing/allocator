"""The sampling property that makes a random walk usable as a survey design.

A walk down a street network is only a *sample* of that network if you know how
often it visits each part. The useful case is when it visits in proportion to
length, because then points spaced evenly along the walk are a uniform sample of
the road network and need no weights. That is the self-weighting property, and it
is what lets a walk-based survey be analysed without an inclusion-probability
correction.

It holds here, and provably. ``generate_walk`` picks uniformly among a node's
neighbours, which is a simple random walk, and for a simple random walk the
stationary distribution over nodes is ``pi(v) = deg(v) / 2|E|``. The rate of
traversing any particular directed edge ``(u, v)`` is then

    pi(u) * (1 / deg(u)) = deg(u)/(2|E|) * 1/deg(u) = 1/(2|E|)

which does not depend on ``u``, ``v``, or the edge's length. Every edge is
traversed equally often. Since walking an edge costs time proportional to its
length, the *distance* spent on an edge comes out proportional to its length --
self-weighting.

The property is worth pinning precisely because it is invisible in ordinary use
and easy to lose. Choosing the next edge with probability proportional to its
length is a natural-looking change -- it even sounds more "length aware" -- and it
destroys the property completely. ``test_a_length_proportional_walk_is_caught``
runs exactly that variant through the same gate and requires it to fail.

Two things about the design of these tests:

**Independent walks, not one long one.** A single walk is a Markov chain, so its
successive traversals are correlated and a binomial standard error computed from
the step count would understate the true variance. Each replicate here is a
separate walk, which makes the replicates genuinely independent and the Monte
Carlo standard error honest.

**The band is corrected for testing every edge at once.** Checking all ``|E|``
edges means running ``|E|`` gates simultaneously, so the per-test threshold comes
from the edge count rather than from a number chosen until the suite went quiet.
"""

import statistics
import unittest
from collections import Counter, defaultdict
from typing import Any

import networkx as nx
import numpy as np
from simcheck import MonteCarloResult, assert_unbiased, reps_for

from allocator.core.random_walk import _build_adjacency, generate_walk


def _irregular_graph(seed: int = 0) -> nx.Graph:
    """A graph built to make the property non-trivial.

    Degrees run from 1 to 4 and edge lengths from about 0.5 to 20, so
    "every edge equally often" and "every edge in proportion to length" are very
    different statements. On a regular graph with equal-length edges they would
    coincide and the test would prove nothing.

    The pendant nodes matter too: a degree-1 node forces the walk to reverse, and
    that dead-end edge correctly receives a double traversal.

    Args:
        seed: Seed for the edge lengths.

    Returns:
        nx.Graph: A connected graph with node ``x``/``y`` and edge ``length``.
    """
    rng = np.random.default_rng(seed)
    graph = nx.Graph()

    ring = 12
    for node in range(ring):
        graph.add_node(node, x=float(node), y=0.0)
    for node in range(ring):
        graph.add_edge(node, (node + 1) % ring, length=float(rng.uniform(0.5, 20.0)))

    for start, end in [(0, 5), (2, 8), (3, 9), (1, 7)]:
        graph.add_edge(start, end, length=float(rng.uniform(0.5, 20.0)))

    for index, pendant in enumerate([12, 13, 14]):
        graph.add_node(pendant, x=float(pendant), y=1.0)
        graph.add_edge(pendant, index * 3, length=float(rng.uniform(0.5, 20.0)))

    return graph


def _length_share(graph: nx.Graph) -> np.ndarray:
    """Fraction of the network's total length carried by each edge.

    Args:
        graph: The network.

    Returns:
        np.ndarray: Shares in ``graph.edges()`` order, summing to one.
    """
    lengths = nx.get_edge_attributes(graph, "length")
    total = sum(lengths.values())
    return np.array([lengths[edge] / total for edge in graph.edges()])


def _distance_share(graph: nx.Graph, traversals: list[tuple[Any, Any, float]]) -> np.ndarray:
    """Fraction of the distance walked that was spent on each edge.

    Args:
        graph: The network.
        traversals: ``(from_node, to_node, length)`` triples from a walk.

    Returns:
        np.ndarray: Shares in ``graph.edges()`` order, summing to one.
    """
    walked: defaultdict[tuple, float] = defaultdict(float)
    for start, end, length in traversals:
        walked[tuple(sorted((start, end)))] += length
    total = sum(walked.values())
    return np.array([walked[tuple(sorted(edge))] / total for edge in graph.edges()])


def _length_proportional_walk(
    graph: nx.Graph,
    adj: dict[Any, list[tuple[Any, float]]],
    start_node: Any,
    walk_length_m: float,
    rng: np.random.Generator,
) -> list[tuple[Any, Any, float]]:
    """A walk that picks the next edge in proportion to its length.

    Deliberately wrong, and wrong in a way that looks reasonable. It biases the
    walk towards long edges in *count* as well as in distance, so the two
    compound and long edges take far more than their share.

    Args:
        graph: The network. Unused beyond matching the real signature.
        adj: Adjacency mapping from ``_build_adjacency``.
        start_node: Where to start.
        walk_length_m: Target distance.
        rng: Source of randomness.

    Returns:
        list: ``(from_node, to_node, length)`` triples.
    """
    del graph
    current = start_node
    walked = 0.0
    traversals: list[tuple[Any, Any, float]] = []

    while walked < walk_length_m:
        neighbours = adj.get(current, [])
        if not neighbours:
            break
        lengths = np.array([length for _, length in neighbours])
        choice = rng.choice(len(neighbours), p=lengths / lengths.sum())
        next_node, edge_length = neighbours[choice]
        traversals.append((current, next_node, edge_length))
        walked += edge_length
        current = next_node

    return traversals


def _per_test_sigmas(n_tests: int, family_alpha: float = 0.01) -> float:
    """Sigmas per gate so that ``n_tests`` of them together fail this rarely.

    Args:
        n_tests: Number of simultaneous gates.
        family_alpha: Chance that a correct design trips any of them.

    Returns:
        float: Sigmas to allow per test.
    """
    return statistics.NormalDist().inv_cdf(1.0 - family_alpha / n_tests / 2.0)


class TestSelfWeighting(unittest.TestCase):
    """A simple random walk spends distance on each edge in proportion to length."""

    # Long enough that each edge is traversed many times per walk, so a single
    # replicate is an informative estimate rather than mostly noise.
    LAPS = 40

    def _shares_over_walks(self, walker, reps: int, seed: int = 1000) -> np.ndarray:
        """Per-edge distance shares from independent walks.

        Args:
            walker: Callable ``(graph, adj, start, target, rng)`` returning
                traversal triples.
            reps: Number of independent walks.
            seed: Base seed; walk ``r`` uses ``seed + r``.

        Returns:
            np.ndarray: Array of shape ``(reps, n_edges)``.
        """
        graph = _irregular_graph()
        adj = _build_adjacency(graph)
        target = sum(nx.get_edge_attributes(graph, "length").values()) * self.LAPS
        return np.array(
            [
                _distance_share(
                    graph,
                    walker(graph, adj, 0, target, np.random.default_rng(seed + rep)),
                )
                for rep in range(reps)
            ]
        )

    @staticmethod
    def _real_walk(graph, adj, start, target, rng) -> list[tuple[Any, Any, float]]:
        """Adapt ``generate_walk`` to the walker signature.

        Args:
            graph: The network.
            adj: Adjacency mapping.
            start: Starting node.
            target: Target distance.
            rng: Source of randomness.

        Returns:
            list: ``(from_node, to_node, length)`` triples.
        """
        return generate_walk(graph, adj, start, target, rng)["edges_traversed"]

    def test_distance_share_matches_length_share(self):
        """The self-weighting property itself, edge by edge.

        Edge by edge rather than pooled or correlated: a correlation across edges
        stays high while one edge is badly wrong, and two edges erring in opposite
        directions cancel in any aggregate.
        """
        graph = _irregular_graph()
        truth = _length_share(graph)
        reps = max(reps_for(), 40)
        shares = self._shares_over_walks(self._real_walk, reps)
        sigmas = _per_test_sigmas(len(truth))

        for index, edge in enumerate(graph.edges()):
            study = MonteCarloResult(
                estimates=shares[:, index],
                standard_errors=np.full(reps, np.nan),
                covered=None,
                rejected=None,
                truth=float(truth[index]),
            )
            assert_unbiased(study, label=f"edge {edge}", sigmas=sigmas)

    def test_a_length_proportional_walk_is_caught(self):
        """The falsification partner. Without it the test above proves nothing.

        Choosing the next edge with probability proportional to its length is the
        obvious-looking alternative, and it breaks self-weighting badly: long
        edges are favoured in the *number* of traversals on top of costing more
        distance each. If this ever stops failing, the gate above has stopped
        measuring anything.
        """
        graph = _irregular_graph()
        truth = _length_share(graph)
        reps = max(reps_for(), 40)
        shares = self._shares_over_walks(_length_proportional_walk, reps)
        sigmas = _per_test_sigmas(len(truth))

        failures = 0
        for index, edge in enumerate(graph.edges()):
            study = MonteCarloResult(
                estimates=shares[:, index],
                standard_errors=np.full(reps, np.nan),
                covered=None,
                rejected=None,
                truth=float(truth[index]),
            )
            try:
                assert_unbiased(study, label=f"edge {edge}", sigmas=sigmas)
            except AssertionError:
                failures += 1

        self.assertGreater(
            failures,
            len(truth) // 2,
            "a length-proportional walk is not self-weighting and most edges "
            f"should have been caught; only {failures} of {len(truth)} were",
        )

    def test_every_edge_is_traversed_equally_often(self):
        """The mechanism underneath: traversal counts ignore length entirely.

        Distance share tracking length share is the consequence. The cause is that
        a simple random walk crosses each edge at rate ``1/(2|E|)`` per step in
        each direction, whatever its length or its endpoints' degrees. Checking it
        directly says *why* the design is self-weighting, so a future change that
        preserved the consequence by accident would still be visible here.
        """
        graph = _irregular_graph()
        adj = _build_adjacency(graph)
        target = sum(nx.get_edge_attributes(graph, "length").values()) * self.LAPS
        n_edges = graph.number_of_edges()
        reps = max(reps_for(), 40)

        fractions = []
        for rep in range(reps):
            traversals = generate_walk(graph, adj, 0, target, np.random.default_rng(7000 + rep))[
                "edges_traversed"
            ]
            counts: Counter = Counter()
            for start, end, _ in traversals:
                counts[tuple(sorted((start, end)))] += 1
            total = sum(counts.values())
            fractions.append([counts[tuple(sorted(edge))] / total for edge in graph.edges()])
        fractions = np.array(fractions)

        sigmas = _per_test_sigmas(n_edges)
        for index, edge in enumerate(graph.edges()):
            study = MonteCarloResult(
                estimates=fractions[:, index],
                standard_errors=np.full(reps, np.nan),
                covered=None,
                rejected=None,
                truth=1.0 / n_edges,
            )
            assert_unbiased(study, label=f"traversal rate of edge {edge}", sigmas=sigmas)


if __name__ == "__main__":
    unittest.main()
