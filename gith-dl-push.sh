#!/bin/bash

# Make sure you're logged into GitHub CLI
gh auth status > /dev/null 2>&1 || {
    echo "❌ Please run 'gh auth login' first."
    exit 1
}

# Root directory: current working dir
ROOT_DIR="$(pwd)"

# Find all `.git` folders inside subdirectories
find . -type d -name ".git" | while read -r GITDIR; do
    REPO_PATH=$(dirname "$GITDIR")        # e.g., ./SomeUser/scripts.git
    REPO_NAME=$(basename "$REPO_PATH")    # e.g., scripts.git
    ACCOUNT_DIR=$(basename "$(dirname "$REPO_PATH")")  # e.g., SomeUser

    # Clean up .git suffix for repo creation
    CLEAN_REPO_NAME="${REPO_NAME%.git}"

    echo "📦 Found: $ACCOUNT_DIR/$CLEAN_REPO_NAME"

    # Move .git repo to clean folder if needed
    DEST_FOLDER="$ROOT_DIR/$ACCOUNT_DIR/$CLEAN_REPO_NAME"
    if [[ "$REPO_PATH" == *".git" ]]; then
        mkdir -p "$DEST_FOLDER"
        mv "$REPO_PATH/.git" "$DEST_FOLDER/.git"
        rm -rf "$REPO_PATH"
    fi

    cd "$DEST_FOLDER" || continue

    # Set a remote if none exists
    if ! git remote | grep -q origin; then
        gh_user=$(gh api user --jq .login)
        gh repo create "$gh_user/$CLEAN_REPO_NAME" --private --source=. --push
    else
        echo "🔁 Remote already exists for $CLEAN_REPO_NAME, skipping repo create."
    fi

    cd "$ROOT_DIR" || exit
done
