import heapq

from models.graph import Graph
from models.zone import Zone


def reconstruct_path(previous: dict[str, list[str]], start: Zone,
                     end: Zone, graph: Graph) -> list[list[Zone]]:
    """Rebuild all shortest paths from the previous map produced by Dijkstra.

    previous can contain many parents for the same zone when two routes have
    the same shortest cost. We explore every parent combination without
    changing previous.
    """

    if start.name == end.name:
        return [[start]]

    paths: list[list[Zone]] = []
    current_path: list[str] = [end.name]

    def backtrack(current_name: str) -> None:
        if current_name == start.name:
            zone_path = [
                graph.get_zone(name)
                for name in reversed(current_path)
            ]
            paths.append(zone_path)
            return

        for parent_name in previous.get(current_name, []):
            if parent_name in current_path:
                continue

            current_path.append(parent_name)
            backtrack(parent_name)
            current_path.pop()

    backtrack(end.name)
    return paths


def find_short_path(graph: Graph) -> list[list[Zone]]:
    """Find all lowest-cost valid paths from start to end."""

    if graph.start_zone is None or graph.end_zone is None:
        raise ValueError("Graph must have a start zone and an end zone")

    start = graph.start_zone
    end = graph.end_zone

    distances: dict[str, float] = {
        zone_name: float("inf") for zone_name in graph.zones
    }

    previous: dict[str, list[str]] = {}

    distances[start.name] = 0
    heap: list[tuple[float, str]] = [(0, start.name)]

    while heap:
        current_distance, current_name = heapq.heappop(heap)

        if current_distance > distances[current_name]:
            continue

        current_zone = graph.get_zone(current_name)

        for connection in graph.get_connections_of(current_name):
            neighbor = connection.other_side(current_zone)

            if neighbor.is_blocked():
                continue

            new_distance = current_distance + neighbor.cost_to_enter()

            if new_distance < distances[neighbor.name]:
                distances[neighbor.name] = new_distance
                previous[neighbor.name] = [current_name]
                heapq.heappush(heap, (new_distance, neighbor.name))

            elif new_distance == distances[neighbor.name]:
                if current_name not in previous[neighbor.name]:
                    previous[neighbor.name].append(current_name)

    if distances[end.name] == float("inf"):
        raise ValueError("No valid path from start to end")

    return reconstruct_path(previous, start, end, graph)
