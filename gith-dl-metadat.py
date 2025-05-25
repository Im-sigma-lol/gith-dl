# github_user_metadata.py
import os
import sys
import json
import hashlib
import httpx
from pathlib import Path

API_BASE = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json"}


def safe_mkdir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def md5sum(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def fetch_paginated(url):
    results = []
    while url:
        r = httpx.get(url, headers=HEADERS)
        r.raise_for_status()
        results.extend(r.json())
        url = r.links.get('next', {}).get('url')
    return results


def save_avatar(username, avatar_url):
    safe_mkdir(f"{username}/avatar")
    avatar_path = Path(f"{username}/avatar/avatar.png")
    tmp_path = Path(f"{username}/avatar/tmp.png")

    r = httpx.get(avatar_url)
    tmp_path.write_bytes(r.content)

    if avatar_path.exists() and md5sum(tmp_path) == md5sum(avatar_path):
        tmp_path.unlink()
    else:
        idx = 1
        while avatar_path.exists():
            avatar_path = Path(f"{username}/avatar/avatar({idx}).png")
            idx += 1
        tmp_path.rename(avatar_path)


def download_user_metadata(username):
    safe_mkdir(username)
    user_info = httpx.get(f"{API_BASE}/users/{username}", headers=HEADERS).json()
    save_json(f"{username}/profile.json", user_info)
    save_avatar(username, user_info.get("avatar_url", ""))

    repos = fetch_paginated(f"{API_BASE}/users/{username}/repos?per_page=100&type=all")
    save_json(f"{username}/repos.json", repos)

    for repo in repos:
        repo_name = repo['name']
        repo_dir = f"{username}/comments/repos/{repo_name}"
        safe_mkdir(repo_dir)

        # Save fork info for their own repos
        forks = fetch_paginated(f"{API_BASE}/repos/{username}/{repo_name}/forks")
        save_json(f"{repo_dir}/forks.json", forks)

        # Save upstream repo info if it's a fork
        if repo.get("fork") and repo.get("parent"):
            parent = repo["parent"]
            save_json(f"{repo_dir}/upstream_repo.json", parent)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python github_user_metadata.py <username>")
        sys.exit(1)

    download_user_metadata(sys.argv[1])
