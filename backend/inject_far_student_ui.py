import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def inject_test_data():
    print("מתחיל בעדכון מיקומים לשרת שלך...")
    session = requests.Session()
    
    teacher_tz = "214980260"
    
    # 1. התחברות
    r = session.post(f"{BASE_URL}/auth/login?teacher_id_input={teacher_tz}")
    if r.status_code != 200:
        print(f"❌ שגיאה: לא הצלחתי להתחבר למורה עם ת\"ז {teacher_tz}.")
        print("תוצאה:", r.text)
        return
        
    teacher_data = r.json()
    class_name = teacher_data.get("class_name")
    print(f"✅ התחברות בהצלחה כמורה {teacher_data.get('first_name')}. כיתה: {class_name}")
    
    # 2. שליפת התלמידות הקיימות בכיתה
    r = session.get(f"{BASE_URL}/students/my-class")
    if r.status_code != 200:
        print("❌ לא הצלחתי לשלוף את רשימת התלמידות.")
        return
        
    existing_students = r.json()
    print(f"✅ נמצאו {len(existing_students)} תלמידות קיימות בכיתה. מעדכן להן מיקום קרוב...")

    # 3. פונקציית עזר לעדכון מיקום
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
            return True
        else:
            print(f"❌ שגיאה בעדכון מיקום עבור {tz}: {res.text}")
            return False

    # 4. מיקום המורה (ירושלים)
    teacher_lat = 31.7767
    teacher_lon = 35.2345
    send_location(teacher_tz, teacher_lat, teacher_lon)
    print("📍 מיקום המורה עודכן בהצלחה.")
    
    # 5. עדכון כל התלמידות הקיימות למיקום *ממש קרוב* (מרחק של כמה עשרות מטרים)
    for s in existing_students:
        # נוסיף קצת רנדומליות זעירה כדי שלא כולן יהיו באותה נקודה מדויקת
        send_location(s["tz"], teacher_lat + 0.001, teacher_lon + 0.001)

    print("📍 המיקומים של כל התלמידות הקיימות עודכנו ל'קרוב מאוד' (פחות מ-3 ק\"מ).")

    # 6. יצירת תלמידה חדשה ורחוקה
    far_tz = "999999999"
    r = session.post(f"{BASE_URL}/students/", json={
        "tz": far_tz,
        "first_name": "תלמידה",
        "last_name": "רחוקה",
        "class_name": class_name
    })
    
    if r.status_code in (200, 400):
        # 400 אומר שהיא כבר קיימת - זה בסדר
        pass
    else:
        print("❌ בעיה ביצירת התלמידה הרחוקה:", r.text)

    # נציב אותה באילת (בוודאות מעל 3 ק"מ מירושלים)
    far_lat = 29.5581
    far_lon = 34.9482
    send_location(far_tz, far_lat, far_lon)
    
    print("📍 נוצרה/עודכנה תלמידה חדשה בשם 'תלמידה רחוקה' עם מיקום רחוק מאוד (אילת).")
    print("\n🎉 סיום! כעת עברי ל-UI.")
    print("1. היכנסי למפת הטיול (Live).")
    print("2. המתיני לרענון האוטומטי או רענני את הדף.")
    print("3. את אמורה לראות בפאנל החריגות *רק* את 'תלמידה רחוקה' (ועוד מישהי אם קיימת בעבר אצלך שרחוקה). שאר כיתת ג1 לא תופיע בפאנל!")

if __name__ == "__main__":
    inject_test_data()
