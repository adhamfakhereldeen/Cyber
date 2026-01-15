from models import Appointment, Doctor, Patient
from store import Store


def demo():
    # Always start fresh: overwrite JSON files each run
    store = Store(fresh_start=True)

    # create objects
    p1 = Patient("p1", "Alice", "111")
    p2 = Patient("p2", "Bob", "222")
    d1 = Doctor("d1", "Dr. Green", "333", "GP")
    d2 = Doctor("d2", "Dr. Blue", "444", "Derm")

    # add to store
    store.add_patient(p1)
    store.add_patient(p2)
    store.add_doctor(d1)
    store.add_doctor(d2)

    # schedule
    a1 = store.schedule_appointment("a1", "p1", "d1", "2026-01-15 10:00")
    a2 = store.schedule_appointment("a2", "p2", "d2", "2026-01-15 11:00")

    # logical methods
    if a1:
        store.reschedule_appointment("a1", "2026-01-15 12:00")
    if a2:
        store.cancel_appointment("a2")
    store.complete_appointment("a1", "Routine check complete")

    p1.add_visit("Follow-up in 3 months")
    print("History p1:", p1.get_history())
    print("Doctor d1 available 10:00?", d1.is_available("2026-01-15 10:00"))
    print("Doctor d1 available 12:00?", d1.is_available("2026-01-15 12:00"))

    store.save_to_files()
    print("Saved to JSON files.")

    # load back to prove it works
    store2 = Store()
    store2.load_from_files()
    print("Loaded appointments:", [a.appt_id for a in store2.appointments])
    print("First appt status:", store2.appointments[0].status if store2.appointments else "none")


if __name__ == "__main__":
    demo()
