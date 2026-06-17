#!/usr/bin/env bash
# Push app hg_food_safety len GitHub. Chay tai thu muc app (chua pyproject.toml).
set -e
REPO="https://github.com/mrhuychien/iso.git"
BRANCH="${1:-main}"

git init -b "$BRANCH" 2>/dev/null || git init
git add -A
git commit -m "feat: hg_food_safety - app ATTP ISO 22000 tren ERPNext v16 (kieu NPP)" || echo "Khong co thay doi de commit"
git branch -M "$BRANCH"
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO"

echo ">> Day code len $REPO ($BRANCH):"
echo "   git push -u origin $BRANCH"
echo "   (neu repo da co commit: them --force lan dau, hoac 'git pull --rebase origin $BRANCH' truoc)"
