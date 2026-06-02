"""Turn-by-turn drone simulator."""

from __future__ import annotations

from collections import defaultdict

from graph import Graph
from models import Drone
from visualizer import Visualizer

__all__ = ["Simulator"]


class Simulator:
    """Move drones through paths while respecting basic capacity rules."""

    def __init__(
        self,
        graph: Graph,
        start: str,
        end: str,
        drone_paths: list[list[str]],
        visualizer: Visualizer,
        max_turns: int = 10000,
    ) -> None:
        """Initialize simulator state."""
        self.graph = graph
        self.start = start
        self.end = end
        self.visualizer = visualizer
        self.max_turns = max_turns
        drone_list = []
        for idx, path in enumerate(drone_paths):
            drone_list.append(Drone(drone_id=idx + 1, path=path))
        self.drones = drone_list

    def all_delivered(self) -> bool:
        """Return True when every drone reached the end."""
        return all(drone.delivered for drone in self.drones)

    def current_occupancy(self) -> dict[str, int]:
        """Count drones currently occupying each zone."""
        occupancy: dict[str, int] = defaultdict(int)
        for drone in self.drones:
            if drone.delivered or drone.in_flight_to is not None:
                continue
            occupancy[drone.current_zone()] += 1
        return occupancy

    def can_enter(self, zone_name: str, occupancy: dict[str, int]) -> bool:
        """Return True if a drone may enter zone_name now."""
        if zone_name == self.end:
            return True
        capacity = self.graph.zone_capacity(zone_name, self.start, self.end)
        return occupancy.get(zone_name, 0) < capacity

    def run(self) -> int:
        """Run the simulation and return the number of turns used."""
        turn = 0
        self.visualizer.print_map_summary(self.start, self.end)

        while not self.all_delivered():
            turn += 1
            if turn > self.max_turns:
                msg = "simulation stopped: max_turns reached, possible deadlock"
                raise RuntimeError(msg)

            movements: list[str] = []
            occupancy = self.current_occupancy()
            link_usage: dict[frozenset[str], int] = defaultdict(int)

            self._finish_restricted_movements(occupancy, movements)
            self._move_ready_drones(occupancy, link_usage, movements)

            self.visualizer.print_turn(turn, movements)

        return turn

    def _finish_restricted_movements(
        self, occupancy: dict[str, int], movements: list[str]
    ) -> None:
        """Advance drones that are travelling to restricted zones."""
        for drone in self.drones:
            if drone.delivered or drone.in_flight_to is None:
                continue

            drone.remaining_turns -= 1
            if drone.remaining_turns > 0:
                conn = f"{drone.in_flight_from}-{drone.in_flight_to}"
                movements.append(f"{drone.label()}-{conn}")
                continue

            destination = drone.in_flight_to
            drone.in_flight_from = None
            drone.in_flight_to = None
            drone.index += 1

            if destination == self.end:
                drone.delivered = True
            else:
                occupancy[destination] = occupancy.get(destination, 0) + 1
            movements.append(f"{drone.label()}-{destination}")

    def _move_ready_drones(
        self,
        occupancy: dict[str, int],
        link_usage: dict[frozenset[str], int],
        movements: list[str],
    ) -> None:
        """Try to move all non-flying drones once during this turn."""
        ready_drones = [
            drone
            for drone in self.drones
            if (not drone.delivered
                and drone.in_flight_to is None
                and drone.next_zone() is not None)
        ]
        ready_drones.sort(key=lambda drone: drone.index, reverse=True)

        for drone in ready_drones:
            current = drone.current_zone()
            destination = drone.next_zone()
            if destination is None:
                continue

            edge_key = frozenset({current, destination})
            edge = self.graph.edge_between(current, destination)
            if link_usage[edge_key] >= edge.max_capacity:
                continue

            if not self.can_enter(destination, occupancy):
                continue

            link_usage[edge_key] += 1
            if current != self.start:
                occupancy[current] = max(0, occupancy.get(current, 0) - 1)

            destination_zone = self.graph.zones[destination]
            if destination_zone.zone_type == "restricted":
                drone.in_flight_from = current
                drone.in_flight_to = destination
                drone.remaining_turns = 1
                movements.append(f"{drone.label()}-{current}-{destination}")
                continue

            drone.index += 1
            if destination == self.end:
                drone.delivered = True
            else:
                occupancy[destination] = occupancy.get(destination, 0) + 1
            movements.append(f"{drone.label()}-{destination}")
