import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from core.auth import login
from core.store import ClinicStore
from models.appointment import Appointment


class ClinicGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ClinicIS")
        self.store = ClinicStore()
        self.store.load_all()
        self.current_user = None

        self.login_frame: Optional[ttk.Frame] = None
        self.main_frame: Optional[ttk.Frame] = None

        self._build_login()

    # ---- UI Builders ----
    def _build_login(self) -> None:
        self.login_frame = ttk.Frame(self.root, padding=10)
        self.login_frame.pack(fill="both", expand=True)
        ttk.Label(self.login_frame, text="Username").grid(row=0, column=0, sticky="w")
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, pady=5)
        ttk.Label(self.login_frame, text="Password").grid(row=1, column=0, sticky="w")
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        login_btn = ttk.Button(self.login_frame, text="Login", command=self._handle_login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

    def _build_main(self) -> None:
        if self.login_frame:
            self.login_frame.destroy()
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Search row
        search_frame = ttk.LabelFrame(self.main_frame, text="Search Patient")
        search_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(search_frame, text="ID or Name:").grid(row=0, column=0)
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<Return>", lambda e: self.refresh_tree())

        # Appointment form
        form = ttk.LabelFrame(self.main_frame, text="Create / Update Appointment")
        form.grid(row=1, column=0, sticky="ew", pady=5)
        ttk.Label(form, text="Patient ID:").grid(row=0, column=0, sticky="w")
        self.patient_entry = ttk.Entry(form, width=20)
        self.patient_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form, text="Doctor:").grid(row=0, column=2, sticky="w")
        self.doctor_combo = ttk.Combobox(form, state="readonly", width=25)
        self.doctor_combo.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(form, text="Date/Time (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky="w")
        self.datetime_entry = ttk.Entry(form, width=25)
        self.datetime_entry.grid(row=1, column=1, padx=5, pady=2)

        self.schedule_btn = ttk.Button(form, text="Schedule", command=self._schedule_click)
        self.schedule_btn.grid(row=1, column=3, padx=5, pady=2, sticky="ew")

        # Appointments list
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=("appt_id", "patient", "doctor", "datetime", "status"),
            show="headings",
            height=8,
        )
        for col in ("appt_id", "patient", "doctor", "datetime", "status"):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=120)
        self.tree.grid(row=2, column=0, sticky="nsew", pady=5)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Summary area and actions
        summary_frame = ttk.LabelFrame(self.main_frame, text="Visit Summary")
        summary_frame.grid(row=3, column=0, sticky="ew")
        self.summary_text = tk.Text(summary_frame, height=4, width=60)
        self.summary_text.grid(row=0, column=0, columnspan=3, pady=5)

        self.cancel_btn = ttk.Button(summary_frame, text="Cancel Appointment", command=self._cancel_click)
        self.cancel_btn.grid(row=1, column=0, padx=5, pady=2)
        self.complete_btn = ttk.Button(summary_frame, text="Complete Appointment", command=self._complete_click)
        self.complete_btn.grid(row=1, column=1, padx=5, pady=2)

        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self._load_doctors()
        self.refresh_tree()

    # ---- Event Handlers ----
    def _handle_login(self) -> None:
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = login(self.store, username, password)
        if not user:
            messagebox.showerror("Login failed", "Invalid credentials")
            return
        self.current_user = user
        self._build_main()

    def _schedule_click(self) -> None:
        if not self._check_perm("schedule"):
            return
        patient_id = self.patient_entry.get().strip()
        doctor_val = self.doctor_combo.get()
        datetime_val = self.datetime_entry.get().strip()
        if not (patient_id and doctor_val and datetime_val):
            messagebox.showwarning("Missing data", "Please fill all fields.")
            return
        doctor_id = doctor_val.split(" - ")[0]
        appt_id = f"a{len(self.store.appointments)+1}"
        appt = self.store.schedule_appointment(
            appt_id, patient_id, doctor_id, datetime_val, actor=self.current_user.username  # type: ignore[union-attr]
        )
        if appt:
            messagebox.showinfo("Success", f"Appointment {appt_id} scheduled.")
            self.store.save_all()
            self.refresh_tree()
        else:
            messagebox.showerror("Error", "Could not schedule (check IDs or conflicts).")

    def _cancel_click(self) -> None:
        if not self._check_perm("cancel"):
            return
        appt = self._selected_appt()
        if not appt:
            messagebox.showwarning("Select", "Choose an appointment first.")
            return
        if self.store.cancel_appointment(appt.appt_id, actor=self.current_user.username):  # type: ignore[union-attr]
            messagebox.showinfo("Cancelled", f"Appointment {appt.appt_id} cancelled.")
            self.store.save_all()
            self.refresh_tree()

    def _complete_click(self) -> None:
        if not self._check_perm("complete"):
            return
        appt = self._selected_appt()
        if not appt:
            messagebox.showwarning("Select", "Choose an appointment first.")
            return
        summary = self.summary_text.get("1.0", "end").strip()
        if not summary:
            messagebox.showwarning("Missing", "Enter a summary first.")
            return
        if self.store.complete_appointment(appt.appt_id, summary, actor=self.current_user.username):  # type: ignore[union-attr]
            messagebox.showinfo("Completed", f"Appointment {appt.appt_id} completed.")
            self.store.save_all()
            self.refresh_tree()

    def _on_select(self, event: tk.Event) -> None:  # type: ignore[override]
        appt = self._selected_appt()
        if not appt:
            return
        details = (
            f"Appt {appt.appt_id}\n"
            f"Patient: {appt.patient_id}\nDoctor: {appt.doctor_id}\n"
            f"When: {appt.datetime_str}\nStatus: {appt.status}\nSummary: {appt.summary}"
        )
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", details)

    # ---- Helpers ----
    def _selected_appt(self) -> Optional[Appointment]:
        sel = self.tree.selection()
        if not sel:
            return None
        appt_id = self.tree.item(sel[0], "values")[0]
        return self.store.find_appointment(appt_id)

    def _load_doctors(self) -> None:
        values = [f"{d.id} - {d.name}" for d in self.store.doctors_by_id.values()]
        self.doctor_combo["values"] = values
        if values:
            self.doctor_combo.current(0)

    def _check_perm(self, action: str) -> bool:
        if not self.current_user or not self.current_user.can(action):
            messagebox.showerror("Permission denied", f"You cannot perform '{action}'")
            return False
        return True

    def refresh_tree(self) -> None:
        # filter by search entry
        query = self.search_entry.get().lower() if hasattr(self, "search_entry") else ""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for appt in self.store.appointments:
            patient = self.store.find_patient(appt.patient_id)
            name = patient.name.lower() if patient else ""
            if query and query not in appt.patient_id.lower() and query not in name:
                continue
            self.tree.insert(
                "",
                "end",
                values=(appt.appt_id, appt.patient_id, appt.doctor_id, appt.datetime_str, appt.status),
            )


def run_gui() -> None:
    root = tk.Tk()
    app = ClinicGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
