"""Stable failures for repository execution lifecycle control."""


class TaskControlError(ValueError):
    """A deterministic lifecycle-control failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        return f"{self.code}: {super().__str__()}"
