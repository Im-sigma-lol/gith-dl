import os
import sys
import json
import requests

BASE_URL = "https://api.github.com/users/"

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def fetch_json(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def main(username):
    folder = username
    os.makedirs(folder, exist_ok=True)

    user_data = fetch_json(BASE_URL + username)
    save_json(user_data, f"{folder}/user_profile.json")

    endpoints = {
        "followers": f"{BASE_URL}{username}/followers",
        "following": f"{BASE_URL}{username}/following",
        "orgs": f"{BASE_URL}{username}/orgs",
        "events": f"{BASE_URL}{username}/events",
        "received_events": f"{BASE_URL}{username}/received_events",
        "starred": f"{BASE_URL}{username}/starred",
        "subscriptions": f"{BASE_URL}{username}/subscriptions"
    }

    for name, url in endpoints.items():
        try:
            data = fetch_json(url)
            save_json(data, f"{folder}/{name}.json")
        except Exception as e:
            print(f"Failed to fetch {name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_github_metadata.py <username>")
        sys.exit(1)
    main(sys.argv[1])
