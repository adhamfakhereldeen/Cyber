# ClinicIS – מערכת ניהול מרפאה (Python 3.8.8 + Tkinter)

פרויקט גמר בקורס “מבוא לסייבר”. כולל לוגיקת OOP, GUI, הרשאות, לוגים ושמירה בקבצי JSON מקומיים (ללא DB וללא cache, ללא pickle).

## דרישות ותלויות
- Python 3.8.8
- ספריית Tkinter (מגיעה עם Python)

## הרצה מהירה
1. צרו סביבת עבודה וירטואלית (מומלץ) והפעילו `python -m pip install -r requirements.txt`.
2. הרצת הדגמת קונסול ללא GUI:  
   `python demo_main.py`
3. הרצת ה-GUI:  
   `python main.py`

## מבנה תיקיות
```
clinic_is/
  main.py
  demo_main.py
  gui_app.py
  models/
  core/
  data/
  logs/
  docs/
```

## מה יש בפרויקט
- OOP עם Person/Patient/Doctor/Appointment/User/Admin + Mixins ל-serialization ו-audit.
- ClinicStore מנהל את כל הישויות ושומר ל-JSON.
- RBAC בסיסי, hashing+salt לסיסמאות, לוג לאירועים רגישים.
- GUI עם Tkinter (חיפוש, קביעת תור, ביטול/סיום, תצוגת תורים).
- מדריך משתמש מפורט: `docs/USER_GUIDE.md`.
