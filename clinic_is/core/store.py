from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from models.appointment import Appointment
from models.doctor import Doctor
from models.patient import Patient
from models.user import Admin, User, hash_password

from .logger import audit_log
from .persistence import BASE_DIR, read_json, write_json

DATA_DIR = BASE_DIR / "data"


class ClinicStore:
    def __init__(self) -> None:
        self.patients_by_id: Dict[str, Patient] = {}
        self.doctors_by_id: Dict[str, Doctor] = {}
        self.appointments: List[Appointment] = []
        self.users_by_username: Dict[str, User] = {}

    # ---- Lookup helpers ----
    def find_patient(self, patient_id: str) -> Optional[Patient]:
        return self.patients_by_id.get(patient_id)

    def find_doctor(self, doctor_id: str) -> Optional[Doctor]:
        return self.doctors_by_id.get(doctor_id)

    def find_appointment(self, appt_id: str) -> Optional[Appointment]:
        return next((a for a in self.appointments if a.appt_id == appt_id), None)

    # ---- Mutations ----
    def add_patient(self, patient: Patient, actor: str = "system") -> None:
        self.patients_by_id[patient.id] = patient
        audit_log("add_patient", actor, f"Added patient {patient.id}")

    def add_doctor(self, doctor: Doctor, actor: str = "system") -> None:
        self.doctors_by_id[doctor.id] = doctor
        audit_log("add_doctor", actor, f"Added doctor {doctor.id}")

    def add_user(self, user: User, actor: str = "system") -> None:
        self.users_by_username[user.username] = user
        audit_log("add_user", actor, f"Added user {user.username}")

    def reset_user_password(self, username: str, new_password: str, actor: str = "system") -> None:
        user = self.users_by_username.get(username)
        if not user:
            return
        user.salt = user.salt or ""
        user.password_hash = hash_password(new_password, user.salt)
        audit_log("reset_password", actor, f"Reset password for {username}")

    def schedule_appointment(
        self,
        appt_id: str,
        patient_id: str,
        doctor_id: str,
        datetime_str: str,
        actor: str = "system",
    ) -> Optional[Appointment]:
        patient = self.find_patient(patient_id)
        doctor = self.find_doctor(doctor_id)
        if not patient or not doctor:
            return None
        if not doctor.is_available(datetime_str):
            return None
        # prevent same doctor double-booking
        conflict = any(
            a.doctor_id == doctor_id and a.datetime_str == datetime_str and a.status == "scheduled"
            for a in self.appointments
        )
        if conflict:
            return None
        appt = Appointment(appt_id, patient_id, doctor_id, datetime_str, status="scheduled")
        self.appointments.append(appt)
        doctor.add_appointment(datetime_str)
        audit_log("schedule", actor, f"Scheduled appt {appt_id} for patient {patient_id} with doctor {doctor_id}")
        return appt

    def cancel_appointment(self, appt_id: str, actor: str = "system") -> bool:
        appt = self.find_appointment(appt_id)
        if not appt:
            return False
        appt.cancel(actor)
        audit_log("cancel", actor, f"Cancelled appt {appt_id}")
        return True

    def complete_appointment(self, appt_id: str, summary: str, actor: str = "system") -> bool:
        appt = self.find_appointment(appt_id)
        if not appt:
            return False
        appt.complete(summary, actor)
        # record visit in patient history
        patient = self.find_patient(appt.patient_id)
        if patient:
            patient.add_visit(summary)
        audit_log("complete", actor, f"Completed appt {appt_id}")
        return True

    # ---- Persistence ----
    def save_all(self) -> None:
        patients_data = [p.to_dict() for p in self.patients_by_id.values()]
        doctors_data = [d.to_dict() for d in self.doctors_by_id.values()]
        appts_data = [a.to_dict() for a in self.appointments]
        users_data = [u.to_dict() for u in self.users_by_username.values()]

        write_json(DATA_DIR / "patients.json", patients_data)
        write_json(DATA_DIR / "doctors.json", doctors_data)
        write_json(DATA_DIR / "appointments.json", appts_data)
        write_json(DATA_DIR / "users.json", users_data)

    def load_all(self) -> None:
        patients_raw = read_json(DATA_DIR / "patients.json")
        doctors_raw = read_json(DATA_DIR / "doctors.json")
        appts_raw = read_json(DATA_DIR / "appointments.json")
        users_raw = read_json(DATA_DIR / "users.json")

        self.patients_by_id = {p["id"]: Patient.from_dict(p) for p in patients_raw} if patients_raw else {}
        self.doctors_by_id = {d["id"]: Doctor.from_dict(d) for d in doctors_raw} if doctors_raw else {}
        self.appointments = [Appointment.from_dict(a) for a in appts_raw] if appts_raw else []
        self.users_by_username = {
            u["username"]: User.from_dict(u) for u in users_raw
        } if users_raw else {}

        if "admin" not in self.users_by_username:
            default = User.create("admin", "admin", "admin123")
            self.add_user(default)

