#!/usr/bin/env bash
# Organically pulls the comprehensive 77 natively supported Frogbot map list for Linux deployments.
set -e

MAPS=(
    "2towers" "aerowalk" "amphi2" "anarena" "anarena10" "anarena2" "anarena3" "anarena4" "anarena5" "anarena6" "anarena7" "anarena8" "anarena9" "anwalked_test" "arenazap" "aztek" "bravado" "catalyst" "cmt1b" "cmt3" "cmt4" "defer" "dm2dmm4" "dm3" "dm3hill" "dm4" "dm6" "dmm4_1" "dmm4_3" "e1m2" "endif" "forsaken" "frobodm2" "katt" "marena2" "marena3" "metron" "monsoon" "nacmidair" "noentry" "obsidian" "oldcrat" "outpost" "phantombase" "pkeg1" "pocket" "povdmm4" "povdmm4b" "ptucket" "pushdmm4" "q1q3monsoon#td" "qobblestone" "qube" "rarena3" "ravageqwb8" "rocka" "sabbath" "schloss" "shifter" "skull" "spinev2" "steam" "stroggopolis" "stronghold" "subterfuge" "ukooldm2" "ukooldm3" "ukooldm6" "ukooldm8" "ukpak2" "ultrav" "ztndm1" "ztndm2" "ztndm3" "ztndm4" "ztndm5" "ztndm6"
)

BOT_MAPS_URL="https://maps.quakeworld.nu/all"
ROOT_PATH=$(cd "$(dirname "$0")/.." && pwd)
MAPS_DIR="$ROOT_PATH/qw/maps"
TEMP_DIR="$ROOT_PATH/tmp"

mkdir -p "$MAPS_DIR"
mkdir -p "$TEMP_DIR"

echo -e "\033[0;36mInitiating Automated QuakeWorld Map Orchestrator on Linux deployment...\033[0m"

for MAP in "${MAPS[@]}"; do
    MAP_BSP="${MAP}.bsp"
    MAP_ZIP="${MAP}.zip"
    
    if [ -f "$MAPS_DIR/$MAP_BSP" ]; then
        echo -e "\033[0;33m [~] $MAP_BSP safely cached locally. Skipping layer download.\033[0m"
        continue
    fi

    DOWNLOAD_TARGET="$BOT_MAPS_URL/$MAP_ZIP"
    TEMP_ZIP_FILE="$TEMP_DIR/$MAP_ZIP"

    echo -e "\033[0;36m [+] Pulling $MAP_ZIP structure natively...\033[0m"
    if curl -s -f -L -o "$TEMP_ZIP_FILE" "$DOWNLOAD_TARGET"; then
        echo "     => Extracting *.bsp payload..."
        unzip -q -o "$TEMP_ZIP_FILE" "*.bsp" -d "$TEMP_DIR" >/dev/null 2>&1 || true
        
        # Sequentially map binaries to the final host structure natively
        find "$TEMP_DIR" -maxdepth 1 -name "*.bsp" -exec mv -f {} "$MAPS_DIR/" \; >/dev/null 2>&1 || true
        
        echo -e "\033[0;32m     => Successfully secured $MAP_BSP!\033[0m"
    else
        echo -e "\033[0;31m [!] Pipeline failed to download or extract $MAP_ZIP organically (Likely a proprietary id1 map or 404). Skipping.\033[0m"
    fi

    rm -f "$TEMP_ZIP_FILE"
done

# Hygienically delete absolute temporary artifacts instantly
rm -rf "$TEMP_DIR"

echo ""
echo "================================================="
echo -e "\033[0;32mFramework successfully synchronized natively inside $MAPS_DIR.\033[0m"
echo -e "\033[0;35mSECURITY REMINDER: Ensure commercial 'id1/pak0.pak' is legally mapped to your host!\033[0m"
echo "================================================="
