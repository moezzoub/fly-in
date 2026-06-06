"""Parser for the Fly-in map format."""

from __future__ import annotations

import re
from pathlib import Path

from models import Connection, Graph, VALID_ZONE_TYPES, Zone, ZoneType
from models.errors import ParsingError

ZONE_PREFIXES = {"start_hub", "end_hub", "hub"}
ZONE_METADATA_KEYS = {"zone", "color", "max_drones"}
EDGE_METADATA_KEYS = {"max_link_capacity"}


def strip_comment(line: str) -> str:
    """Remove comments and surrounding whitespace from one line."""
    return line.split("#", 1)[0].strip()


def validate_metadata_keys(
    metadata: dict[str, str],
    allowed_keys: set[str],
    line_number: int,
) -> None:
    """Raise a parser error when a metadata key is not allowed here."""
    for key in metadata:
        if key not in allowed_keys:
            raise ParsingError(line_number, f"unknown metadata key '{key}'")


def split_metadata(text: str, line_number: int) -> tuple[str, dict[str, str]]:
    """Split a line body into normal content and optional [metadata]."""
    if "[" not in text and "]" not in text:
        return text.strip(), {}

    match = re.fullmatch(r"(.*?)\s*\[(.*?)\]\s*", text)
    if match is None:
        raise ParsingError(line_number, "invalid metadata block")

    before = match.group(1).strip()
    metadata_text = match.group(2).strip()
    metadata: dict[str, str] = {}

    if not metadata_text:
        return before, metadata

    for item in metadata_text.split():
        if "=" not in item:
            raise ParsingError(line_number, f"invalid metadata item '{item}'")
        key, value = item.split("=", 1)
        if not key or not value:
            raise ParsingError(line_number, f"invalid metadata item '{item}'")
        if key in metadata:
            raise ParsingError(line_number, f"duplicate metadata key '{key}'")
        metadata[key] = value

    return before, metadata


def positive_int(value: str, line_number: int, field: str) -> int:
    """Parse a positive integer field."""
    try:
        number = int(value)
    except ValueError as exc:
        raise ParsingError(line_number, f"{field} must be an integer") from exc
    if number <= 0:
        raise ParsingError(line_number, f"{field} must be positive")
    return number


def validate_zone_name(name: str, line_number: int) -> None:
    """Validate the subject constraints for zone names."""
    if not name:
        raise ParsingError(line_number, "zone name cannot be empty")
    if "-" in name or any(char.isspace() for char in name):
        raise ParsingError(line_number, "zone names cannot contain dashes or spaces")


def parse_zone(prefix: str, body: str, line_number: int) -> Zone:
    """Parse start_hub, end_hub, or hub line body."""
    content, metadata = split_metadata(body, line_number)
    validate_metadata_keys(metadata, ZONE_METADATA_KEYS, line_number)
    parts = content.split()
    if len(parts) != 3:
        raise ParsingError(line_number, f"{prefix} must be: name x y [metadata]")

    name, x_text, y_text = parts
    validate_zone_name(name, line_number)

    try:
        x = int(x_text)
        y = int(y_text)
    except ValueError as exc:
        raise ParsingError(line_number, "zone coordinates must be integers") from exc

    zone_type = metadata.get("zone", "normal")
    if zone_type not in VALID_ZONE_TYPES:
        raise ParsingError(line_number, f"invalid zone type '{zone_type}'")

    zone_enum = ZoneType(zone_type)

    max_drones = positive_int(metadata.get("max_drones", "1"), line_number, "max_drones")
    color = metadata.get("color", "none")
    return Zone(name=name, x=x, y=y, zone_type=zone_enum, color=color, max_drones=max_drones)


def parse_connection(body: str, graph: Graph, line_number: int) -> None:
    """Parse and add a connection line."""
    content, metadata = split_metadata(body, line_number)
    validate_metadata_keys(metadata, EDGE_METADATA_KEYS, line_number)
    parts = content.split()
    if len(parts) != 1 or "-" not in parts[0]:
        raise ParsingError(line_number, "connection must be: zone1-zone2 [metadata]")

    zone_a, zone_b = parts[0].split("-", 1)
    validate_zone_name(zone_a, line_number)
    validate_zone_name(zone_b, line_number)

    capacity = positive_int(
        metadata.get("max_link_capacity", "1"),
        line_number,
        "max_link_capacity",
    )
    graph.add_connection(
        Connection(
            graph.get_zone(zone_a),
            graph.get_zone(zone_b),
            capacity,
        )
    )


def parse_file(path: str) -> Graph:
    """Parse a Fly-in map file and return a populated Graph object."""
    graph: Graph | None = None
    saw_connections = False

    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ParsingError(0, f"cannot read file: {exc}") from exc

    for line_number, raw_line in enumerate(lines, start=1):
        line = strip_comment(raw_line)
        if not line:
            continue

        if graph is None:
            if not line.startswith("nb_drones:"):
                raise ParsingError(line_number, "first line must be nb_drones: <positive_integer>")
            value = line.split(":", 1)[1].strip()
            nb_drones = positive_int(value, line_number, "nb_drones")
            graph = Graph(nb_drones)
            continue

        if ":" not in line:
            raise ParsingError(line_number, "missing ':' separator")

        prefix, body = line.split(":", 1)
        prefix = prefix.strip()
        body = body.strip()

        if prefix in ZONE_PREFIXES:
            if saw_connections:
                raise ParsingError(line_number, "zones must be declared before connections")
            zone = parse_zone(prefix, body, line_number)
            graph.add_zone(zone)
            if prefix == "start_hub":
                if graph.start_zone is not None:
                    raise ParsingError(line_number, "multiple start_hub lines")
                graph.set_start_zone(zone)
            elif prefix == "end_hub":
                if graph.end_zone is not None:
                    raise ParsingError(line_number, "multiple end_hub lines")
                graph.set_end_zone(zone)
        elif prefix == "connection":
            saw_connections = True
            parse_connection(body, graph, line_number)
        else:
            raise ParsingError(line_number, f"unknown prefix '{prefix}'")

    if graph is None:
        raise ParsingError(0, "missing nb_drones line")
    if graph.start_zone is None:
        raise ParsingError(0, "missing start_hub")
    if graph.end_zone is None:
        raise ParsingError(0, "missing end_hub")
    if graph.start_zone.is_blocked():
        raise ParsingError(0, "start_hub cannot be blocked")
    if graph.end_zone.is_blocked():
        raise ParsingError(0, "end_hub cannot be blocked")

    return graph
