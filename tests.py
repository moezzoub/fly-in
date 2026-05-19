"""Small self-tests for parser and simulator.

These tests are not required by the subject, but they help you verify changes
quickly before peer review.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from parser import parse_file
from pathfinder import assign_paths, find_candidate_paths
from simulator import Simulator
from visualizer import Visualizer


def solve(map_file: str) -> int:
    """Return number of turns for one map."""
    parsed = parse_file(map_file)
    paths = find_candidate_paths(parsed.graph, parsed.start, parsed.end)
    drone_paths = assign_paths(parsed.nb_drones, paths, parsed.graph, parsed.start, parsed.end)
    visualizer = Visualizer(parsed.graph, use_color=False, verbose=False)
    return Simulator(parsed.graph, parsed.start, parsed.end, drone_paths, visualizer).run()


def test_linear_map() -> None:
    """Check that the simplest provided map is solvable."""
    turns = solve("maps/easy/01_linear_path.txt")
    assert turns <= 6


def test_invalid_zone_type() -> None:
    """Check that the parser rejects unknown zone types."""
    content = """nb_drones: 1
start_hub: start 0 0
end_hub: goal 1 0
hub: bad 2 0 [zone=wrong]
connection: start-goal
"""
    with TemporaryDirectory() as folder:
        path = Path(folder) / "bad.txt"
        path.write_text(content, encoding="utf-8")
        try:
            parse_file(str(path))
        except Exception as exc:
            assert "invalid zone type" in str(exc)
        else:
            raise AssertionError("parser accepted an invalid zone type")


if __name__ == "__main__":
    test_linear_map()
    test_invalid_zone_type()
    print("tests passed")
