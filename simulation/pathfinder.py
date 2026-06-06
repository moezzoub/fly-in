import heapq

from models.graph import Graph
from models.zone import Zone


def reconstruct_path(previous: dict[str, list[str]], start: Zone,
                     end: Zone, graph: Graph) -> list[list[Zone]]:
    """Rebuild all shortest paths from the previous map produced by Dijkstra"""

    paths: list[list[Zone]] = []
    num = 1
    while num > 0:
        path = [end]
        current_name = end.name

        while current_name != start.name:
            current_names = previous[current_name]
            if len(current_names) > 1:
                num += 1
                current_name = previous[current_name].pop()
            else:
                current_name = previous[current_name][0]
            path.append(graph.get_zone(current_name))
        num -= 1
        path.reverse()
        paths.append(path)
    return paths


def find_shortest_path(graph: Graph) -> list[list[Zone]]:
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
