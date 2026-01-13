from core.auth import login
from core.store import ClinicStore
from models.appointment import Appointment
from models.doctor import Doctor
from models.patient import Patient
from models.user import Admin, User


def build_demo_store() -> ClinicStore:
    store = ClinicStore()
    # sample users
    admin = Admin.create("admin", "admin", "admin123")  # type: ignore[attr-defined]
    clerk = User.create("clerk", "clerk", "clerk123")
    store.add_user(admin)
    store.add_user(clerk)

    # doctors
    d1 = Doctor("d1", "Dr. Green", "555-0001", "Cardiology", "09:00-16:00")
    d2 = Doctor("d2", "Dr. Blue", "555-0002", "Dermatology", "10:00-18:00")
    store.add_doctor(d1)
    store.add_doctor(d2)

    # patients
    p1 = Patient("p1", "Alice Patient", "050-1111111")
    p2 = Patient("p2", "Bob Patient", "050-2222222", notes="Allergy note")
    store.add_patient(p1)
    store.add_patient(p2)

    # appointments
    a1 = store.schedule_appointment("a1", "p1", "d1", "2026-01-14 10:00", actor="admin")
    a2 = store.schedule_appointment("a2", "p2", "d1", "2026-01-14 11:00", actor="admin")
    a3 = store.schedule_appointment("a3", "p2", "d2", "2026-01-15 12:00", actor="admin")

    # logical methods demo
    if a1:
        a1.reschedule("2026-01-14 12:30", actor="admin")
    if a2:
        a2.cancel(actor="admin")
    if a3:
        a3.complete("Routine check completed", actor="admin")
    p1.add_visit("Follow-up needed")
    p2.add_visit("Skin treatment")
    print("Doctor availability d1 10:00:", d1.is_available("2026-01-14 10:00"))
    print("Doctor availability d1 13:00:", d1.is_available("2026-01-14 13:00"))
    print("Patient history p2:", p2.get_history())

    store.complete_appointment("a3", "Stored summary", actor="admin")
    store.cancel_appointment("a2", actor="admin")
    store.save_all()
    return store


def demo_login(store: ClinicStore) -> None:
    user = login(store, "admin", "admin123")
    print("Login as admin:", bool(user))
    if user:
        print("Admin can schedule?", user.can("schedule"))
        print("Admin can view?", user.can("view_records"))


if __name__ == "__main__":
    demo_store = build_demo_store()
    demo_login(demo_store)
    print("Appointments saved:", [a.appt_id for a in demo_store.appointments])
