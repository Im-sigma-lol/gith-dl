import os
import sys
import requests
from time import sleep

GITHUB_API = "https://api.github.com"

def safe_filename(name):
    return "".join(c if c.isalnum() or c in " ._-()" else "_" for c in name)

def download_file(url, dest, headers=None):
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def fetch_all_repos(username):
    repos = []
    page = 1
    while True:
        r = requests.get(f"{GITHUB_API}/users/{username}/repos", params={"per_page": 100, "page": page})
        if r.status_code != 200:
            raise Exception(f"Failed to fetch repos: {r.text}")
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def fetch_releases(owner, repo):
    releases = []
    page = 1
    while True:
        r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/releases", params={"per_page": 100, "page": page})
        if r.status_code != 200:
            print(f"Failed to fetch releases for {repo}: {r.status_code}")
            break
        data = r.json()
        if not data:
            break
        releases.extend(data)
        page += 1
    return releases

def main():
    if len(sys.argv) < 2:
        print("Usage: python download_github_releases.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    base_folder = safe_filename(username)
    os.makedirs(base_folder, exist_ok=True)

    repos = fetch_all_repos(username)
    print(f"Found {len(repos)} repositories for {username}")

    for repo in repos:
        repo_name = repo["name"]
        print(f"\nChecking repo: {repo_name}")
        releases = fetch_releases(username, repo_name)
        if not releases:
            print("  No releases.")
            continue

        for rel in releases:
            rel_name = safe_filename(rel["tag_name"] or rel["name"])
            rel_folder = os.path.join(base_folder, repo_name, rel_name)
            os.makedirs(rel_folder, exist_ok=True)

            # Save release description
            body = rel.get("body", "")
            with open(os.path.join(rel_folder, "release_info.txt"), "w", encoding="utf-8") as f:
                f.write(body)

            # Download assets
            for asset in rel["assets"]:
                asset_name = safe_filename(asset["name"])
                asset_url = asset["browser_download_url"]
                print(f"  Downloading asset: {asset_name}")
                try:
                    download_file(asset_url, os.path.join(rel_folder, asset_name))
                except Exception as e:
                    print(f"    Failed: {e}")
                sleep(1)  # Avoid rate-limiting

            # Download source archives
            if rel.get("zipball_url"):
                print("  Downloading zipball source")
                try:
                    download_file(rel["zipball_url"], os.path.join(rel_folder, "source.zip"))
                except Exception as e:
                    print(f"    Failed: {e}")

            if rel.get("tarball_url"):
                print("  Downloading tarball source")
                try:
                    download_file(rel["tarball_url"], os.path.join(rel_folder, "source.tar.gz"))
                except Exception as e:
                    print(f"    Failed: {e}")

            sleep(1)

if __name__ == "__main__":
    main()
