#!/usr/bin/env bash
# Safely pulls the absolute latest master branch commits from upstream engines natively for Linux.

set -e

echo -e "\033[0;36m==> Resolving latest upstream tracking boundaries recursively...\033[0m"
git submodule update --remote --merge

echo ""
echo -e "\033[0;36m==> Active Traversal Status:\033[0m"
git status -s

echo ""
echo -e "\033[0;32m==> SOTA Modules locally aligned.\033[0m"
echo -e "\033[0;33mIf you are satisfied with this delta, mechanically lock them via:\033[0m"
echo "  git add mvdsv ktx ezquake"
echo '  git commit -m "chore: synchronize upstream submodules to latest master tracking branch"'
echo "  git push"
echo ""
