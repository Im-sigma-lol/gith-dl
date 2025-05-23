
# GitHub Account Archiver Setup Guide

## Installation

```bash
REPO_URL="https://github.com/Im-sigma-lol/gith-dl"; INSTALL_BIN="/data/data/com.termux/files/usr/bin/gith-dl"; command -v git >/dev/null 2>&1 || pkg install -y git; [ -f "$INSTALL_BIN" ] || { TEMP=$(mktemp -d) && git clone "$REPO_URL" "$TEMP" && cd "$TEMP" && bash install.sh && cd - && rm -rf "$TEMP"; }
```

This installs `gith-dl` if it is not already present on your system.

---

## Archiving GitHub Data

### To archive all repositories:
```bash
gith-dl -repo
```

### To archive all public gists:
```bash
gith-dl -gist
```

---

## What Are Repositories and Gists?

- **Repository (repo):** A full project directory that contains code, folders, and Git history.
- **Gist:** A lightweight way to share code snippets or small scripts. Each gist is treated like its own mini-repo.

> **Note:** This tool archives entire GitHub accounts. It **does not support secret gists** unless downloaded manually.

---

## Understanding the Output

After archiving, a folder will be created in your current directory using the GitHub account name (e.g., `MainScripts352`). Inside this folder are `.git` directories — these are **bare repositories**, which are not yet readable like regular project folders.

---

## Making Archived Repos Readable (Checkout)

To convert the `.git` folders into readable project directories, run the following **checkout script** from inside the account folder:

```bash
#!/bin/bash

flat_mode=0
if [ "$1" = "1" ]; then
    flat_mode=1
fi

mkdir -p CHECKOUT

for account_dir in */; do
    [ -d "$account_dir" ] || continue

    account_name="${account_dir%/}"
    base_target_dir="CHECKOUT/$account_name"
    mkdir -p "$base_target_dir"

    echo "Processing account: $account_name"

    for git_repo in "$account_dir"/*.git; do
        [ -d "$git_repo" ] || continue

        repo_name=$(basename "$git_repo" .git)
        target_dir="$base_target_dir"
        [ "$flat_mode" -eq 0 ] && target_dir="$base_target_dir/$repo_name"
        mkdir -p "$target_dir"

        metadata_file="$target_dir/metadata.json"
        [ -f "$metadata_file" ] || echo "{}" > "$metadata_file"

        echo "Checking out repo: $git_repo"

        tmp_dir=$(mktemp -d)

        # Checkout latest files into temp dir
        GIT_DIR="$git_repo" git --work-tree="$tmp_dir" checkout -f

        # Iterate over checked out files
        find "$tmp_dir" -type f | while read -r file; do
            rel_path="${file#$tmp_dir/}"
            file_hash=$(md5sum "$file" | awk '{print $1}')

            # Sanitize filename
            base_name=$(basename "$rel_path")
            sanitized_name=$(echo "$base_name" | sed 's/[^A-Za-z0-9._]/ /g')
            dest_path="$target_dir/$sanitized_name"

            # Skip duplicates
            if jq -e --arg h "$file_hash" 'to_entries[] | select(.value == $h)' "$metadata_file" > /dev/null; then
                echo "Skipping duplicate: $rel_path"
                continue
            fi

            # Handle filename collisions
            count=1
            while [ -e "$dest_path" ]; do
                name_no_ext="${sanitized_name%.*}"
                ext="${sanitized_name##*.}"
                [ "$sanitized_name" = "$name_no_ext" ] && ext=""
                new_name="${name_no_ext}($count)"
                [ -n "$ext" ] && new_name="$new_name.$ext"
                dest_path="$target_dir/$new_name"
                count=$((count + 1))
            done

            echo "Adding file: $dest_path"
            cp "$file" "$dest_path"

            # Update metadata.json
            jq --arg k "$(basename "$dest_path")" --arg v "$file_hash" '. + {($k): $v}' "$metadata_file" > "$metadata_file.tmp" && mv "$metadata_file.tmp" "$metadata_file"
        done

        rm -rf "$tmp_dir"
    done
done

rm -rf CHECKOUT/CHECKOUT
```

### Example:

If you archived the user `MainScripts352`:

```bash
cd /storage/emulated/0/gith/MainScripts352
bash checkout.sh  # (Assuming you saved the script as checkout.sh)
```

A folder called `CHECKOUT` will be created, and inside it you’ll find each repository in a readable format.

---

## Coming Soon

Checkout functionality will be built into `gith-dl` in a future update — for now, it must be done manually using the script above.
