import requests
import time
from datetime import datetime, timezone

# הגדרות השרת - ודאי שהבאקנד בדוקר רץ
BASE_URL = "http://localhost:8000"
ENDPOINT = "/locations/update"

# רשימת התלמידות עם מיקומים שונים (ירושלים, ת"א, חיפה, באר שבע)
students_data = [
    {
        "ID": "11111111", 
        "name": "חנה בן",
        "lon": {"Degrees": "35", "Minutes": "13", "Seconds": "05"},
        "lat": {"Degrees": "31", "Minutes": "46", "Seconds": "20"}
    },
    {
        "ID": "22222222", 
        "name": "חוה כהן",
        "lon": {"Degrees": "34", "Minutes": "48", "Seconds": "10"},
        "lat": {"Degrees": "32", "Minutes": "05", "Seconds": "15"}
    },
    {
        "ID": "33333333", 
        "name": "רחל לוי",
        "lon": {"Degrees": "34", "Minutes": "59", "Seconds": "30"},
        "lat": {"Degrees": "32", "Minutes": "48", "Seconds": "40"}
    },
    {
        "ID": "44444444", 
        "name": "רפאלה חננאל",
        "lon": {"Degrees": "34", "Minutes": "53", "Seconds": "50"},
        "lat": {"Degrees": "31", "Minutes": "15", "Seconds": "10"}
    }
]

def send_location(student):
    payload = {
        "ID": student["ID"],
        "Coordinates": {
            "Longitude": student["lon"],
            "Latitude": student["lat"]
        },
        # פורמט זמן ISO 8601 כפי שנדרש
        "Time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    try:
        response = requests.post(f"{BASE_URL}{ENDPOINT}", json=payload)
        
        if response.status_code == 200:
            print(f"✅ עודכן מיקום עבור {student['name']} ({student['ID']})")
        elif response.status_code == 404:
            print(f"❌ תלמידה {student['ID']} לא נמצאה בבסיס הנתונים.")
        else:
            print(f"⚠️ שגיאה {response.status_code} עבור {student['ID']}: {response.text}")
            
    except Exception as e:
        print(f"🔥 שגיאת תקשורת: {e}")

if __name__ == "__main__":
    print("🚀 מתחיל שליחת מיקומים למערכת...")
    for student in students_data:
        send_location(student)
        time.sleep(0.5) # השהייה קלה כדי לא להעמיס
    print("\n🏁 סיום שליחה. בדקי את המפה עכשיו!")