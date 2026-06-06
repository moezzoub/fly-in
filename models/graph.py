from .zone import Zone
from .connection import Connection


class Graph:
    """ Represent the full map used by the drone simulation """
    def __init__(self, nb_drones: int):
        """ Initialize an empty graph """
        if nb_drones <= 0:
            raise ValueError("nb_drones must be positive", 1)

        self.nb_drones = nb_drones
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.neighbors: dict[str, list[Connection]] = {}
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        """ Add a zone to the graph """
        if zone.name in self.zones:
            raise ValueError(f"Zone with name {zone.name} already exists")
        self.zones[zone.name] = zone
        self.neighbors[zone.name] = []

    def get_zone(self, name: str) -> Zone:
        """ Return a zone by name """
        if name not in self.zones:
            raise ValueError(f"Zone with name {name} does not exist")
        return self.zones[name]

    def set_start_zone(self, zone: Zone) -> None:
        """ Set the graph start zone """
        if zone.name not in self.zones:
            raise ValueError(f"Zone with name {zone.name} does not exist")
        self.start_zone = zone

    def set_end_zone(self, zone: Zone) -> None:
        """ Set the graph end zone """
        if zone.name not in self.zones:
            raise ValueError(f"Zone with name {zone.name} does not exist")
        self.end_zone = zone

    def add_connection(self, connection: Connection) -> None:
        """ Add a connection to the graph and adjacency list """
        if connection.zone1.name not in self.zones:
            raise ValueError(
                f"Zone with name {connection.zone1.name} does not exist")

        if connection.zone2.name not in self.zones:
            raise ValueError(
                f"Zone with name {connection.zone2.name} does not exist")

        for exist_connection in self.connections:
            if exist_connection.connects(connection.zone1, connection.zone2):
                raise ValueError(
                    f"Connection between {connection.zone1.name} and "
                    f"{connection.zone2.name} already exists"
                )

        self.connections.append(connection)
        self.neighbors[connection.zone1.name].append(connection)
        self.neighbors[connection.zone2.name].append(connection)

    def has_connection(self, zone1_name: str, zone2_name: str) -> bool:
        """ Return True if two named zones are directly connected """
        for conn in self.connections:
            if conn.connects(self.zones[zone1_name], self.zones[zone2_name]):
                return True

        return False

    def get_neighbors(self, zone_name: str) -> list[Zone]:
        """ Return all zones directly connected to the given zone """
        if zone_name not in self.neighbors:
            raise ValueError(f"Unknown zone: {zone_name}")

        zone = self.get_zone(zone_name)
        lst = []

        for conn in self.neighbors[zone_name]:
            lst.append(conn.other_side(zone))

        return lst

    def get_connections_of(self, zone_name: str) -> list[Connection]:
        """ Return all connections attached to the named zone """
        if zone_name not in self.neighbors:
            raise ValueError(f"Unknown zone: {zone_name}")

        return self.neighbors[zone_name]

    def get_connection_between(self, zone1_name: str, zone2_name: str
                               ) -> Connection:
        """ Return the connection between two named zones """
        zone1 = self.get_zone(zone1_name)
        zone2 = self.get_zone(zone2_name)

        for conn in self.connections:
            if conn.connects(zone1, zone2):
                return conn

        raise ValueError(
            f"No connection between {zone1_name} and {zone2_name}")

    def validate_special_zones(self) -> None:
        """ Validate that the graph has both start and end zones """
        if self.start_zone is None:
            raise ValueError("Missing start zone")
        if self.end_zone is None:
            raise ValueError("Missing end zone")
