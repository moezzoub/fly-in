"""Custom exceptions for the Fly-in project."""


class FlyInError(Exception):
    """Base exception for Fly-in errors."""


class ParsingError(FlyInError):
    """Raised when the input map file has invalid syntax."""

    def __init__(self, line_number: int, message: str) -> None:
        """Create a parsing error with line information."""
        super().__init__(f"Line {line_number}: {message}")
        self.line_number = line_number
        self.message = message


class NoPathError(FlyInError):
    """Raised when no valid path exists from start to end."""