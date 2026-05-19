"""Graph representation for Fly-in maps.

The project forbids graph helper libraries, so this file implements a small
adjacency-list graph manually.
"""

from models import Edge, Zone
from errors import ParsingError


class Graph:
    """Store zones and bidirectional connections."""

    def __init__(self) -> None:
        """Create an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.edges: dict[frozenset[str], Edge] = {}
        self.adjacency: dict[str, list[str]] = {}

    def add_zone(self, zone: Zone, line_number: int) -> None:
        """Add a zone to the graph.

        Args:
            zone: Zone object to add.
            line_number: Map file line number, used for error messages.
        """
        if zone.name in self.zones:
            raise ParsingError(line_number, f"duplicate zone '{zone.name}'")
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_edge(self, zone_a: str, zone_b: str, capacity: int, line_number: int) -> None:
        """Add a bidirectional edge between two existing zones."""
        if zone_a not in self.zones:
            raise ParsingError(line_number, f"unknown zone '{zone_a}'")
        if zone_b not in self.zones:
            raise ParsingError(line_number, f"unknown zone '{zone_b}'")
        if zone_a == zone_b:
            raise ParsingError(line_number, "connection cannot link a zone to itself")

        key = frozenset({zone_a, zone_b})
        if key in self.edges:
            raise ParsingError(line_number, f"duplicate connection '{zone_a}-{zone_b}'")

        self.edges[key] = Edge(zone_a=zone_a, zone_b=zone_b, max_capacity=capacity)
        self.adjacency[zone_a].append(zone_b)
        self.adjacency[zone_b].append(zone_a)

    def neighbors(self, zone_name: str) -> list[str]:
        """Return neighbors of a zone."""
        return self.adjacency.get(zone_name, [])

    def edge_between(self, zone_a: str, zone_b: str) -> Edge:
        """Return the edge between two zones."""
        return self.edges[frozenset({zone_a, zone_b})]

    def zone_capacity(self, zone_name: str, start_name: str, end_name: str) -> int:
        """Return effective zone capacity.

        Start and end are special: they can hold many drones.
        """
        if zone_name in {start_name, end_name}:
            return 10**9
        return self.zones[zone_name].max_drones
