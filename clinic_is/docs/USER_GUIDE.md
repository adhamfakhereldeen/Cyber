# ClinicIS – מדריך משתמש

## כניסה
1. הפעל `python main.py`.
2. מסך Login: הזן שם משתמש וסיסמה (ברירת מחדל: admin / admin123).

## מסך ראשי ופקדים
- Entry חיפוש מטופל (ID/שם) + אירוע Enter לסינון.
- Combobox בחירת רופא.
- Entry ID מטופל ו-Entry שעת תור (YYYY-MM-DD HH:MM).
- Button “Schedule” לקביעת תור (אירוע click).
- Treeview להצגת התורים (אירוע בחירה <<TreeviewSelect>>).
- Text לסיכום ביקור (קלט רב-שורות).
- Buttons “Cancel Appointment” ו-“Complete Appointment”.

## אירועים (Events)
- הקלקת כפתור Schedule → יצירת תור דרך `ClinicStore.schedule_appointment`.
- בחירת שורה ב-Treeview → מציג פרטי התור וסיכום מתחת.
- הקשה Enter בשדה החיפוש → מסנן את רשימת התורים.

## תסריט שימוש
1. Login כ-admin.
2. חיפוש מטופל לפי ID או שם.
3. בחירת רופא מה-Combobox והזנת תאריך/שעה → Schedule.
4. לחיצה על תור ב-Treeview להצגת פרטים.
5. שינוי/ביטול תור באמצעות Cancel או השלמת תור עם Complete + כתיבת סיכום ב-Text.
6. כל פעולה נשמרת ב-JSON (תיקיית data/) ונרשמת בלוג (logs/audit.log).

## הרשאות (RBAC)
- admin: כל הפעולות (add_patient, add_doctor, schedule, cancel, complete, view_records, add_user, reset_password).
- doctor: schedule, cancel, complete, view_records.
- clerk: add_patient, add_doctor, schedule, cancel, view_records.

## קבצי נתונים ולוגים
- data/patients.json, doctors.json, appointments.json, users.json – נשמרים בקריאה/כתיבה דרך SerializableMixin.
- logs/audit.log – לוג JSON-לייני לכל פעולה רגישה (login/schedule/cancel/complete/add_user).

## מקומות לצילומי מסך
- Screenshot 1: מסך Login.
- Screenshot 2: מסך ראשי – חיפוש תורים.
- Screenshot 3: קביעת תור (Schedule).
- Screenshot 4: בחירת תור ב-Treeview.
- Screenshot 5: השלמת תור עם סיכום.
