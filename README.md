
# GitHub Account Archiver Setup Guide

## Installation

```bash
REPO_URL="https://github.com/Im-sigma-lol/gith-dl"
INSTALL_BIN="/data/data/com.termux/files/usr/bin/gith-dl"
[ -f "$INSTALL_BIN" ] || { TEMP=$(mktemp -d) && git clone "$REPO_URL" "$TEMP" && cd "$TEMP" && bash install.sh && cd - && rm -rf "$TEMP"; }
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

for dir in *.git; do
    if [ -d "$dir" ]; then
        repo_name="${dir%.git}"
        target_dir="CHECKOUT/$repo_name"

        echo "Checking out bare repo $dir to $target_dir"

        mkdir -p "$target_dir"
        GIT_DIR="$dir" git --work-tree="$target_dir" checkout -f
    fi
done
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
