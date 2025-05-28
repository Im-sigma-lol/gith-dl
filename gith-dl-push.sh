#!/bin/bash

# Ensure you're logged into GitHub
if ! gh auth status &>/dev/null; then
    echo "❌ Please run 'gh auth login' first."
    exit 1
fi

ROOT_DIR="$(pwd)"
GITHUB_USERNAME=$(gh api user --jq .login)

# Configure git to use gh token for HTTPS
git config --global credential.helper "$(gh auth git-credential)"

# Find all folders ending in .git (bare repos)
find . -type d -name "*.git" | while read -r BARE_REPO; do
    ACCOUNT_NAME=$(basename "$(dirname "$BARE_REPO")")
    REPO_NAME=$(basename "$BARE_REPO" .git)
    FINAL_REPO_NAME="Reuploaded-from-${ACCOUNT_NAME}---${REPO_NAME}"

    echo "📦 Processing $ACCOUNT_NAME/$REPO_NAME → $FINAL_REPO_NAME"

    # Temp clone of bare repo
    TEMP_DIR=$(mktemp -d)
    git clone --bare "$BARE_REPO" "$TEMP_DIR/$REPO_NAME" &>/dev/null
    cd "$TEMP_DIR/$REPO_NAME" || continue

    # Create repo on GitHub if it doesn't exist
    if gh repo view "$GITHUB_USERNAME/$FINAL_REPO_NAME" &>/dev/null; then
        echo "⚠️  Repo already exists: $FINAL_REPO_NAME"
    else
        gh repo create "$FINAL_REPO_NAME" --private -y &>/dev/null
        echo "✅ Created: https://github.com/$GITHUB_USERNAME/$FINAL_REPO_NAME"
    fi

    # Push with gh-authenticated git
    git push --mirror "https://github.com/$GITHUB_USERNAME/$FINAL_REPO_NAME.git" &>/dev/null
    echo "🚀 Pushed to GitHub"

    # Cleanup
    cd "$ROOT_DIR"
    rm -rf "$TEMP_DIR"
done
