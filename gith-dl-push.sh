#!/bin/bash

# Ensure you're logged into GitHub
gh auth status > /dev/null 2>&1 || {
    echo "❌ Please run 'gh auth login' first."
    exit 1
}

ROOT_DIR="$(pwd)"

# Find all folders ending in .git (bare repos)
find . -type d -name "*.git" | while read -r BARE_REPO; do
    # Get parent folder name as account
    ACCOUNT_NAME=$(basename "$(dirname "$BARE_REPO")")
    REPO_NAME=$(basename "$BARE_REPO" .git)
    FINAL_REPO_NAME="Reuploaded-from-${ACCOUNT_NAME}---${REPO_NAME}"

    echo "📦 Processing $ACCOUNT_NAME/$REPO_NAME → $FINAL_REPO_NAME"

    # Create temp clone from bare repo
    TEMP_DIR=$(mktemp -d)
    git clone --bare "$BARE_REPO" "$TEMP_DIR/$REPO_NAME" > /dev/null 2>&1
    cd "$TEMP_DIR/$REPO_NAME" || continue

    # Create repo on your GitHub
    if gh repo view "$FINAL_REPO_NAME" > /dev/null 2>&1; then
        echo "⚠️ Repo already exists: $FINAL_REPO_NAME"
    else
        gh repo create "$FINAL_REPO_NAME" --private --confirm > /dev/null
        echo "✅ Created: https://github.com/$(gh api user --jq .login)/$FINAL_REPO_NAME"
    fi

    # Push to GitHub
    git push --mirror "https://github.com/$(gh api user --jq .login)/$FINAL_REPO_NAME.git" > /dev/null
    echo "🚀 Pushed to GitHub"

    cd "$ROOT_DIR"
    rm -rf "$TEMP_DIR"
done
