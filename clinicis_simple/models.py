import json
from typing import Any, Dict, List


class SerializableMixin:
    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)


class AuditableMixin:
    def audit(self, msg: str) -> None:
        print(f"[AUDIT] {msg}")


class Person:
    def __init__(self, pid: str, name: str, phone: str) -> None:
        self.pid = pid
        self.name = name
        self.phone = phone

    def update_phone(self, new_phone: str) -> None:
        self.phone = new_phone

    def display(self) -> str:
        return f"{self.name} ({self.pid}) - {self.phone}"


class Patient(Person):
    def __init__(self, pid: str, name: str, phone: str) -> None:
        super().__init__(pid, name, phone)
        self.visits: List[str] = []

    def add_visit(self, note: str) -> None:
        self.visits.append(note)

    def get_history(self) -> List[str]:
        return list(self.visits)


class Doctor(Person):
    def __init__(self, pid: str, name: str, phone: str, specialty: str) -> None:
        super().__init__(pid, name, phone)
        self.specialty = specialty
        self.schedule: List[str] = []

    def is_available(self, datetime_str: str) -> bool:
        return datetime_str not in self.schedule

    def add_appointment(self, datetime_str: str) -> None:
        if datetime_str not in self.schedule:
            self.schedule.append(datetime_str)


class Appointment(SerializableMixin, AuditableMixin):
    def __init__(self, appt_id: str, patient_id: str, doctor_id: str, datetime_str: str) -> None:
        self.appt_id = appt_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.datetime_str = datetime_str
        self.status = "scheduled"
        self.summary = ""

    def reschedule(self, new_datetime: str) -> None:
        old = self.datetime_str
        self.datetime_str = new_datetime
        self.audit(f"Rescheduled {self.appt_id}: {old} -> {new_datetime}")

    def cancel(self) -> None:
        self.status = "cancelled"
        self.audit(f"Cancelled {self.appt_id}")

    def complete(self, summary: str) -> None:
        self.status = "completed"
        self.summary = summary
        self.audit(f"Completed {self.appt_id} with summary")
