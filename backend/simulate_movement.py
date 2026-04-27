import requests
import time
import random
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
STUDENTS = [f"1234567{i:02d}" for i in range(1, 11)]

def move_students():
    print("🚗 סימולציית תנועה קיצונית התחילה...")
    
    while True:
        for tz in STUDENTS:
            # שינוי קיצוני: כל תלמידה מקבלת קואורדינטות אקראיות לגמרי באזור המרכז
            # שיניתי את ה-Degrees וה-Minutes כדי שהן "יקפצו" מרחקים גדולים
            new_lat_min = random.randint(0, 59)
            new_lon_min = random.randint(0, 59)

            payload = {
                "ID": tz,
                "Coordinates": {
                    "Longitude": {"Degrees": "34", "Minutes": str(new_lon_min), "Seconds": str(random.randint(0, 59))},
                    "Latitude": {"Degrees": "31", "Minutes": str(new_lat_min), "Seconds": str(random.randint(0, 59))}
                },
                "Time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }

            try:
                requests.post(f"{BASE_URL}/locations/update", json=payload)
            except Exception as e:
                print(f"❌ שגיאה בחיבור לשרת: {e}")

        print(f"🚀 בוצע עדכון לכולן ב-{datetime.now().strftime('%H:%M:%S')}. בדקי את המפה!")
        time.sleep(5)

if __name__ == "__main__":
    move_students()