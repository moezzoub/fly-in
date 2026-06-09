import sys
from models.drone import Drone
from models.graph import Graph
from models.zone import Zone
from simulation.pathfinder import find_short_path
from visualizer import Visualizer


class Simulator:
    """ Run the drone movement simulation on a parsed graph """
    def __init__(self, graph: Graph):
        """ Initialize the simulator with a validated graph """
        if graph.start_zone is None or graph.end_zone is None:
            raise ValueError("Graph must have a start zone and an end zone")

        self.graph = graph
        self.start_zone = graph.start_zone
        self.end_zone = graph.end_zone
        self.paths = find_short_path(graph)
        if not self.paths:
            raise ValueError("No valid path found from start to end")

        self.drones = [Drone(drone_id=i + 1, start_zone=graph.start_zone)
                       for i in range(graph.nb_drones)]

        self.drone_paths: dict[int, int] = {
            drone.drone_id: (drone.drone_id - 1) % len(self.paths)
            for drone in self.drones
        }

        self.turn = 0
        self.visualizer = Visualizer(graph)
        self.visualizer.draw_graph(self.drones)

    def get_next_zone(self, drone: Drone, path_index: int) -> Zone | None:
        """ Return the next zone on the selected path for a drone """
        if drone.current_zone is None:
            return None

        path = self.paths[path_index]

        for i, zone in enumerate(path):
            if zone.name == drone.current_zone.name:
                if i + 1 < len(path):
                    return path[i + 1]
                return None

        return None

    def all_delivered(self) -> bool:
        """ Return True when every drone has reached the destination """
        return all(drone.delivered for drone in self.drones)

    def run(self) -> None:
        """Run simulation turns one by one until all drones are delivered."""
        while not self.all_delivered():
            try:
                self.turn += 1
                moves = self.simulate_turn()

                if moves:
                    print(" ".join(moves))

                self.visualizer.update_graph(self.drones, self.turn)

            except KeyboardInterrupt:
                self.visualizer.close()
                print("\nGood Bye")
                sys.exit(0)

        print(f"number of turns: {self.turn}")
        self.visualizer.finish()

    def simulate_turn(self) -> list[str]:
        """ Simulate one turn of drone movement """
        moves: list[str] = []
        moved_this_turn: set[int] = set()

        transit_drones = [drone for drone in self.drones if drone.in_transit]

        # 1. move drones that were already in transit
        for drone in transit_drones:
            drone.in_transition()
            moved_this_turn.add(drone.drone_id)

            if drone.current_zone is not None:
                if drone.current_zone != self.end_zone:
                    drone.current_zone.enter()
                moves.append(
                    f"D{drone.drone_id}-{drone.current_zone.name}")

            if drone.current_zone is not None and\
                    drone.current_zone.name == self.end_zone.name:
                drone.mark_delivered()

        # [id, (current_zone, next_zone)]
        can_move: dict[int, tuple[Zone | None, Zone | None]] = {}

        planned_leave: dict[str, int] = {}
        planned_enter: dict[str, int] = {}

        def add_leave(zone: Zone) -> None:
            """ we call this func when drone plan to leave his current zone """
            planned_leave[zone.name] = planned_leave.get(zone.name, 0) + 1

        def add_enter(zone: Zone) -> None:
            """ and we call this func when drone plan to enter the next zone"""
            planned_enter[zone.name] = planned_enter.get(zone.name, 0) + 1

        def future_free_slots(zone: Zone) -> int:
            """ we calculate how much zone can accept """
            return (
                zone.rest_accept_drones()
                + planned_leave.get(zone.name, 0)
                - planned_enter.get(zone.name, 0)
            )

        # 2. plan for drones that will move
        for drone in self.drones:
            if drone.drone_id in moved_this_turn:
                continue

            if not drone.is_available():
                continue

            current_zone = drone.current_zone
            if current_zone is None:
                continue

            if current_zone == self.end_zone:
                drone.mark_delivered()
                continue

            path_index = self.drone_paths[drone.drone_id]
            next_zone = self.get_next_zone(drone, path_index)

            if next_zone is None:
                continue

            connection = self.graph.get_connection_between(
                current_zone.name,
                next_zone.name
            )

            if not connection.can_be_used():
                continue

            if next_zone != self.end_zone:
                if future_free_slots(next_zone) <= 0:
                    continue

            can_move[drone.drone_id] = (current_zone, next_zone)

            if current_zone != self.start_zone:
                add_leave(current_zone)

            if next_zone != self.end_zone:
                add_enter(next_zone)

        # 3. now move available planed drones
        for drone in self.drones:
            if drone.drone_id in moved_this_turn:
                continue

            if drone.drone_id not in can_move:
                continue

            if not drone.is_available():
                continue

            if (drone.current_zone is not None and
                    drone.current_zone.name == self.end_zone.name):
                drone.mark_delivered()
                continue

            path_index = self.drone_paths[drone.drone_id]
            next_zone = self.get_next_zone(drone, path_index)

            if next_zone is None:
                continue

            if next_zone != self.end_zone \
               and not next_zone.can_accept_drone():
                continue

            current_zone = drone.current_zone
            if current_zone is None:
                continue

            connection = self.graph.get_connection_between(
                current_zone.name, next_zone.name)

            if not connection.can_be_used():
                continue

            connection.use()

            if next_zone.cost_to_enter() == 1:
                if current_zone != self.start_zone:
                    current_zone.leave()

                drone.start_move(next_zone, connection)

                if next_zone != self.end_zone:
                    next_zone.enter()
                moves.append(f"D{drone.drone_id}-{next_zone.name}")

                if next_zone == self.end_zone:
                    drone.mark_delivered()

            else:
                if current_zone != self.start_zone:
                    current_zone.leave()

                drone.start_move(next_zone, connection)

                moves.append(f"D{drone.drone_id}-{connection.name()}")

        for conn in self.graph.connections:
            conn.current_usage = sum(
                1 for d in self.drones
                if d.in_transit and d.connection is conn
            )

        return moves
