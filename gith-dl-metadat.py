#!/usr/bin/env python3 import os import sys import json import hashlib import requests

API_BASE = "https://api.github.com" HEADERS = { "Accept": "application/vnd.github.squirrel-girl-preview+json" }

def ensure_dir(path): os.makedirs(path, exist_ok=True)

def save_json(data, path): with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)

def md5_file(filepath): hash_md5 = hashlib.md5() with open(filepath, "rb") as f: for chunk in iter(lambda: f.read(4096), b""): hash_md5.update(chunk) return hash_md5.hexdigest()

def download_avatar(url, folder): avatar_dir = os.path.join(folder, "profile", "avatars") ensure_dir(avatar_dir) tmp_path = os.path.join(avatar_dir, "avatar.tmp") r = requests.get(url, stream=True, headers=HEADERS) r.raise_for_status() with open(tmp_path, "wb") as f: for chunk in r.iter_content(1024): f.write(chunk) new_hash = md5_file(tmp_path) index = 0 while True: target = f"avatar{' (' + str(index) + ')' if index else ''}.png" target_path = os.path.join(avatar_dir, target) if not os.path.exists(target_path): os.rename(tmp_path, target_path) break elif md5_file(target_path) == new_hash: os.remove(tmp_path) break index += 1

def fetch_paginated(url): results = [] page = 1 while True: r = requests.get(url, params={"per_page": 100, "page": page}, headers=HEADERS) r.raise_for_status() data = r.json() if not data: break results.extend(data) page += 1 return results

def fetch_reactions_for_comments(comment_list, reaction_url_format): reactions = [] for comment in comment_list: cid = comment["id"] url = reaction_url_format.format(cid=cid) try: reacts = fetch_paginated(url) reactions.append({"id": cid, "reactions": reacts}) except Exception as e: print(f"Failed to fetch reactions for comment {cid}: {e}") return reactions

def main(username): base_folder = username ensure_dir(base_folder)

# Profile
profile_dir = os.path.join(base_folder, "profile")
ensure_dir(profile_dir)
user_data = requests.get(f"{API_BASE}/users/{username}", headers=HEADERS).json()
save_json(user_data, os.path.join(profile_dir, "user.json"))
if 'avatar_url' in user_data:
    download_avatar(user_data['avatar_url'], base_folder)

# Basic endpoints
metadata_dir = os.path.join(base_folder, "metadata")
ensure_dir(metadata_dir)
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
        save_json(data, os.path.join(metadata_dir, f"{name}.json"))
    except Exception as e:
        print(f"Failed to fetch {name}: {e}")

# Gists
gist_dir = os.path.join(base_folder, "gists")
ensure_dir(gist_dir)
gists = fetch_paginated(f"{API_BASE}/users/{username}/gists")
for gist in gists:
    gid = gist["id"]
    gpath = os.path.join(gist_dir, gid)
    ensure_dir(gpath)
    save_json(gist, os.path.join(gpath, "gist.json"))
    comments = fetch_paginated(f"{API_BASE}/gists/{gid}/comments")
    save_json(comments, os.path.join(gpath, "comments.json"))
    if comments:
        reacts = fetch_reactions_for_comments(
            comments,
            reaction_url_format=f"{API_BASE}/gists/{gid}/comments/{{cid}}/reactions"
        )
        save_json(reacts, os.path.join(gpath, "reactions.json"))

# Repos
repos = fetch_paginated(f"{API_BASE}/users/{username}/repos")
repos_dir = os.path.join(base_folder, "repos")
ensure_dir(repos_dir)
for repo in repos:
    rname = repo["name"]
    rpath = os.path.join(repos_dir, rname)
    ensure_dir(rpath)
    save_json(repo, os.path.join(rpath, "repo.json"))
    # Comments and reactions
    def store_comments(type_, endpoint):
        try:
            comments = fetch_paginated(endpoint)
            save_json(comments, os.path.join(rpath, f"{type_}_comments.json"))
            if comments:
                reacts = fetch_reactions_for_comments(
                    comments,
                    f"{endpoint}/{{cid}}/reactions".replace("/comments", "/comments")
                )
                save_json(reacts, os.path.join(rpath, f"{type_}_reactions.json"))
        except Exception as e:
            print(f"{type_} failed for {rname}: {e}")
    store_comments("issue", f"{API_BASE}/repos/{username}/{rname}/issues/comments")
    store_comments("commit", f"{API_BASE}/repos/{username}/{rname}/comments")
    store_comments("pr", f"{API_BASE}/repos/{username}/{rname}/pulls/comments")
    try:
        contributors = fetch_paginated(f"{API_BASE}/repos/{username}/{rname}/contributors")
        save_json(contributors, os.path.join(rpath, "contributors.json"))
        stargazers = fetch_paginated(f"{API_BASE}/repos/{username}/{rname}/stargazers")
        save_json(stargazers, os.path.join(rpath, "stargazers.json"))
        subscribers = fetch_paginated(f"{API_BASE}/repos/{username}/{rname}/subscribers")
        save_json(subscribers, os.path.join(rpath, "subscribers.json"))
        forks = fetch_paginated(f"{API_BASE}/repos/{username}/{rname}/forks")
        save_json(forks, os.path.join(rpath, "forks.json"))
    except Exception as e:
        print(f"Failed to fetch repo metadata for {rname}: {e}")

if name == "main": if len(sys.argv) != 2: print("Usage: python3 github_metadata_archiver.py <username>") sys.exit(1) main(sys.argv[1])

