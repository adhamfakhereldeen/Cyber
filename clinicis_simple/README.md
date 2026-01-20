# ClinicIS – פרויקט גמר

מסמך זה משמש כהנחיות הפעלה מלאות למערכת (GUI + קונסול), כולל פירוט פקדים, אירועים ושימוש בכל הפונקציות. יש להוסיף צילומי מסך לפי המקומות המסומנים.

## הרצה
- קונסול (דמו לכל הפונקציות): `python main.py`
- GUI: `python gui.py`

> הערה: המערכת מוגדרת ל-"Fresh Start" — בכל הרצה היא מאפסת את קבצי ה-JSON בתיקיית `data/`.

## מבנה קבצים
- models.py – מחלקות Person/Patient/Doctor/Appointment + mixins.
- clinic.py – מחלקת Clinic (מחלקת מערכת מרכזית) עם dict/list ושמירה/טעינה.
- gui.py – ממשק Tkinter.
- main.py – דוגמאות אתחול והרצה לכל האובייקטים והפונקציות.

## הפעלת GUI – שלב אחר שלב
1. הריצו: `python gui.py`.
2. ייפתח חלון ClinicIS.
3. ניתן להוסיף מטופלים ורופאים דרך כפתורי “Add Patient” ו-“Add Doctor”.
4. בחרו מטופל ורופא מהרשימות, הזינו תאריך/שעה בפורמט: dd-mm-yyyy/hh:mm.
5. לחצו “קבע תור” ליצירת תור.
6. בחרו תור מהרשימה כדי לראות את הפרטים בתיבת “Appointment Details”.
7. הזינו סיכום ביקור ולחצו “Complete”, או בטלו/מחקו/שנו תור לפי הצורך.

### צילומי מסך (יש להוסיף)
- צילום מסך של המסך הראשי לאחר פתיחת GUI.
- צילום מסך של חלון “Add Patient”.
- צילום מסך של חלון “Add Doctor”.
- צילום מסך לאחר יצירת תור והצגת פרטים.

## פקדים ב-GUI
1. Entry חיפוש מטופל (Patient ID/Name).
2. Button “Search”.
3. Text “Patient Details”.
4. Buttons “Add Patient” ו-“Add Doctor” (פותחים חלונות קופצים).
5. Combobox בחירת רופא.
6. Combobox בחירת מטופל.
7. Entry תאריך/שעה + שורת פורמט.
8. Button “קבע תור”.
9. Listbox תורים.
10. Text “Appointment Details”.
11. Text “Visit Summary”.
12. Buttons: Complete / Cancel / Delete / Reschedule.

## אירועים במערכת (Events)
1. הקשה Enter בשדה החיפוש – מפעיל חיפוש מטופל.
2. לחיצה על Button “Search” – חיפוש מטופל.
3. לחיצה על Button “קבע תור” – יצירת תור.
4. בחירת פריט ב-Listbox – הצגת פרטי התור.
5. לחיצות על Complete / Cancel / Delete / Reschedule – עדכון סטטוס התור.
6. לחיצה על Add Patient / Add Doctor – פתיחת חלון קופץ והוספה.

## שימוש בכל פונקציות המערכת (Clinic)
להלן פירוט הפעולות שכל פונקציה מבצעת ואיך מפעילים אותן:
- add_patient: הוספת מטופל חדש (דרך חלון Add Patient או ב-main.py).
- add_doctor: הוספת רופא חדש (דרך חלון Add Doctor או ב-main.py).
- schedule_appointment: קביעת תור חדש (כפתור “קבע תור”).
- reschedule_appointment: שינוי זמן לתור קיים (כפתור “Reschedule”).
- cancel_appointment: ביטול תור (כפתור “Cancel”).
- delete_appointment: מחיקת תור (כפתור “Delete”).
- complete_appointment: סיום תור והוספת סיכום ביקור (כפתור “Complete”).
- save_to_files / load_from_files: שמירה וטעינה אוטומטיים לקבצי JSON.

## הפעלת קונסול (main.py)
הרצה של `python main.py` מדגימה:
- יצירת אובייקטים (מטופלים/רופאים/תורים).
- הפעלת כל הפונקציות הלוגיות.
- שמירה וטעינה מקבצי JSON.

### צילומי מסך לקונסול (יש להוסיף)
- צילום מסך של פלט הרצה של main.py.
