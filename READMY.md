# 🌍 Hadasim Travel - School Trip Management System

מערכת לניהול ואיכון תלמידות בזמן אמת, שפותחה במסגרת תרגיל בית לתוכנית הדסים.

---

## 📋 תיאור הפרויקט
המערכת נועדה לסייע למורות בניהול טיול שנתי.  
היא מאפשרת:

- ניהול תלמידות ומורות
- שליפת מידע דרך API
- צפייה במיקומי תלמידות בזמן אמת על גבי מפה
- בדיקת תלמידות שהתרחקו 

המערכת מבוססת על ארכיטקטורת Client-Server ומורכבת מ־Backend ו־Frontend.

---

### ✨ Key Features
- **DMS Integration:** תמיכה מלאה בקבלת קואורדינטות בפורמט צבאי (DMS) והמרתן למערכת עשרונית.
-**Smart Distance Logic (Bonus):** אלגוריתם המחשב מרחק אווירי בזמן אמת ומספק התראות ויזואליות על תלמידות שנמצאות מעל 3 ק"מ מהמורה.
- **Real-time Monitoring:** מעקב חי אחרי מיקומי תלמידות על גבי מפת OpenLayers.
- **DMS Conversion:** לוגיקה ייעודית להמרת קואורדינטות ממעלות/דקות/שניות (DMS) לערכים עשרוניים.
- **Distance Analytics (Bonus):** חישוב מרחק אוטונומי המתריע על תלמידות שחורגות מרדיוס של 3 ק"מ מהמורה המלווה.
- **Auto-Sync:** סנכרון נתונים אוטומטי בין ה-Backend ל-Frontend ללא צורך ברענון ידני.

## 🚀 הרצה והתקנה (Docker)

המערכת ניתנת להרצה מלאה באמצעות Docker Compose, ללא צורך בהתקנות מקומיות של מסד נתונים או סביבות ריצה.

### דרישות קדם
- Docker Desktop
- Git

---

### ▶️ שלבי הרצה

```bash
git clone https://github.com/YOUR_USERNAME/hadasim-travel-system.git
cd hadasim-travel-system
docker-compose up --build
```
באופן אוטומטי אם הבסיס נתונים של המורות ריק יש מורה Admin, Admin, 12345678, כיתה: A 
על מנת שיהיה ניתן להכניס את המורה הראשונה 

לכן ניתן להכנס למערכת בפעם הראשונה עם הת"ז: 12345678

---

### ▶️ גישה למערכת 


Frontend: http://localhost:5173
Backend (Swagger): http://localhost:8000/docs

API עיקרי
Authentication
POST /auth/login
POST /auth/logout
Students
GET /students/
GET /students/{id}
GET /students/my-class
POST /students/
Teachers
GET /teachers/
GET /teachers/{id}
POST /teachers/ 
Locations
POST /locations/update Update Location
GET /locations/{student_tz}/last-location
GET /locations/{student_tz}/path
GET /locations/class-last-locations
GET /locations/far-students

### הרשאות
רק מורה יכולה לגשת ל־API
מורה יכולה לצפות רק בתלמידות מהכיתה שלה

### 📸 צילומי מסך
<p align="center">
  <img src="screenshots/map.png" width="400" alt="מפת איכון בזמן אמת">
  <img src="screenshots/login.png" width="400" alt="מסך התחברות">
  <img src="screenshots/UI.png" width="400" alt="מסך בית">

</p>

---

###  טכנלוגיות ושפות 

Backend: Python (FastAPI), SQLModel (Pydantic + SQLAlchemy).

Frontend: React (Vite), Axios, OpenLayers (Map Integration).

DevOps: Docker & Docker Compose.

Database: SQLite (Relational storage for locations & users).

### 📦 מבנה הפרויקט
/backend – שרת ה־API
/frontend – צד לקוח
docker-compose.yml – הגדרת שירותים
