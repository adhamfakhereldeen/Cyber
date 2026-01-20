import ctypes
import tkinter as tk
from tkinter import messagebox, ttk

from models import Doctor, Patient
from clinic import Clinic


class ClinicGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ClinicIS")
        # Always start fresh: overwrite JSON files each run
        self.store = Clinic(fresh_start=True)
        self.store.load_from_files()
        self._ensure_seed()
        self._build_ui()
        self.refresh_list()

    def _build_ui(self) -> None:
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)

        # Search entry (Event: Enter key)
        ttk.Label(frm, text="Search Patient ID/Name:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(frm, width=20)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<Return>", self._on_search)
        ttk.Button(frm, text="Search", command=self._on_search).grid(row=0, column=2, padx=5, pady=5)

        # Search details panel
        ttk.Label(frm, text="Patient Details:").grid(row=1, column=0, sticky="w")
        self.search_details_text = tk.Text(frm, height=4, width=50)
        self.search_details_text.grid(row=2, column=0, columnspan=2, pady=5)
        self.search_details_text.configure(state="disabled")

        # Combobox doctor (input)
        ttk.Label(frm, text="Doctor:").grid(row=3, column=0, sticky="w")
        self.doctor_combo = ttk.Combobox(frm, values=self._doctor_values(), state="readonly", width=25)
        self.doctor_combo.grid(row=3, column=1, padx=5, pady=5)
        if self.doctor_combo["values"]:
            self.doctor_combo.current(0)

        # Combobox patient (input)
        ttk.Label(frm, text="Patient:").grid(row=4, column=0, sticky="w")
        self.patient_combo = ttk.Combobox(frm, values=self._patient_values(), state="readonly", width=25)
        self.patient_combo.grid(row=4, column=1, padx=5, pady=5)
        if self.patient_combo["values"]:
            self.patient_combo.current(0)

        # Datetime entry
        ttk.Label(frm, text="Date/Time:").grid(row=5, column=0, sticky="w")
        self.datetime_entry = ttk.Entry(frm, width=20)
        self.datetime_entry.grid(row=5, column=1, padx=5, pady=5)
        ttk.Label(frm, text="Format: dd-mm-yyyy/hh:mm", foreground="gray").grid(
            row=6, column=0, columnspan=2, sticky="w"
        )

        # Button schedule (Event: click)
        self.schedule_btn = ttk.Button(frm, text="קבע תור", command=self._on_schedule)
        self.schedule_btn.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)

        # Listbox appointments (Event: select)
        ttk.Label(frm, text="Appointments:").grid(row=8, column=0, sticky="w")
        self.listbox = tk.Listbox(frm, height=6, width=50)
        self.listbox.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=5)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # Details panel (no popups)
        ttk.Label(frm, text="Appointment Details:").grid(row=10, column=0, sticky="w")
        self.details_text = tk.Text(frm, height=4, width=50)
        self.details_text.grid(row=11, column=0, columnspan=2, pady=5)
        self.details_text.configure(state="disabled")

        # Text summary input
        ttk.Label(frm, text="Visit Summary:").grid(row=12, column=0, sticky="w")
        self.summary_text = tk.Text(frm, height=4, width=50)
        self.summary_text.grid(row=13, column=0, columnspan=2, pady=5)

        # Action buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=14, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(btn_frame, text="Complete", command=self._on_complete).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self._on_delete).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Reschedule", command=self._on_reschedule).grid(row=0, column=3, padx=2)

        # Status label (replaces popups)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frm, textvariable=self.status_var, foreground="gray").grid(
            row=15, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(9, weight=1)

    def _doctor_values(self):
        return [f"{d.pid} - {d.name}" for d in self.store.doctors.values()]

    def _patient_values(self):
        return [f"{p.pid} - {p.name}" for p in self.store.patients.values()]

    def _set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    def _show_error(self, title: str, msg: str) -> None:
        messagebox.showerror(title, msg)

    def _on_search(self, event=None):
        query = self.search_entry.get().strip()
        if not query:
            self._set_status("Enter a patient ID or name")
            return

        patient = self.store.patients.get(query)
        if not patient:
            q = query.casefold()
            patient = next((p for p in self.store.patients.values() if p.name.casefold() == q), None)

        if patient:
            appts = [a for a in self.store.appointments if a.patient_id == patient.pid]
            details = [
                f"Patient {patient.pid}",
                f"Name {patient.name}",
                f"Phone {patient.phone}",
                f"Visits {len(patient.visits)}",
                f"Appointments {len(appts)}",
            ]
            if appts:
                details.append("\nAppointments:")
                for a in appts:
                    details.append(f"- {a.appt_id} | {a.doctor_id} | {a.datetime_str} | {a.status}")

            self.search_details_text.configure(state="normal")
            self.search_details_text.delete("1.0", "end")
            self.search_details_text.insert("1.0", "\n".join(details))
            self.search_details_text.configure(state="disabled")

            self.listbox.selection_clear(0, "end")
            first_idx = None
            for idx, appt in enumerate(self.store.appointments):
                if appt.patient_id == patient.pid:
                    self.listbox.selection_set(idx)
                    if first_idx is None:
                        first_idx = idx
            if first_idx is not None:
                self.listbox.see(first_idx)

            self._set_status("Ready")
        else:
            self.search_details_text.configure(state="normal")
            self.search_details_text.delete("1.0", "end")
            self.search_details_text.configure(state="disabled")
            self._set_status(f"No patient with id or name {query}")
            self._show_error("Not found", f"No patient with id or name {query}.")

    def _on_schedule(self):
        patient_val = self.patient_combo.get()
        doctor_val = self.doctor_combo.get()
        dt = self.datetime_entry.get().strip()
        if not (patient_val and doctor_val and dt):
            self._set_status("Fill patient, doctor, and date/time")
            self._show_error("Missing data", "Please select patient, doctor, and date/time.")
            return
        pid = patient_val.split(" - ")[0]
        doctor_id = doctor_val.split(" - ")[0]
        appt_id = self._next_appt_id()
        appt = self.store.schedule_appointment(appt_id, pid, doctor_id, dt)
        if appt:
            self.store.save_to_files()
            self.refresh_list()
            self._set_status(f"Appointment {appt_id} created")
        else:
            self._set_status("Failed to schedule (conflict or invalid)")
            self._show_error("Schedule error", "Unable to schedule. Time conflict or invalid data.")

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
            self._show_error("Missing data", "Please enter a new date/time.")
            return

        idx = sel[0]
        appt = self.store.appointments[idx]
        if self.store.reschedule_appointment(appt.appt_id, new_dt):
            self.store.save_to_files()
            self.refresh_list()
            self._set_status("Appointment rescheduled")
        else:
            self._set_status("Failed to reschedule (conflict?)")
            self._show_error("Reschedule error", "Unable to reschedule. Time conflict or invalid data.")

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
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 2.25)
    except Exception:
        pass
    ClinicGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
