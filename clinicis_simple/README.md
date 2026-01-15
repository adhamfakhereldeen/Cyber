# ClinicIS – פרויקט גמר 

## הרצה
- הדגמת קונסול: `python main.py`
- GUI: `python gui.py`

> הערה: כרגע הפרויקט מוגדר ל-"Fresh Start" — בכל הרצה המערכת מאפסת את קבצי ה-JSON בתיקיית `data/` כדי להתחיל נקי.

## קבצים
- models.py – המחלקות Person/Patient/Doctor/Appointment + mixins.
- store.py – מחלקת Store עם dict patients/doctors ו-list appointments (שומר/טוען ל-data/).
- gui.py – ממשק Tkinter בסיסי (מסך אחד).
- main.py – יוצר אובייקטים, מפעיל כל הפונקציות, שומר/טוען JSON.

## פקדים ב-GUI
- Entry חיפוש מטופל.
- ttk.Combobox בחירת רופא.
- Entry Patient ID.
- Entry Date/Time.
- Button "קבע תור".
- Listbox תורים.
- Text סיכום ביקור.

## אירועים
- Button click על "קבע תור".
- בחירת פריט ב-Listbox (<<ListboxSelect>>) מציגה פרטי תור.
- הקשה Enter ב-Entry החיפוש מחפשת מטופל ומציגה הודעה.
