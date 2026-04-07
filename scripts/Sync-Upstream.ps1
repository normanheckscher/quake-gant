<#
.SYNOPSIS
    Safely synchronizes the absolute latest master branch commits from 
    upstream native repositories organically into your local wrapper index.
#>

Write-Host "==> Resolving latest upstream tracking boundaries recursively..." -ForegroundColor Cyan
git submodule update --remote --merge

Write-Host "`n==> Active Traversal Status:" -ForegroundColor Cyan
git status -s

Write-Host "`n==> SOTA Modules locally aligned." -ForegroundColor Green
Write-Host "If you are satisfied with this delta, mechanically lock them via:" -ForegroundColor Yellow
Write-Host "  git add mvdsv ktx ezquake"
Write-Host "  git commit -m ""chore: synchronize upstream submodules to latest master tracking branch"""
Write-Host "  git push`n"
