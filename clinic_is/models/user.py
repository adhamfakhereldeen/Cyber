from __future__ import annotations

import hashlib
import os
from typing import Dict, List

from .security_mixins import SerializableMixin

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": [
        "add_patient",
        "add_doctor",
        "schedule",
        "cancel",
        "complete",
        "view_records",
        "add_user",
        "reset_password",
    ],
    "doctor": ["schedule", "cancel", "complete", "view_records"],
    "clerk": ["add_patient", "add_doctor", "schedule", "cancel", "view_records"],
}


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


class User(SerializableMixin):
    def __init__(self, username: str, role: str, password_hash: str, salt: str) -> None:
        self.username = username
        self.role = role
        self.password_hash = password_hash
        self.salt = salt

    @staticmethod
    def create(username: str, role: str, password: str) -> "User":
        salt = os.urandom(8).hex()
        return User(username, role, hash_password(password, salt), salt)

    def verify_password(self, password: str) -> bool:
        return self.password_hash == hash_password(password, self.salt)

    def can(self, action: str) -> bool:
        return action in ROLE_PERMISSIONS.get(self.role, [])


class Admin(User):
    @staticmethod
    def create(username: str, role: str, password: str) -> "Admin":
        salt = os.urandom(8).hex()
        return Admin(username, role, hash_password(password, salt), salt)

    def add_user(self, store: "ClinicStore", user: User) -> None:  # type: ignore[name-defined]
        store.add_user(user, actor=self.username)

    def reset_password(self, store: "ClinicStore", username: str, new_password: str) -> None:  # type: ignore[name-defined]
        store.reset_user_password(username, new_password, actor=self.username)
