"""Pathfinding algorithms for Fly-in."""

from __future__ import annotations

import heapq
from dataclasses import dataclass

from errors import NoPathError
from graph import Graph

INF = 10**18


@dataclass(frozen=True)
class PathInfo:
    """A candidate path with its weighted cost."""

    nodes: list[str]
    cost: int

    def bottleneck_score(self, graph: Graph, start: str, end: str) -> int:
        """Return a rough score for path congestion.

        Lower is better. Zones and links with capacity 1 are bottlenecks.
        """
        score = 0
        for node in self.nodes[1:-1]:
            score += max(0, 3 - graph.zone_capacity(node, start, end))
        for first, second in zip(self.nodes, self.nodes[1:]):
            score += max(0, 3 - graph.edge_between(first, second).max_capacity)
        return score


def path_cost(graph: Graph, nodes: list[str]) -> int:
    """Compute weighted path cost based on destination zones."""
    total = 0
    for zone_name in nodes[1:]:
        total += graph.zones[zone_name].movement_cost()
    return total


def dijkstra(
    graph: Graph,
    start: str,
    end: str,
    node_penalty: dict[str, int] | None = None,
    edge_penalty: dict[frozenset[str], int] | None = None,
) -> list[str]:
    """Find one lowest-cost path from start to end.

    Penalties are used to discover alternative paths after the first shortest path.
    """
    node_penalty = node_penalty or {}
    edge_penalty = edge_penalty or {}

    distances: dict[str, int] = {start: 0}
    parents: dict[str, str] = {}
    queue: list[tuple[int, str]] = [(0, start)]
    visited: set[str] = set()

    while queue:
        current_cost, current = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)

        if current == end:
            break

        neighbors = sorted(
            graph.neighbors(current),
            key=lambda name: (
                0 if graph.zones[name].zone_type == "priority" else 1,
                graph.zones[name].movement_cost(),
                name,
            ),
        )
        for neighbor in neighbors:
            zone = graph.zones[neighbor]
            if zone.is_blocked():
                continue

            edge_key = frozenset({current, neighbor})
            step_cost = zone.movement_cost()
            step_cost += node_penalty.get(neighbor, 0)
            step_cost += edge_penalty.get(edge_key, 0)

            new_cost = current_cost + step_cost
            if new_cost < distances.get(neighbor, INF):
                distances[neighbor] = new_cost
                parents[neighbor] = current
                heapq.heappush(queue, (new_cost, neighbor))

    if end not in distances:
        raise NoPathError(f"no path from '{start}' to '{end}'")

    path = [end]
    while path[-1] != start:
        path.append(parents[path[-1]])
    path.reverse()
    return path


def find_candidate_paths(graph: Graph, start: str, end: str, limit: int = 20) -> list[PathInfo]:
    """Find several useful paths from start to end.

    This is a practical beginner-friendly alternative to a full k-shortest-path
    implementation. After every path, used nodes and edges receive penalties,
    encouraging Dijkstra to search another corridor.
    """
    paths: list[PathInfo] = []
    seen: set[tuple[str, ...]] = set()
    node_penalty: dict[str, int] = {}
    edge_penalty: dict[frozenset[str], int] = {}

    for _ in range(max(1, limit * 2)):
        try:
            nodes = dijkstra(graph, start, end, node_penalty, edge_penalty)
        except NoPathError:
            break

        key = tuple(nodes)
        if key not in seen:
            seen.add(key)
            paths.append(PathInfo(nodes=nodes, cost=path_cost(graph, nodes)))
            if len(paths) >= limit:
                break

        for node in nodes[1:-1]:
            node_penalty[node] = node_penalty.get(node, 0)
            + graph.zone_capacity(node, start, end) + 1
        for first, second in zip(nodes, nodes[1:]):
            edge_key = frozenset({first, second})
            edge = graph.edge_between(first, second)
            edge_penalty[edge_key] = edge_penalty.get(edge_key, 0) + edge.max_capacity + 1

    if not paths:
        raise NoPathError(f"no path from '{start}' to '{end}'")

    paths.sort(key=lambda path:
               (path.cost, path.bottleneck_score(graph, start, end), len(path.nodes)))
    return paths


def assign_paths(
        nb_drones: int, paths: list[PathInfo], graph: Graph, start: str, end: str
) -> list[list[str]]:
    """Assign drones to paths using load-balancing with bottleneck awareness."""
    assigned_counts = [0 for _ in paths]
    result: list[list[str]] = []

    for _ in range(nb_drones):
        best_index = 0
        best_score = INF
        for index, path in enumerate(paths):
            bottleneck = max(1, path.bottleneck_score(graph, start, end))
            score = path.cost + (assigned_counts[index] * bottleneck)
            if score < best_score:
                best_score = score
                best_index = index
        assigned_counts[best_index] += 1
        result.append(paths[best_index].nodes)

    return result
