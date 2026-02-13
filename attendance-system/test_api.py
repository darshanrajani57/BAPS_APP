import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_api():
    try:
        # Get all sessions
        print("Fetching all sessions...")
        try:
            res = requests.get(f"{BASE_URL}/sessions")
        except requests.exceptions.ConnectionError:
            print("Failed to connect to backend. Is it running?")
            return

        print(f"Sessions Status: {res.status_code}")
        if res.status_code != 200:
            print(f"Failed to get sessions. Response: {res.text}")
            return

        sessions = res.json().get('data', [])
        print(f"Found {len(sessions)} sessions")

        if not sessions:
            print("No sessions to test details/report")
            
            # Create a dummy session for testing
            print("Creating dummy session...")
            res = requests.post(f"{BASE_URL}/sessions", json={
                "date": "2024-01-01",
                "start_time": "10:00",
                "end_time": "12:00",
                "status": "ENDED"
            })
            print(f"Create Status: {res.status_code}")
            if res.status_code == 201:
                session_id = res.json().get('id')
                print(f"Created session: {session_id}")
            else:
                print(f"Failed to create session. Response: {res.text}")
                return
        else:
            session_id = sessions[0]['id']
            print(f"Testing with session: {session_id}")

        # Get session details
        print(f"Fetching details for {session_id}...")
        res = requests.get(f"{BASE_URL}/sessions/{session_id}")
        print(f"Details Status: {res.status_code}")
        if res.status_code != 200:
            print(f"Details Error: {res.text}")
        else:
            print("Details OK")

        # Get session report
        print(f"Fetching report for {session_id}...")
        res = requests.get(f"{BASE_URL}/sessions/{session_id}/report")
        print(f"Report Status: {res.status_code}")
        if res.status_code != 200:
            try:
                error_msg = res.json().get('message', res.text)
                print(f"Report Error: {error_msg}")
            except:
                print(f"Report Error (Raw): {res.text}")
        else:
            print("Report OK")

    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    test_api()
