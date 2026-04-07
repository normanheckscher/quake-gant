<#
.SYNOPSIS
    Downloads standard Frogbot-supported map packages natively from maps.quakeworld.nu
    and extracts the underlying BSP binaries correctly into /qw/maps/.
#>

$Maps = @(
    "2towers", "aerowalk", "amphi2", "anarena", "anarena10", "anarena2", "anarena3", "anarena4",
    "anarena5", "anarena6", "anarena7", "anarena8", "anarena9", "anwalked_test", "arenazap",
    "aztek", "bravado", "catalyst", "cmt1b", "cmt3", "cmt4", "defer", "dm2dmm4", "dm3",
    "dm3hill", "dm4", "dm6", "dmm4_1", "dmm4_3", "e1m2", "endif", "forsaken", "frobodm2",
    "katt", "marena2", "marena3", "metron", "monsoon", "nacmidair", "noentry", "obsidian",
    "oldcrat", "outpost", "phantombase", "pkeg1", "pocket", "povdmm4", "povdmm4b", "ptucket",
    "pushdmm4", "q1q3monsoon#td", "qobblestone", "qube", "rarena3", "ravageqwb8", "rocka",
    "sabbath", "schloss", "shifter", "skull", "spinev2", "steam", "stroggopolis", "stronghold",
    "subterfuge", "ukooldm2", "ukooldm3", "ukooldm6", "ukooldm8", "ukpak2", "ultrav", "ztndm1",
    "ztndm2", "ztndm3", "ztndm4", "ztndm5", "ztndm6"
)

$BotMapsUrl = "https://maps.quakeworld.nu/all"

# Organically map directories natively using the script origin as our anchor
$RootPath = (Resolve-Path "$PSScriptRoot\..").Path
$MapsDir = Join-Path $RootPath "qw\maps"
$TempDir = Join-Path $RootPath "tmp"

if (-Not (Test-Path $MapsDir)) {
    New-Item -ItemType Directory -Path $MapsDir | Out-Null
    Write-Host "[+] Generated mandatory container mapping directory: $MapsDir" -ForegroundColor Green
}
if (-Not (Test-Path $TempDir)) {
    New-Item -ItemType Directory -Path $TempDir | Out-Null
}

Write-Host "Initiating Automated QuakeWorld Map Orchestrator natively mapping 77 Bot routes..." -ForegroundColor Cyan

foreach ($Map in $Maps) {
    $MapZip = "$Map.zip"
    $MapBsp = "$Map.bsp"

    # If the map BSP natively exists, bypass iteration dynamically
    if (Test-Path (Join-Path $MapsDir $MapBsp)) {
        Write-Host " [~] $MapBsp safely cached locally. Skipping layer download." -ForegroundColor Yellow
        continue
    }

    $DownloadTarget = "$BotMapsUrl/$MapZip"
    $TempZipFile = Join-Path $TempDir $MapZip

    try {
        Write-Host " [+] Pulling $MapZip structure natively..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $DownloadTarget -OutFile $TempZipFile -UseBasicParsing -ErrorAction Stop

        Write-Host "     => Extracting *.bsp payload..."
        Expand-Archive -Path $TempZipFile -DestinationPath $TempDir -Force

        # Move solely the bsp natively to `/qw/maps`, ignoring txt readmes structurally
        Get-ChildItem -Path $TempDir -Filter "*.bsp" | ForEach-Object {
            Move-Item -Path $_.FullName -Destination $MapsDir -Force
        }
        
        Write-Host "     => Successfully secured $MapBsp!" -ForegroundColor Green

    } catch {
        Write-Host " [!] Pipeline failed to download or extract $MapZip organically (Likely proprietary id1 map or 404). Skipping." -ForegroundColor Red
    } finally {
        # Strict garbage collection rule handling temporary files natively
        if (Test-Path $TempZipFile) { Remove-Item $TempZipFile -Force -ErrorAction SilentlyContinue }
    }
}

# Discard dirty extraction ghosts entirely per architectural hygiene guidelines
Get-ChildItem -Path $TempDir | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host " "
Write-Host "================================================="
Write-Host "Framework successfully synchronized natively inside $MapsDir." -ForegroundColor Green
Write-Host "SECURITY REMINDER: Ensure commercial 'id1/pak0.pak' is legally mapped to your host!" -ForegroundColor Magenta
Write-Host "================================================="
