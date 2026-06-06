from enum import Enum
from typing import Optional


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """ Represent a location that drones can enter or pass through """
    def __init__(self, name: str,
                 x: int,
                 y: int,
                 zone_type: ZoneType = ZoneType.NORMAL,
                 color: Optional[str] = None,
                 max_drones: int = 1):
        """ Initialize a zone """

        if max_drones <= 0:
            raise ValueError("max_drones must be positive")

        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.current_drones = 0

    def rest_accept_drones(self) -> int:
        return self.max_drones - self.current_drones

    def can_accept_drone(self) -> bool:
        """ Return True if another drone can enter the zone """
        return self.current_drones < self.max_drones

    def enter(self) -> None:
        """ Register one drone as entering the zone """
        if not self.can_accept_drone():
            raise ValueError(f"Zone {self.name} is full")
        self.current_drones += 1

    def leave(self) -> None:
        """ Register one drone as leaving the zone if any drone is present """
        if self.current_drones > 0:
            self.current_drones -= 1

    def is_blocked(self) -> bool:
        """ Return True if this zone cannot be entered """
        return self.zone_type == ZoneType.BLOCKED

    def cost_to_enter(self) -> int:
        """ Return the movement cost required to enter the zone """
        if self.zone_type == ZoneType.PRIORITY:
            return 1
        elif self.zone_type == ZoneType.NORMAL:
            return 1
        elif self.zone_type == ZoneType.RESTRICTED:
            return 2
        elif self.zone_type == ZoneType.BLOCKED:
            raise ValueError(f"Cannot enter blocked zone: {self.name}")
