from __future__ import annotations

from typing import Any

from .security_mixins import SerializableMixin


class Person(SerializableMixin):
    def __init__(self, id: str, name: str, phone: str) -> None:
        self.id = id
        self.name = name
        self.phone = phone

    def update_phone(self, new_phone: str) -> None:
        self.phone = new_phone

    def display(self) -> str:
        return f"{self.name} ({self.id}) - {self.phone}"

    def __repr__(self) -> str:  # helpful for debugging/demo
        return f"Person(id={self.id}, name={self.name}, phone={self.phone})"
