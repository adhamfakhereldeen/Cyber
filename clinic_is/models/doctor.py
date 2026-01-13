from __future__ import annotations

from typing import List

from .person import Person


class Doctor(Person):
    def __init__(
        self,
        id: str,
        name: str,
        phone: str,
        specialty: str,
        office_hours: str,
        schedule: List[str] = None,
    ) -> None:
        super().__init__(id, name, phone)
        self.specialty = specialty
        self.office_hours = office_hours
        self.schedule: List[str] = schedule or []

    def is_available(self, datetime_str: str) -> bool:
        return datetime_str not in self.schedule

    def add_appointment(self, datetime_str: str) -> None:
        if datetime_str not in self.schedule:
            self.schedule.append(datetime_str)
