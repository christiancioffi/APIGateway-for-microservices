import requests
import threading
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


URL = "https://localhost/authentication/login"
NUM_REQUESTS = 110

def send_request():
    try:
        data={"username":"user1", "password":"password"}

        response = requests.post(URL, json=data, verify=False)
        print(response.status_code)
    except requests.RequestException as e:
        print(f"Error: {e}")

# Creiamo e avviamo NUM_REQUESTS thread
threads = []
for _ in range(NUM_REQUESTS):
    thread = threading.Thread(target=send_request)
    thread.start()
    threads.append(thread)

# Aspettiamo che tutti i thread terminino
for thread in threads:
    thread.join()

print("All requests have been sent!")
