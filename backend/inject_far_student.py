import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def inject_far_student():
    print("מתחיל בהוספת תלמידה רחוקה...")
    session = requests.Session()
    
    teacher_tz = "214980260"
    
    # 1. התחברות בתור המורה כדי לגלות את שם הכיתה שלה
    r = session.post(f"{BASE_URL}/auth/login?teacher_id_input={teacher_tz}")
    if r.status_code != 200:
        print(f"❌ שגיאה: לא הצלחתי להתחבר למורה עם ת\"ז {teacher_tz}.")
        print("ודאי שהשרת פועל ושהמורה קיימת במערכת.")
        return
        
    teacher_data = r.json()
    class_name = teacher_data.get("class_name")
    print(f"✅ התחברות בהצלחה כמורה {teacher_data.get('first_name')}. כיתה: {class_name}")
    
    # 2. יצירת התלמידה הרחוקה
    far_student = {
        "tz": "999999999", 
        "first_name": "בדיקה", 
        "last_name": "רחוקה", 
        "class_name": class_name
    }
    
    r = session.post(f"{BASE_URL}/students/", json=far_student)
    if r.status_code in (200, 400):
        print(f"✅ התלמידה (ת\"ז 999999999) נוצרה או כבר קיימת בכיתה {class_name}.")
    else:
        print(f"❌ שגיאה ביצירת התלמידה: {r.text}")
        return

    # 3. עדכון מיקום התלמידה הרחוקה (למשל באילת - בוודאות יותר מ-3 ק"מ מכל מקום במרכז/ירושלים)
    lat = 29.5581
    lon = 34.9482
    
    payload = {
        "ID": far_student["tz"],
        "Coordinates": {
            "Latitude": {"Degrees": str(lat), "Minutes": "0", "Seconds": "0"},
            "Longitude": {"Degrees": str(lon), "Minutes": "0", "Seconds": "0"}
        },
        "Time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    res = requests.post(f"{BASE_URL}/locations/update", json=payload)
    if res.status_code == 200:
        print("📍 מיקום רחוק (אילת) עודכן בהצלחה לתלמידה!")
        print("כעת רענני את ה-UI או המתיני לעדכון, והתלמידה 'בדיקה רחוקה' אמורה להופיע ברשימת החריגות מתחת למפה.")
    else:
        print(f"❌ שגיאה בעדכון מיקום: {res.text}")

if __name__ == "__main__":
    inject_far_student()
