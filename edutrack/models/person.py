"""Person and Faculty domain models.

Demonstrates Object-Oriented Programming (OOP) concepts:
Inheritance, encapsulation, method overriding, and polymorphism.
"""

from typing import Dict, Any


class Person:
    """Base class representing a university individual."""

    def __init__(self, name: str, email: str, phone: str = ""):
        self._name = name.strip()
        self._email = email.strip()
        self._phone = phone.strip()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        if not val.strip():
            raise ValueError("Name cannot be empty.")
        self._name = val.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, val: str):
        self._email = val.strip()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, val: str):
        self._phone = val.strip()

    def get_role(self) -> str:
        """Polymorphic method to identify role."""
        return "Person"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Person instance to a dictionary."""
        return {
            "name": self._name,
            "email": self._email,
            "phone": self._phone,
            "role": self.get_role(),
        }

    def __str__(self) -> str:
        return f"{self.get_role()}: {self._name} ({self._email})"


class Faculty(Person):
    """Faculty class inheriting from Person."""

    def __init__(self, emp_id: str, name: str, email: str, department: str, phone: str = ""):
        super().__init__(name=name, email=email, phone=phone)
        self.emp_id = emp_id.strip().upper()
        self.department = department.strip()

    def get_role(self) -> str:
        """Override base role."""
        return "Faculty"

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "emp_id": self.emp_id,
            "department": self.department,
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Faculty":
        return cls(
            emp_id=data.get("emp_id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            department=data.get("department", ""),
            phone=data.get("phone", ""),
        )

    def __str__(self) -> str:
        return f"Faculty [{self.emp_id}] {self.name} - {self.department}"
