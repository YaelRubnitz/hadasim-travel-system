import requests
import time
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def seed_data():
    print("מתחיל בהזרקת נתוני הבדיקה דרך ה-API...")
    session = requests.Session()
    
    admin_tz = "12345678"
    teacher_tz = "214980260"
    class_name = "ClassUI"
    
    # 1. Login as Admin
    try:
        r = session.post(f"{BASE_URL}/auth/login?teacher_id_input={admin_tz}")
    except requests.exceptions.ConnectionError:
        print("❌ לא ניתן להתחבר לשרת. ודאי שהקונטיינרים רצים (docker-compose up) ופורט 8000 פתוח.")
        return
    if r.status_code != 200:
        print(f"לא הצלחתי להתחבר כאדמין (ת\"ז 12345678). מנסה להתחבר כמורה {teacher_tz} ישירות.")
        r = session.post(f"{BASE_URL}/auth/login?teacher_id_input={teacher_tz}")
        if r.status_code != 200:
            print("לא הצלחתי להתחבר. ודאי שהשרת פועל בפורט 8000 (docker-compose up).")
            return
    else:
        # 2. Create the Teacher
        r = session.post(f"{BASE_URL}/teachers/", json={
            "tz": teacher_tz,
            "first_name": "שרה",
            "last_name": "לוי",
            "class_name": class_name
        })
        if r.status_code in (200, 400):
            print(f"✅ מורה עם ת\"ז {teacher_tz} נוצרה או כבר קיימת.")
        else:
            print(f"❌ שגיאה ביצירת מורה: {r.text}")
            return
            
    # 3. Login as the new Teacher
    session = requests.Session()
    r = session.post(f"{BASE_URL}/auth/login?teacher_id_input={teacher_tz}")
    if r.status_code != 200:
        print("❌ שגיאה בהתחברות כמורה החדשה.")
        return

    # 4. Create Students
    students = [
        {"tz": "300000001", "first_name": "קרובה", "last_name": "אחת", "lat": 31.7767, "lon": 35.2350},
        {"tz": "300000002", "first_name": "קרובה", "last_name": "שתיים", "lat": 31.7770, "lon": 35.2345},
        {"tz": "300000003", "first_name": "רחוקה", "last_name": "אחת", "lat": 31.85, "lon": 35.30},
        {"tz": "300000004", "first_name": "רחוקה", "last_name": "שתיים", "lat": 32.0, "lon": 34.8},
        {"tz": "300000005", "first_name": "חסרת", "last_name": "מיקום", "lat": None, "lon": None},
    ]

    for s in students:
        r = session.post(f"{BASE_URL}/students/", json={
            "tz": s["tz"],
            "first_name": s["first_name"],
            "last_name": s["last_name"],
            "class_name": class_name
        })
        if r.status_code in (200, 400):
            print(f"✅ תלמידה {s['first_name']} {s['last_name']} נוצרה/קיימת.")
        else:
            print(f"❌ שגיאה ביצירת תלמידה {s['tz']}: {r.text}")

    # 5. Send Locations
    def send_location(tz, lat, lon):
        if lat is None or lon is None:
            return
        payload = {
            "ID": tz,
            "Coordinates": {
                # טריק קטן: שלחים את המעלות כמספר עשרוני, דקות ושניות כ-0
                "Latitude": {"Degrees": str(lat), "Minutes": "0", "Seconds": "0"},
                "Longitude": {"Degrees": str(lon), "Minutes": "0", "Seconds": "0"}
            },
            "Time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        # הפעולה של עדכון מיקום לא דורשת Auth במערכת הנוכחית
        res = requests.post(f"{BASE_URL}/locations/update", json=payload)
        if res.status_code == 200:
            print(f"📍 מיקום עודכן עבור ת\"ז {tz}")
        else:
            print(f"❌ שגיאה בעדכון מיקום עבור ת\"ז {tz}: {res.text}")

    # Teacher location
    send_location(teacher_tz, 31.7767, 35.2345)
    
    # Students location
    for s in students:
        send_location(s["tz"], s["lat"], s["lon"])

    print("\n🎉 סיום! כל הנתונים הוזרקו בהצלחה.")
    print("כעת ניתן לפתוח את ה-UI ולהתחבר עם ת\"ז: 214980260")

if __name__ == "__main__":
    seed_data()
