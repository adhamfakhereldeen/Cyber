import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from models import Appointment, Doctor, Patient

logger = logging.getLogger(__name__)


class Clinic:
    def __init__(self, fresh_start: bool = False) -> None:
        self.patients: Dict[str, Patient] = {}
        self.doctors: Dict[str, Doctor] = {}
        self.appointments: List[Appointment] = []
        self.base = Path(__file__).parent

        if fresh_start:
            self.reset_files()

    def reset_files(self) -> None:
        """Overwrite the JSON files with empty lists (fresh start each run)."""
        data_dir = self.base / "data"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "patients.json").write_text("[]", encoding="utf-8")
        (data_dir / "doctors.json").write_text("[]", encoding="utf-8")
        (data_dir / "appointments.json").write_text("[]", encoding="utf-8")

        # also reset in-memory state
        self.patients = {}
        self.doctors = {}
        self.appointments = []

    def add_patient(self, patient: Patient) -> None:
        self.patients[patient.pid] = patient

    def add_doctor(self, doctor: Doctor) -> None:
        self.doctors[doctor.pid] = doctor

    def schedule_appointment(
        self, appt_id: str, patient_id: str, doctor_id: str, datetime_str: str
    ) -> Optional[Appointment]:
        patient = self.patients.get(patient_id)
        doctor = self.doctors.get(doctor_id)
        if not patient or not doctor:
            return None
        if any(a.patient_id == patient_id and a.datetime_str == datetime_str for a in self.appointments):
            return None
        if not doctor.is_available(datetime_str):
            return None
        appt = Appointment(appt_id, patient_id, doctor_id, datetime_str, patient_obj=patient, doctor_obj=doctor)
        self.appointments.append(appt)
        doctor.add_appointment(datetime_str)
        return appt

    def cancel_appointment(self, appt_id: str) -> bool:
        appt = self._find(appt_id)
        if not appt:
            return False
        # free doctor's slot (so it can be booked again)
        doc = self.doctors.get(appt.doctor_id)
        if doc and appt.datetime_str in doc.schedule:
            doc.schedule.remove(appt.datetime_str)
        appt.cancel()
        return True

    def reschedule_appointment(self, appt_id: str, new_datetime: str) -> bool:
        appt = self._find(appt_id)
        if not appt:
            return False

        doc = self.doctors.get(appt.doctor_id)
        if not doc:
            return False

        old_datetime = appt.datetime_str
        if new_datetime == old_datetime:
            return True

        if any(
            a.patient_id == appt.patient_id
            and a.datetime_str == new_datetime
            and a.appt_id != appt_id
            for a in self.appointments
        ):
            return False

        # If the new time is already booked (other than this same appointment), reject.
        if new_datetime in doc.schedule:
            return False

        # update doctor's schedule
        if old_datetime in doc.schedule:
            doc.schedule.remove(old_datetime)
        doc.add_appointment(new_datetime)

        # update appointment
        appt.reschedule(new_datetime)
        return True

    def complete_appointment(self, appt_id: str, summary: str) -> bool:
        appt = self._find(appt_id)
        if not appt:
            return False
        appt.complete(summary)
        patient = self.patients.get(appt.patient_id)
        if patient:
            patient.add_visit(summary)
        return True

    def delete_appointment(self, appt_id: str) -> bool:
        appt = self._find(appt_id)
        if not appt:
            return False
        # remove from doctor's schedule if present
        doc = self.doctors.get(appt.doctor_id)
        if doc and appt.datetime_str in doc.schedule:
            doc.schedule.remove(appt.datetime_str)
        self.appointments = [a for a in self.appointments if a.appt_id != appt_id]
        return True

    def _find(self, appt_id: str) -> Optional[Appointment]:
        return next((a for a in self.appointments if a.appt_id == appt_id), None)

    def save_to_files(self) -> None:
        data_dir = self.base / "data"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "patients.json").write_text(
            json.dumps([p.__dict__ for p in self.patients.values()], indent=2),
            encoding="utf-8",
        )
        (data_dir / "doctors.json").write_text(
            json.dumps([d.__dict__ for d in self.doctors.values()], indent=2),
            encoding="utf-8",
        )
        (data_dir / "appointments.json").write_text(
            json.dumps([a.to_dict() for a in self.appointments], indent=2),
            encoding="utf-8",
        )

    def load_from_files(self) -> None:
        data_dir = self.base / "data"
        data_dir.mkdir(exist_ok=True)
        try:
            patients_raw = json.loads((data_dir / "patients.json").read_text(encoding="utf-8"))
            self.patients = {p["pid"]: Patient(**p) for p in patients_raw}
        except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load patients.json: %s", exc)
            self.patients = {}
        try:
            doctors_raw = json.loads((data_dir / "doctors.json").read_text(encoding="utf-8"))
            self.doctors = {d["pid"]: Doctor(**d) for d in doctors_raw}
        except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load doctors.json: %s", exc)
            self.doctors = {}
        try:
            appts_raw = json.loads((data_dir / "appointments.json").read_text(encoding="utf-8"))
            self.appointments = [Appointment.from_dict(a) for a in appts_raw]
        except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load appointments.json: %s", exc)
            self.appointments = []
