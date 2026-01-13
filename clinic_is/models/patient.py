from __future__ import annotations

from typing import List, Optional

from .person import Person


class Patient(Person):
    def __init__(
        self,
        id: str,
        name: str,
        phone: str,
        visits: Optional[List[str]] = None,
        notes: str = "",
    ) -> None:
        super().__init__(id, name, phone)
        self.visits: List[str] = visits or []
        self.notes = notes

    def add_visit(self, note: str) -> None:
        self.visits.append(note)

    def get_history(self) -> List[str]:
        return list(self.visits)
