import matplotlib.pyplot as plt
from matplotlib.colors import is_color_like
from matplotlib.text import Text

from models.graph import Graph
from models.drone import Drone


class Visualizer:
    """ Draw and update the graph while drones move through it """
    def __init__(self, graph: Graph):
        """ Initialize the matplotlib figure for a graph """
        self.graph = graph
        self.fig, self.ax = plt.subplots()
        self.drone_point: dict[int, Text] = {}

    def get_valid_color(self, color: str | None) -> str:
        """ Return a matplotlib-compatible color """
        if color is None:
            return "gray"
        if is_color_like(color):
            return color

        return "gray"

    def draw_graph(self, drones: list[Drone]) -> None:
        """ Draw the initial graph and drone positions """
        self.ax.clear()
        self.ax.axis("off")
        self.fig.set_size_inches(15, 10)
        for connection in self.graph.connections:
            x = [connection.zone1.x, connection.zone2.x]
            y = [connection.zone1.y, connection.zone2.y]
            self.ax.plot(x, y, color="black", linewidth=3)

        for zone in self.graph.zones.values():
            zone_color = self.get_valid_color(zone.color)
            self.ax.scatter(zone.x, zone.y, s=2000,
                            edgecolors="black", color=zone_color,
                            zorder=3, linewidth=2)

        for drone in drones:
            if drone.current_zone is None:
                continue

            point = self.ax.text(
                        drone.current_zone.x,
                        drone.current_zone.y,
                        f"D{drone.drone_id}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        color="white",
                        bbox=dict(
                            facecolor="black",
                            edgecolor="white",
                            boxstyle="circle,pad=0.6"
                        ),
                        zorder=5,
                    )

            self.drone_point[drone.drone_id] = point
        plt.ion()
        plt.show()

    def update_graph(self, drones: list[Drone], turn: int) -> None:
        """ Update drone markers for a simulation turn """

        self.ax.set_title(f"Fly-in Drone Simulation - Turn {turn}")
        for drone in drones:
            pos = self.get_drone_position(drone)

            if pos is None:
                continue

            x, y = pos

            point = self.drone_point[drone.drone_id]

            point.set_position((x, y))

        plt.pause(0.3)

    def get_drone_position(self, drone: Drone) -> tuple[float, float] | None:
        """ Return the current visual position of a drone """
        if drone.current_zone is not None:
            return float(drone.current_zone.x), float(drone.current_zone.y)

        if drone.in_transit and \
                drone.from_zone is not None and \
                drone.to_zone is not None:
            x = (drone.from_zone.x + drone.to_zone.x) / 2
            y = (drone.from_zone.y + drone.to_zone.y) / 2
            return x, y
        return None

    def finish(self) -> None:
        """ Keep the final graph window open after the simulation ends """
        plt.ioff()
        plt.show()

    def close(self) -> None:
        """ Close the matplotlib figure """
        plt.ioff()
        plt.close(self.fig)
