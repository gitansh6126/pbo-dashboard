#!/usr/bin/env bash
# deploy_gh_pages.sh — deploy PBO dashboard to GitHub Pages
# Usage: ./deploy_gh_pages.sh <github-username> <repo-name>
# Requires: git, gh CLI authenticated (gh auth login)

set -euo pipefail

USER="${1:-}"
REPO="${2:-}"
if [[ -z "$USER" || -z "$REPO" ]]; then
  echo "Usage: $0 <github-username> <repo-name>"
  echo "Example: $0 gitansh6126 pbo-dashboard"
  exit 1
fi

ROOT="/home/ubuntu/ceo-system"
EXPORT="$ROOT/web-export"
TMP=$(mktemp -d)
BRANCH="gh-pages"

echo "=== PBO → GitHub Pages deploy ==="
echo "User: $USER"
echo "Repo: $REPO"
echo "Branch: $BRANCH"

# 1. Ensure export is fresh
echo "→ Regenerating data.json from brain..."
cd "$ROOT"
python3 -c "
import sys; sys.path.insert(0, 'src')
from pbo.core import Brain
from pbo.reports import full_report
import json, datetime
b = Brain('scratch-brain')
r = full_report(b)
ents = {}
for rec in b.list():
    k = f\"{rec['_module']}.{rec['_type']}\"
    ents.setdefault(k, []).append(rec)
with open('web-export/data.json', 'w') as f:
    json.dump({'report': r, 'entities': ents, 'generated': str(datetime.date.today())}, f, indent=2, default=str)
print('  data.json updated')
"

# 2. Prepare clean deploy dir
echo "→ Copying export to temp dir..."
cp -r "$EXPORT"/* "$TMP/"

# 3. Init git in temp dir and push to gh-pages
echo "→ Pushing to $USER/$REPO:$BRANCH..."
cd "$TMP"
git init -q
git config user.name "GitHub Actions"
git config user.email "actions@github.com"
git checkout -b "$BRANCH" -q
git add -A
git commit -m "Deploy PBO dashboard $(date -u +'%Y-%m-%d %H:%M UTC')" -q

# Use gh CLI if available, else fallback to git push with token
if command -v gh >/dev/null 2>&1; then
  gh repo deploy "$USER/$REPO" --branch "$BRANCH" --source . --message "Deploy $(date -u +'%Y-%m-%d %H:%M UTC')"
else
  echo "gh CLI not found. Push manually:"
  echo "  cd $TMP"
  echo "  git remote add origin https://github.com/$USER/$REPO.git"
  echo "  git push -f origin $BRANCH"
  echo ""
  echo "Then enable Pages in repo Settings → Pages → Source: gh-pages branch"
fi

echo ""
echo "✅ Done. Your dashboard will be at:"
echo "   https://$USER.github.io/$REPO/"
echo ""
echo "To auto-refresh data, run the python regen step before each deploy,"
echo "or set up a GitHub Action that runs the seed+export on a schedule."