import tkinter as tk
from tkinter import messagebox, ttk

from models import Doctor, Patient
from store import Store


class SimpleGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ClinicIS Simple")
        # Always start fresh: overwrite JSON files each run
        self.store = Store(fresh_start=True)
        self.store.load_from_files()
        self._ensure_seed()
        self._build_ui()
        self.refresh_list()

    def _build_ui(self) -> None:
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)

        # Search entry (Event: Enter key)
        ttk.Label(frm, text="Search Patient ID:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(frm, width=20)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<Return>", self._on_search)

        # Combobox doctor (input)
        ttk.Label(frm, text="Doctor:").grid(row=1, column=0, sticky="w")
        self.doctor_combo = ttk.Combobox(frm, values=self._doctor_values(), state="readonly", width=25)
        self.doctor_combo.grid(row=1, column=1, padx=5, pady=5)
        if self.doctor_combo["values"]:
            self.doctor_combo.current(0)

        # Patient ID entry
        ttk.Label(frm, text="Patient ID:").grid(row=2, column=0, sticky="w")
        self.patient_entry = ttk.Entry(frm, width=20)
        self.patient_entry.grid(row=2, column=1, padx=5, pady=5)

        # Datetime entry
        ttk.Label(frm, text="Date/Time:").grid(row=3, column=0, sticky="w")
        self.datetime_entry = ttk.Entry(frm, width=20)
        self.datetime_entry.grid(row=3, column=1, padx=5, pady=5)

        # Button schedule (Event: click)
        self.schedule_btn = ttk.Button(frm, text="קבע תור", command=self._on_schedule)
        self.schedule_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # Listbox appointments (Event: select)
        ttk.Label(frm, text="Appointments:").grid(row=5, column=0, sticky="w")
        self.listbox = tk.Listbox(frm, height=6, width=50)
        self.listbox.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # Details panel (no popups)
        ttk.Label(frm, text="Appointment Details:").grid(row=7, column=0, sticky="w")
        self.details_text = tk.Text(frm, height=4, width=50)
        self.details_text.grid(row=8, column=0, columnspan=2, pady=5)
        self.details_text.configure(state="disabled")

        # Text summary input
        ttk.Label(frm, text="Visit Summary:").grid(row=9, column=0, sticky="w")
        self.summary_text = tk.Text(frm, height=4, width=50)
        self.summary_text.grid(row=10, column=0, columnspan=2, pady=5)

        # Action buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(btn_frame, text="Complete", command=self._on_complete).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self._on_delete).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Reschedule", command=self._on_reschedule).grid(row=0, column=3, padx=2)

        # Status label (replaces popups)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frm, textvariable=self.status_var, foreground="gray").grid(
            row=12, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

    def _doctor_values(self):
        return [f"{d.pid} - {d.name}" for d in self.store.doctors.values()]

    def _set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    def _on_search(self, event=None):
        pid = self.search_entry.get().strip()
        patient = self.store.patients.get(pid)
        if patient:
            msg = f"Found patient {pid}: {patient.name} (Visits: {len(patient.visits)})"
            self._set_status(msg)
        else:
            self._set_status(f"No patient with id {pid}")

    def _on_schedule(self):
        pid = self.patient_entry.get().strip()
        doctor_val = self.doctor_combo.get()
        dt = self.datetime_entry.get().strip()
        if not (pid and doctor_val and dt):
            self._set_status("Fill patient, doctor, and date/time")
            return
        if pid not in self.store.patients:
            self.store.add_patient(Patient(pid, f"Patient {pid}", "000"))
        doctor_id = doctor_val.split(" - ")[0]
        appt_id = self._next_appt_id()
        appt = self.store.schedule_appointment(appt_id, pid, doctor_id, dt)
        if appt:
            self.store.save_to_files()
            self.refresh_list()
            self._set_status(f"Appointment {appt_id} created")
        else:
            self._set_status("Failed to schedule (id? conflict?)")

    def _next_appt_id(self) -> str:
        max_num = 0
        for appt in self.store.appointments:
            appt_id = getattr(appt, "appt_id", "")
            if isinstance(appt_id, str) and appt_id.startswith("a") and appt_id[1:].isdigit():
                max_num = max(max_num, int(appt_id[1:]))
        return f"a{max_num + 1}"

    def _on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        appt = self.store.appointments[idx]
        details = (
            f"Appt {appt.appt_id}\n"
            f"Patient {appt.patient_id}\n"
            f"Doctor {appt.doctor_id}\n"
            f"Time {appt.datetime_str}\n"
            f"Status {appt.status}"
        )
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", details)
        self.details_text.configure(state="disabled")
        # keep summary box for user input only
        self.summary_text.delete("1.0", "end")

    def _on_complete(self):
        sel = self.listbox.curselection()
        if not sel:
            self._set_status("Choose an appointment first")
            return
        idx = sel[0]
        appt = self.store.appointments[idx]
        summary = self.summary_text.get("1.0", "end").strip()
        if not summary:
            self._set_status("Add a summary first")
            return
        if self.store.complete_appointment(appt.appt_id, summary):
            self.store.save_to_files()
            self.refresh_list()
            self._set_status("Appointment completed")

    def _on_cancel(self):
        sel = self.listbox.curselection()
        if not sel:
            self._set_status("Choose an appointment first")
            return
        idx = sel[0]
        appt = self.store.appointments[idx]
        if self.store.cancel_appointment(appt.appt_id):
            self.store.save_to_files()
            self.refresh_list()
            self._set_status("Appointment cancelled")

    def _on_delete(self):
        sel = self.listbox.curselection()
        if not sel:
            self._set_status("Choose an appointment first")
            return
        idx = sel[0]
        appt = self.store.appointments[idx]
        if self.store.delete_appointment(appt.appt_id):
            self.store.save_to_files()
            self.refresh_list()
            self._set_status("Appointment removed")

    def _on_reschedule(self):
        sel = self.listbox.curselection()
        if not sel:
            self._set_status("Choose an appointment first")
            return

        new_dt = self.datetime_entry.get().strip()
        if not new_dt:
            self._set_status("Enter a new Date/Time first")
            return

        idx = sel[0]
        appt = self.store.appointments[idx]
        if self.store.reschedule_appointment(appt.appt_id, new_dt):
            self.store.save_to_files()
            self.refresh_list()
            self._set_status("Appointment rescheduled")
        else:
            self._set_status("Failed to reschedule (conflict?)")

    def refresh_list(self):
        self.listbox.delete(0, "end")
        for appt in self.store.appointments:
            self.listbox.insert("end", f"{appt.appt_id} | {appt.patient_id} | {appt.doctor_id} | {appt.datetime_str} | {appt.status}")

    def _ensure_seed(self):
        changed = False
        if not self.store.doctors:
            self.store.add_doctor(Doctor("d1", "Dr. Green", "555-0001", "GP"))
            self.store.add_doctor(Doctor("d2", "Dr. Blue", "555-0002", "Derm"))
            changed = True
        if not self.store.patients:
            self.store.add_patient(Patient("p1", "Alice", "111"))
            self.store.add_patient(Patient("p2", "Bob", "222"))
            changed = True

        if changed:
            self.store.save_to_files()


def run_gui():
    root = tk.Tk()
    SimpleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
