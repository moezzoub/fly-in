import sys
from parser import parse_file
from simulation.simulator import Simulator
import matplotlib.pyplot as plt


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        sys.exit(1)

    graph = parse_file(sys.argv[1])
    simulator = Simulator(graph)
    simulator.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close("all")
        print("\nGood Bye")
        sys.exit(0)
