import os
import sys
import json
import requests
import hashlib
from urllib.parse import urlparse

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def fetch_json(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def md5_file(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download_avatar(url, folder):
    avatar_dir = os.path.join(folder, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    
    # Get image
    r = requests.get(url, stream=True)
    r.raise_for_status()
    
    tmp_path = os.path.join(folder, "avatar.tmp")
    with open(tmp_path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    new_hash = md5_file(tmp_path)

    # Check existing files
    index = 0
    while True:
        if index == 0:
            target_name = "avatar.png"
        else:
            target_name = f"avatar ({index}).png"
        target_path = os.path.join(avatar_dir, target_name)

        if not os.path.exists(target_path):
            # New unique file
            os.rename(tmp_path, target_path)
            print(f"Saved new avatar: {target_name}")
            break
        elif md5_file(target_path) == new_hash:
            # Already exists
            os.remove(tmp_path)
            print(f"Duplicate avatar skipped: {target_name}")
            break
        else:
            index += 1

def main(username):
    folder = username
    os.makedirs(folder, exist_ok=True)

    user_data = fetch_json(f"https://api.github.com/users/{username}")
    save_json(user_data, os.path.join(folder, "user_profile.json"))

    # Avatar
    avatar_url = user_data.get("avatar_url")
    if avatar_url:
        download_avatar(avatar_url, folder)

    endpoints = {
        "followers": f"https://api.github.com/users/{username}/followers",
        "following": f"https://api.github.com/users/{username}/following",
        "orgs": f"https://api.github.com/users/{username}/orgs",
        "events": f"https://api.github.com/users/{username}/events",
        "received_events": f"https://api.github.com/users/{username}/received_events",
        "starred": f"https://api.github.com/users/{username}/starred",
        "subscriptions": f"https://api.github.com/users/{username}/subscriptions"
    }

    for name, url in endpoints.items():
        try:
            data = fetch_json(url)
            save_json(data, os.path.join(folder, f"{name}.json"))
        except Exception as e:
            print(f"Failed to fetch {name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_github_metadata.py <username>")
        sys.exit(1)
    main(sys.argv[1])
