from __future__ import annotations

from typing import Optional

from .security_mixins import AuditableMixin, SerializableMixin


class Appointment(SerializableMixin, AuditableMixin):
    def __init__(
        self,
        appt_id: str,
        patient_id: str,
        doctor_id: str,
        datetime_str: str,
        status: str = "scheduled",
        summary: str = "",
    ) -> None:
        self.appt_id = appt_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.datetime_str = datetime_str
        self.status = status
        self.summary = summary

    def reschedule(self, new_datetime: str, actor: str = "system") -> None:
        old_time = self.datetime_str
        self.datetime_str = new_datetime
        self.audit("reschedule", f"{old_time} -> {new_datetime}", actor)

    def cancel(self, actor: str = "system") -> None:
        self.status = "cancelled"
        self.audit("cancel", f"Appointment {self.appt_id} cancelled", actor)

    def complete(self, summary: str, actor: str = "system") -> None:
        self.status = "completed"
        self.summary = summary
        self.audit("complete", f"Appointment {self.appt_id} completed", actor)
