"""Entry point for the Fly-in project."""

import argparse
import sys

from errors import FlyInError
from parser import parse_file
from pathfinder import assign_paths, find_candidate_paths
from simulator import Simulator
from visualizer import Visualizer


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description="Fly-in drone routing simulator")
    parser.add_argument("map_file", help="Path to a Fly-in map file")
    parser.add_argument("--verbose", action="store_true", help="Print map summary and turn numbers")
    parser.add_argument("--no-color", action="store_true", help="Disable colored terminal output")
    parser.add_argument("--paths", type=int, default=20, help="Maximum candidate paths to search")
    parser.add_argument(
        "--show-paths", action="store_true", help="Print candidate paths in verbose mode")
    return parser


def main() -> int:
    """Parse arguments, solve the map, and run the simulation."""
    args = build_arg_parser().parse_args()

    try:
        parsed = parse_file(args.map_file)
        visualizer = Visualizer(parsed.graph, use_color=not args.no_color, verbose=args.verbose)
        paths = find_candidate_paths(parsed.graph, parsed.start, parsed.end, limit=args.paths)
        if args.verbose and args.show_paths:
            for index, path in enumerate(paths, start=1):
                joined = " -> ".join(path.nodes)
                print(f"Path {index} cost={path.cost}: {joined}")
        drone_paths = assign_paths(parsed.nb_drones, paths, parsed.graph, parsed.start, parsed.end)
        simulator = Simulator(parsed.graph, parsed.start, parsed.end, drone_paths, visualizer)
        turns = simulator.run()
        if args.verbose:
            print(f"Total turns: {turns}")
        return 0
    except FlyInError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
