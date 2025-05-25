import os
import sys
import json
import hashlib
import requests

API_BASE = "https://api.github.com"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def md5_file(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download_avatar(url, folder):
    avatar_dir = os.path.join(folder, "avatars")
    ensure_dir(avatar_dir)

    tmp_path = os.path.join(folder, "avatar.tmp")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(tmp_path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    new_hash = md5_file(tmp_path)
    index = 0
    while True:
        target = f"avatar{' (' + str(index) + ')' if index else ''}.png"
        target_path = os.path.join(avatar_dir, target)
        if not os.path.exists(target_path):
            os.rename(tmp_path, target_path)
            break
        elif md5_file(target_path) == new_hash:
            os.remove(tmp_path)
            break
        index += 1

def fetch_paginated(url):
    results = []
    page = 1
    while True:
        r = requests.get(url, params={"per_page": 100, "page": page})
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return results

def main(username):
    folder = username
    ensure_dir(folder)

    # User profile
    user_data = requests.get(f"{API_BASE}/users/{username}").json()
    save_json(user_data, os.path.join(folder, "user_profile.json"))

    # Avatar
    if 'avatar_url' in user_data:
        download_avatar(user_data['avatar_url'], folder)

    # Standard endpoints
    endpoints = {
        "followers": f"{API_BASE}/users/{username}/followers",
        "following": f"{API_BASE}/users/{username}/following",
        "orgs": f"{API_BASE}/users/{username}/orgs",
        "events": f"{API_BASE}/users/{username}/events",
        "received_events": f"{API_BASE}/users/{username}/received_events",
        "starred": f"{API_BASE}/users/{username}/starred",
        "subscriptions": f"{API_BASE}/users/{username}/subscriptions"
    }

    for name, url in endpoints.items():
        try:
            data = fetch_paginated(url)
            save_json(data, os.path.join(folder, f"{name}.json"))
        except Exception as e:
            print(f"Failed to fetch {name}: {e}")

    # Gist comments
    gist_dir = os.path.join(folder, "comments/gists")
    ensure_dir(gist_dir)
    try:
        gists = fetch_paginated(f"{API_BASE}/users/{username}/gists")
        for gist in gists:
            gid = gist["id"]
            comments = fetch_paginated(f"{API_BASE}/gists/{gid}/comments")
            save_json(comments, os.path.join(gist_dir, f"{gid}.json"))
    except Exception as e:
        print(f"Failed to fetch gist comments: {e}")

    # Repo comments
    repo_dir = os.path.join(folder, "comments/repos")
    ensure_dir(repo_dir)
    try:
        repos = fetch_paginated(f"{API_BASE}/users/{username}/repos")
        for repo in repos:
            name = repo["name"]
            path = os.path.join(repo_dir, name)
            ensure_dir(path)

            try:
                issue_comments = fetch_paginated(f"{API_BASE}/repos/{username}/{name}/issues/comments")
                save_json(issue_comments, os.path.join(path, "issue_comments.json"))
            except Exception as e:
                print(f"Issue comments failed for {name}: {e}")

            try:
                commit_comments = fetch_paginated(f"{API_BASE}/repos/{username}/{name}/comments")
                save_json(commit_comments, os.path.join(path, "commit_comments.json"))
            except Exception as e:
                print(f"Commit comments failed for {name}: {e}")

            try:
                pr_comments = fetch_paginated(f"{API_BASE}/repos/{username}/{name}/pulls/comments")
                save_json(pr_comments, os.path.join(path, "pr_comments.json"))
            except Exception as e:
                print(f"PR comments failed for {name}: {e}")
    except Exception as e:
        print(f"Failed to fetch repo comments: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_github_metadata.py <username>")
        sys.exit(1)
    main(sys.argv[1])
