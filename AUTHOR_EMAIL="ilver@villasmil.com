#!/bin/bash
# Lightweight deployment helper (draft-friendly PRs)
set -e

REPO_OWNER="YOUR_GITHUB_USERNAME"   # <-- update
REPO_NAME="villasmil-omega-protocol"
AUTHOR_NAME="Ilver Villasmil"
AUTHOR_EMAIL="ilver@villasmil.com"  # <-- update

git config user.name "$AUTHOR_NAME"
git config user.email "$AUTHOR_EMAIL"

# Create branches
git checkout -B feature/test-harness
git add villasmil_omega tests requirements.txt
git commit -m "Add core prototype and tests" || true
git push -u origin feature/test-harness

git checkout main
git checkout -B feature/docs-full
git add docs protocol README.md LICENSE
git commit -m "Add architecture docs and schemas" || true
git push -u origin feature/docs-full

echo "Branches pushed: feature/test-harness, feature/docs-full"
echo "Create PRs via GitHub UI or 'gh pr create' if you have gh installed."
