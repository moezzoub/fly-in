"""Terminal visualizer for the Fly-in simulation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


ANSI_RESET = "\033[0m"

FOREGROUND_COLORS: dict[str, str] = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
    "grey": "\033[90m",
}


class Visualizer:
    """Display Fly-in simulation feedback in the terminal."""

    def __init__(self, graph: Any, use_color: bool = True, verbose: bool = False) -> None:
        """Initialize the visualizer.

        Args:
            graph: Graph object containing zones and connections.
            use_color: If False, ANSI colors are disabled.
            verbose: If True, detailed visual feedback is printed.
        """
        self.graph = graph
        self.use_color = use_color
        self.verbose = verbose

    def print_map_summary(self, start: str, end: str) -> None:
        """Print a short map summary before the simulation starts.

        Args:
            start: Name of the start zone.
            end: Name of the end zone.
        """
        if not self.verbose:
            return

        print()
        print("Map summary")
        print("=" * 50)
        print(f"Start: {self._format_zone_label(start)}")
        print(f"End: {self._format_zone_label(end)}")
        print(f"Zones: {len(self.graph.zones)}")
        print(f"Connections: {self._count_connections()}")
        print()

        print("Zones detail")
        print("-" * 50)

        for zone_name, zone in self.graph.zones.items():
            label = self._format_zone_label(zone_name)
            zone_type = self._get_zone_type_text(zone)
            color = self._get_zone_color_text(zone)
            max_drones = getattr(zone, "max_drones", 1)

            special = ""
            if getattr(zone, "is_start", False):
                special = " start"
            elif getattr(zone, "is_end", False):
                special = " end"

            print(
                f"  {label}"
                f" type={zone_type}"
                f" color={color}"
                f" max_drones={max_drones}"
                f"{special}"
            )

        print()

    def print_turn(
        self,
        turn_number: int,
        movements: Sequence[str],
        drone_positions: dict[int, str] | None = None,
    ) -> None:
        """Print one simulation turn.

        Args:
            turn_number: Current simulation turn number.
            movements: Official movements for this turn.
            drone_positions: Drone positions after this turn, if available.
        """
        official_line = " ".join(movements)

        if not self.verbose:
            if official_line:
                print(official_line)
            return

        print()
        print(f"Turn {turn_number}")
        print("=" * 50)

        if drone_positions is not None:
            self.print_map_state(drone_positions)

        if official_line:
            print()
            print(f"Moves: {official_line}")
            self.print_movement_explanation(movements)
        else:
            print()
            print("Moves: no movement")

    def print_map_state(self, drone_positions: dict[int, str]) -> None:
        """Print all zones and drones currently inside them.

        Args:
            drone_positions: Dictionary mapping drone id to current zone name.
        """
        zones_to_drones = self._group_drones_by_zone(drone_positions)

        print("Map state")
        print("-" * 50)

        for zone_name, zone in self.graph.zones.items():
            label = self._format_zone_label(zone_name)
            drones = zones_to_drones.get(zone_name, [])
            drones_text = self._format_drones(drones)
            zone_type = self._get_zone_type_text(zone)

            print(f"  {label} ({zone_type}): {drones_text}")

    def print_movement_explanation(self, movements: Sequence[str]) -> None:
        """Print readable movement explanations.

        Args:
            movements: Official movement strings.
        """
        if not self.verbose:
            return

        print("Movement detail")

        for movement in movements:
            if "-" not in movement:
                print(f"  {movement}")
                continue

            drone, destination = movement.split("-", 1)
            colored_destination = self._format_zone_label_if_exists(destination)
            print(f"  {drone} moved to {colored_destination}")

    def print_paths(self, paths: Sequence[Any]) -> None:
        """Print candidate paths.

        Args:
            paths: Candidate path objects. Each path should have nodes and cost.
        """
        if not self.verbose:
            return

        print()
        print("Candidate paths")
        print("=" * 50)

        for index, path in enumerate(paths, start=1):
            nodes = getattr(path, "nodes", [])
            cost = getattr(path, "cost", "?")
            joined = " -> ".join(str(node) for node in nodes)
            print(f"Path {index} cost={cost}: {joined}")

    def _group_drones_by_zone(self, drone_positions: dict[int, str]) -> dict[str, list[int]]:
        """Group drone ids by zone name.

        Args:
            drone_positions: Dictionary mapping drone id to zone name.

        Returns:
            Dictionary mapping zone name to sorted drone ids.
        """
        grouped: dict[str, list[int]] = {}

        for drone_id, zone_name in drone_positions.items():
            if zone_name not in grouped:
                grouped[zone_name] = []
            grouped[zone_name].append(drone_id)

        for drones in grouped.values():
            drones.sort()

        return grouped

    def _format_drones(self, drones: list[int]) -> str:
        """Format drones inside a zone.

        Args:
            drones: List of drone ids.

        Returns:
            Human-readable drone list.
        """
        if not drones:
            return "empty"

        return " ".join(f"D{drone_id}" for drone_id in drones)

    def _format_zone_label_if_exists(self, zone_name: str) -> str:
        """Format zone label only if the zone exists.

        Args:
            zone_name: Zone name or connection name.

        Returns:
            Colored label if zone exists, otherwise plain text.
        """
        if zone_name in self.graph.zones:
            return self._format_zone_label(zone_name)

        return zone_name

    def _format_zone_label(self, zone_name: str) -> str:
        """Format a zone label using zone metadata color.

        Args:
            zone_name: Name of the zone.

        Returns:
            Colored or plain zone label.
        """
        zone = self.graph.zones[zone_name]
        label = f"[{zone_name}]"

        if not self.use_color:
            return label

        color = getattr(zone, "color", None)
        if color is None:
            return label

        ansi_color = FOREGROUND_COLORS.get(str(color).lower())
        if ansi_color is None:
            return label

        return f"{ansi_color}{label}{ANSI_RESET}"

    def _get_zone_type_text(self, zone: Any) -> str:
        """Return zone type as text.

        Args:
            zone: Zone object.

        Returns:
            Zone type text.
        """
        zone_type = getattr(zone, "zone_type", "normal")

        if hasattr(zone_type, "value"):
            return str(zone_type.value)

        return str(zone_type)

    def _get_zone_color_text(self, zone: Any) -> str:
        """Return zone color as text.

        Args:
            zone: Zone object.

        Returns:
            Zone color or none.
        """
        color = getattr(zone, "color", None)

        if color is None:
            return "none"

        return str(color)

    def _count_connections(self) -> int:
        """Return number of connections in the graph.

        Returns:
            Number of graph connections.
        """
        connections = getattr(self.graph, "connections", None)

        if connections is None:
            return 0

        return len(connections)