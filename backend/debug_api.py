import requests

BASE_URL = "http://localhost:8000"
teacher_tz = "214980260"

session = requests.Session()
r = session.post(f"{BASE_URL}/auth/login?teacher_id_input={teacher_tz}")
if r.status_code == 200:
    print("Login successful. Fetching class students...")
    r2 = session.get(f"{BASE_URL}/students/my-class")
    print(r2.json())
else:
    print("Login failed", r.text)
