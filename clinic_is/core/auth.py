from __future__ import annotations

from typing import Optional

from .logger import audit_log
from .store import ClinicStore


def login(store: ClinicStore, username: str, password: str) -> Optional["User"]:
    user = store.users_by_username.get(username)
    if user and user.verify_password(password):
        audit_log("login_success", username, "User logged in")
        return user
    audit_log("login_failure", username, "Invalid credentials")
    return None
