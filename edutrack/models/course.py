"""Course domain model.

Represents an academic course offered in a semester.
"""

from typing import Dict, Any


class Course:
    """Class representing an academic course."""

    def __init__(
        self,
        code: str,
        title: str,
        credits: int,
        faculty_name: str = "TBA",
        slot: str = "N/A",
        max_capacity: int = 60,
    ):
        self.code = code.strip().upper()
        self.title = title.strip()
        self.credits = int(credits)
        self.faculty_name = faculty_name.strip()
        self.slot = slot.strip().upper()
        self.max_capacity = int(max_capacity)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize course to dictionary."""
        return {
            "code": self.code,
            "title": self.title,
            "credits": self.credits,
            "faculty_name": self.faculty_name,
            "slot": self.slot,
            "max_capacity": self.max_capacity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Course":
        """Reconstruct course instance from dictionary."""
        return cls(
            code=data["code"],
            title=data["title"],
            credits=data["credits"],
            faculty_name=data.get("faculty_name", "TBA"),
            slot=data.get("slot", "N/A"),
            max_capacity=data.get("max_capacity", 60),
        )

    def __repr__(self) -> str:
        return f"Course({self.code}, credits={self.credits})"

    def __str__(self) -> str:
        return f"[{self.code}] {self.title} ({self.credits} Credits, Slot: {self.slot}, Faculty: {self.faculty_name})"
