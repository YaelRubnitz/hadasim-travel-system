import requests
from datetime import datetime, timezone
import math

BASE_URL = "http://localhost:8000"

def inject_locations_for_existing_students():
    print("מתחיל בהזרקת מיקומים לתלמידות הקיימות...")
    session = requests.Session()
    
    teacher_tz = "214980260"
    
    # 1. Login to get teacher info
    r = session.post(f"{BASE_URL}/auth/login?teacher_id_input={teacher_tz}")
    if r.status_code != 200:
        print(f"❌ שגיאה: לא הצלחתי להתחבר למורה עם ת\"ז {teacher_tz}.")
        return
        
    teacher_data = r.json()
    class_name = teacher_data.get("class_name")
    print(f"✅ התחברות בהצלחה כמורה {teacher_data.get('first_name')}. כיתה: {class_name}")
    
    # 2. Get students in this class
    r = session.get(f"{BASE_URL}/students/my-class")
    if r.status_code != 200:
        print("❌ לא הצלחתי לשלוף את רשימת התלמידות.")
        return
        
    students = r.json()
    print(f"✅ נמצאו {len(students)} תלמידות בכיתה.")

    # 3. Send locations
    def send_location(tz, lat, lon):
        payload = {
            "ID": tz,
            "Coordinates": {
                "Latitude": {"Degrees": str(lat), "Minutes": "0", "Seconds": "0"},
                "Longitude": {"Degrees": str(lon), "Minutes": "0", "Seconds": "0"}
            },
            "Time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        res = requests.post(f"{BASE_URL}/locations/update", json=payload)
        if res.status_code == 200:
            print(f"📍 מיקום עודכן עבור ת\"ז {tz}")
        else:
            print(f"❌ שגיאה בעדכון מיקום עבור ת\"ז {tz}: {res.text}")

    teacher_lat = 31.7767
    teacher_lon = 35.2345
    send_location(teacher_tz, teacher_lat, teacher_lon)
    
    for i, s in enumerate(students):
        tz = s["tz"]
        if i % 3 == 0:
            # קרובות
            send_location(tz, teacher_lat + 0.005, teacher_lon)
        elif i % 3 == 1:
            # רחוקות מאוד
            send_location(tz, teacher_lat + 0.1, teacher_lon)
        else:
            # ללא מיקום כלל
            print(f"⚪ מדלג על {tz} כדי שתהיה חסרת מיקום.")

    print("\n🎉 סיום! כל הנתונים הוזרקו בהצלחה.")
    print("כעת חזרי ל-UI, ודאי שאת בדף המפה, והמתיני כמה שניות לרענון.")

if __name__ == "__main__":
    inject_locations_for_existing_students()
