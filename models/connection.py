from models.zone import Zone


class Connection:
    """ link between two zones """
    def __init__(self, zone1: Zone, zone2: Zone, max_link_capacity: int = 1):
        """ Initialize a connection between two zones """
        if max_link_capacity <= 0:
            raise ValueError("max_link_capacity must be positive")

        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity
        self.current_usage = 0

    def connects(self, zone_a: Zone, zone_b: Zone) -> bool:
        """ useful in parsing when checking duplicates or if already exists """
        return (
            (self.zone1 == zone_a and self.zone2 == zone_b)
            or
            (self.zone1 == zone_b and self.zone2 == zone_a)
        )

    def contains(self, zone: Zone) -> bool:
        """check if zone included this connection"""
        return self.zone1 == zone or self.zone2 == zone

    def other_side(self, zone: Zone) -> Zone:
        """ to give me the other zone """
        if zone == self.zone1:
            return self.zone2
        elif zone == self.zone2:
            return self.zone1
        raise ValueError(f"Zone {zone.name} is not part of this connection")

    def can_be_used(self) -> bool:
        """ to check if we can use this connection """
        return self.current_usage < self.max_link_capacity

    def use(self) -> None:
        if not self.can_be_used():
            raise ValueError(
                f"connection {self.zone1.name}-{self.zone2.name} is full")
        self.current_usage += 1

    def reset_usage(self) -> None:
        """ at the end of each turn, usage should be cleared for next turn """
        self.current_usage = 0

    def name(self) -> str:
        """ Return the display name of the connection """
        return f"{self.zone1.name}-{self.zone2.name}"
