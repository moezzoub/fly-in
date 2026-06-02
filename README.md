*This project has been created as part of the 42 curriculum by moeezoub.*

# Fly-in

## Description

Fly-in is a Python 3.10+ project that routes multiple drones from a start hub to an end hub through a graph of connected zones.

The program includes:

- a parser for the subject map format,
- an object-oriented graph representation,
- a pathfinding module based on Dijkstra,
- a turn-by-turn simulation engine,
- capacity handling for zones and connections,
- terminal output for drone movements.

## Instructions

Install tools:

```bash
make install
```

Run with one map:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

Verbose mode:

```bash
python3 main.py maps/easy/01_linear_path.txt --verbose
```

Lint and type-check:

```bash
make lint
```

## Algorithm Strategy

The graph is represented manually using an adjacency list. No graph library is used.

The pathfinder uses Dijkstra because movement has weights:

- normal zones cost 1 turn,
- priority zones cost 1 turn and are preferred when sorting neighbors,
- restricted zones cost 2 turns,
- blocked zones are ignored.

To create multiple paths, the program runs Dijkstra several times. After each found path, it adds penalties to the nodes and edges already used. This encourages the next search to discover a different path.

Drones are assigned to paths with a load-balancing heuristic:

```text
estimated_finish = path_cost + drones_already_assigned_to_path
```

Each new drone receives the path with the smallest estimated finish.

## Simulation Strategy

The simulation runs in discrete turns. In each turn:

1. drones already travelling to restricted zones advance,
2. ready drones are processed from the end of their path backwards,
3. each movement checks zone capacity and connection capacity,
4. movements are printed in the required `D<ID>-<zone>` format.

Processing drones closer to the end first allows this valid situation:

```text
D1 moves A -> B
D2 moves start -> A
```

This is valid because D1 leaves `A` during the same turn before D2 enters it.

## Visual Representation

The program supports optional colored terminal display based on the `color=` metadata of zones. Verbose mode prints turn numbers and a map summary.

## Resources

- Python documentation: dataclasses, argparse, pathlib, heapq
- PEP 257 for docstrings
- flake8 and mypy documentation
- Dijkstra shortest path algorithm references

## AI Usage

AI was used to help understand the subject, plan the architecture, and explain concepts. The code must still be reviewed, tested, and understood by the student before peer evaluation.


## Improvement Notes

This version includes stricter metadata validation, duplicate metadata detection,
bottleneck-aware path assignment, a `--show-paths` debugging option, and a small
`tests.py` script that can be launched with `make test`.

Useful commands:

```bash
python3 main.py maps/easy/01_linear_path.txt --verbose --show-paths
make test
make lint
```
