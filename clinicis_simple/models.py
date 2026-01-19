import json
from typing import Any, Dict, List, Optional


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

    def get_contact(self) -> str:
        return f"Name: {self.name}, Phone: {self.phone}"


class Patient(Person):
    def __init__(self, pid: str, name: str, phone: str, visits: Optional[List[str]] = None) -> None:
        super().__init__(pid, name, phone)
        self.visits: List[str] = list(visits or [])

    def add_visit(self, note: str) -> None:
        self.visits.append(note)

    def get_history(self) -> List[str]:
        return list(self.visits)


class Doctor(Person):
    def __init__(
        self,
        pid: str,
        name: str,
        phone: str,
        specialty: str,
        schedule: Optional[List[str]] = None,
    ) -> None:
        super().__init__(pid, name, phone)
        self.specialty = specialty
        self.schedule: List[str] = list(schedule or [])

    def is_available(self, datetime_str: str) -> bool:
        return datetime_str not in self.schedule

    def add_appointment(self, datetime_str: str) -> None:
        if datetime_str not in self.schedule:
            self.schedule.append(datetime_str)


class Appointment(SerializableMixin, AuditableMixin):
    def __init__(
        self,
        appt_id: str,
        patient_id: str,
        doctor_id: str,
        datetime_str: str,
        status: str = "scheduled",
        summary: str = "",
        patient_obj=None,
        doctor_obj=None,
    ) -> None:
        self.appt_id = appt_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.datetime_str = datetime_str
        self.status = status
        self.summary = summary
        self.patient_obj = patient_obj
        self.doctor_obj = doctor_obj

    def to_dict(self) -> Dict[str, Any]:
        return {
            "appt_id": self.appt_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "datetime_str": self.datetime_str,
            "status": self.status,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Appointment":
        return cls(
            data.get("appt_id", ""),
            data.get("patient_id", ""),
            data.get("doctor_id", ""),
            data.get("datetime_str", ""),
            data.get("status", "scheduled"),
            data.get("summary", ""),
            patient_obj=None,
            doctor_obj=None,
        )

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
