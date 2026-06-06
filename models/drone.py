from models.zone import Zone
from models.connection import Connection


class Drone:
    """ Represent a single drone moving through the graph.

        A drone can be located inside a zone,
        be in transit between two zones, or
        be marked as delivered after reaching the end zone.
    """
    def __init__(self, drone_id: int, start_zone: Zone):
        """ Initialize a drone at the start zone """
        self.drone_id = drone_id
        self.current_zone: Zone | None = start_zone
        self.delivered = False
        self.in_transit = False
        self.from_zone: Zone | None = None
        self.to_zone: Zone | None = None
        self.connection: Connection | None = None
        self.remaining_turns = 0

    def start_move(self, destination: Zone, connection: Connection) -> None:
        """ Start moving the drone toward a destination zone """
        cost = destination.cost_to_enter()

        if cost == 1:
            self.current_zone = destination
            return

        self.in_transit = True
        self.from_zone = self.current_zone
        self.to_zone = destination
        self.connection = connection
        self.remaining_turns = cost - 1
        self.current_zone = None

    def in_transition(self) -> None:
        """ Advance an in-transit drone by one turn """
        if not self.in_transit:
            raise ValueError(f"Drone {self.drone_id} is not in transition")

        self.remaining_turns -= 1

        if self.remaining_turns == 0:
            if self.to_zone is None:
                raise ValueError(
                    "Transition finished but destination zone is missing")

            self.current_zone = self.to_zone
            self.in_transit = False
            self.from_zone = None
            self.to_zone = None
            self.connection = None
            self.remaining_turns = 0

    def mark_delivered(self) -> None:
        """ Mark the drone as delivered after reaching the end zone """
        self.delivered = True

    def is_available(self) -> bool:
        """ Return True if the drone can move during the current turn """
        return not self.delivered and not self.in_transit
