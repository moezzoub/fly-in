"""Data models used by the Fly-in simulation."""

from dataclasses import dataclass
from typing import Optional

VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


@dataclass(frozen=True)
class Zone:
    """A zone/node in the drone map.

    Attributes:
        name: Unique zone name.
        x: X coordinate.
        y: Y coordinate.
        zone_type: One of normal, blocked, restricted, priority.
        color: Optional color name for visual output.
        max_drones: Maximum drones allowed in this zone at one time.
    """

    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1

    def movement_cost(self) -> int:
        """Return how many turns it costs to enter this zone."""
        if self.zone_type == "restricted":
            return 2
        return 1

    def is_blocked(self) -> bool:
        """Return True when drones are not allowed to enter this zone."""
        return self.zone_type == "blocked"


@dataclass(frozen=True)
class Edge:
    """A bidirectional connection between two zones."""

    zone_a: str
    zone_b: str
    max_capacity: int = 1

    def name(self) -> str:
        """Return a stable printable connection name."""
        return f"{self.zone_a}-{self.zone_b}"

    def connects(self, first: str, second: str) -> bool:
        """Return True if this edge connects first and second."""
        return {self.zone_a, self.zone_b} == {first, second}


@dataclass
class Drone:
    """Runtime state of one drone during simulation."""

    drone_id: int
    path: list[str]
    index: int = 0
    in_flight_from: Optional[str] = None
    in_flight_to: Optional[str] = None
    remaining_turns: int = 0
    delivered: bool = False

    def label(self) -> str:
        """Return the output label of this drone, for example D1."""
        return f"D{self.drone_id}"

    def current_zone(self) -> str:
        """Return current zone name when the drone is not in flight."""
        return self.path[self.index]

    def next_zone(self) -> Optional[str]:
        """Return the next zone in the path, or None if already at the end."""
        if self.index + 1 >= len(self.path):
            return None
        return self.path[self.index + 1]
