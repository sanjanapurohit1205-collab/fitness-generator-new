import requests
import time

print("Waiting for server...")
time.sleep(3)

# Test Config
BASE_URL = 'http://127.0.0.1:5000'
TEST_KEY = 'TEST_API_KEY_12345'

s = requests.Session()

# 1. Login to get session
print("Logging in...")
s.post(f'{BASE_URL}/login', data={'email': 'tester@test.com'})

# 2. Post to /settings (Simulating user pasting key)
print(f"Posting key: {TEST_KEY}")
r = s.post(f'{BASE_URL}/settings', data={'api_key': TEST_KEY})

if r.status_code == 200:
    print("Settings Update POST successful.")
else:
    print(f"Settings Update FAILED: {r.status_code}")

# 3. Check login page to see if it thinks key is configured
# (The template checks for key presence)
r = s.get(f'{BASE_URL}/login')
if "AI Active" in r.text or "Active" in r.text: # Broad check
    print("UI reports AI Active (or Setup Required changed state)")
else:
    print("UI Check: Result unclear (might verify manually)")

# 4. Read .env file directly to verify save
try:
    with open('.env', 'r') as f:
        content = f.read()
        if TEST_KEY in content:
            print("SUCCESS: Key found in .env file!")
        else:
            print("FAILURE: Key NOT found in .env file.")
except Exception as e:
    print(f"Error reading .env: {e}")