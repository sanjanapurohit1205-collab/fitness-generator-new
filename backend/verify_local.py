import requests
import time

print("Waiting for server...")
time.sleep(3)

try:
    # Need to login/setup session first, but generate-plan requires session.
    # Actually, let's just use Python requests with a Session object to simulate login then generate.
    s = requests.Session()
    
    # Login (creates user in DB)
    s.post('http://127.0.0.1:5000/login', data={'email': 'test@test.com'})
    
    # Submit Form (creates profile)
    s.post('http://127.0.0.1:5000/form', data={
        'name': 'Tester', 'height': '180', 'weight': '75', 
        'goal': 'Muscle Gain', 'time': '45', 'diet_type': 'Non-Veg', 'streak': '0'
    })
    
    # Generate Plan
    print("Requesting plan...")
    r = s.post('http://127.0.0.1:5000/generate-plan')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}...") # Print first 200 chars

except Exception as e:
    print(f"Error: {e}")