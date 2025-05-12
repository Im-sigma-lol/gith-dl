
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

mkdir -p CHECKOUT

for account_dir in */; do
    [ -d "$account_dir" ] || continue
    account_name="${account_dir%/}"

    echo "Processing account: $account_name"

    output_dir="CHECKOUT/$account_name"
    mkdir -p "$output_dir"

    for git_dir in "$account_dir"*.git; do
        [ -d "$git_dir" ] || continue

        repo_name="${git_dir##*/}"
        repo_name="${repo_name%.git}"
        temp_checkout="CHECKOUT/tmp_$account_name/$repo_name"

        echo "  Checking out $git_dir to $temp_checkout"
        mkdir -p "$temp_checkout"
        GIT_DIR="$git_dir" git --work-tree="$temp_checkout" checkout -f
    done

    echo "  Flattening into $output_dir"

    find "CHECKOUT/tmp_$account_name" -mindepth 1 -type f -exec bash -c '
        output_dir="$1"
        shift
        for f; do
            name=$(basename "$f")
            base="${name%.*}"
            ext="${name##*.}"
            [ "$base" = "$name" ] && ext=""
            n=1
            dest="$output_dir/$name"
            while [ -e "$dest" ]; do
                dest="$output_dir/${base} ($n)${ext:+.$ext}"
                ((n++))
            done
            mv "$f" "$dest"
        done
    ' _ "$output_dir" {} +

    # Remove the temp checkout folder
    rm -rf "CHECKOUT/tmp_$account_name"

    echo "  Done with $account_name"
done

echo "All done."
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
