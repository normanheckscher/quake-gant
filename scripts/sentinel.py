import os
import sys

def colored(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

RED = "31;1"
GREEN = "32;1"
YELLOW = "33;1"

def fail(message):
    print(colored(f"[FATAL ERROR] {message}", RED))
    sys.exit(1)

def ok(message):
    print(colored(f"[OK] {message}", GREEN))

def scan_sh_files():
    print(colored("\n==> Scanning for invalid Bash Scripts (.sh) out of bounds...", YELLOW))
    # Ignore nested third-party submodules or build trees where upstream might have .sh files via CMake
    ignore_dirs = {".git", "mvdsv", "ktx", "ezquake", "build-standard", "build-avx512", "qw"}
    
    found_sh = []
    for root, dirs, files in os.walk("."):
        # Prune ignores
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(".sh"):
                # Whitelist curated pipeline deployment scripts exclusively located in the /scripts matrix
                if root.startswith("./scripts") or root.startswith("scripts"):
                    continue
                found_sh.append(os.path.join(root, file))
                
    if found_sh:
        fail(f"OS Guardrail Breached! Found .sh files in orchestrator bounds: {found_sh}. Native Windows PowerShell handles local execution via .cmd/.ps1.")
    else:
        ok("No .sh artifacts discovered in wrapper core.")

def scan_ci_strategy():
    print(colored("\n==> Verifying CI/CD Submodule Fetch Strategy...", YELLOW))
    gitlab_path = ".gitlab-ci.yml"
    if not os.path.exists(gitlab_path):
        fail("Missing .gitlab-ci.yml")
        
    with open(gitlab_path, 'r') as f:
        content = f.read()
        
    if "GIT_SUBMODULE_STRATEGY: none" not in content:
        fail("GitLab Runner Submodule Fetching is NOT disabled! Do not execute recursive fetches to prevent massive client-sided ezQuake bloat. Ensure 'GIT_SUBMODULE_STRATEGY: none' is set in compile-quake variables.")
    else:
        ok("Sovereign CI Submodule fetching is safely constrained.")

def scan_gitmodules_sota():
    print(colored("\n==> Enforcing SOTA Upstream Origins...", YELLOW))
    gitmodules_path = ".gitmodules"
    if not os.path.exists(gitmodules_path):
        fail("Missing .gitmodules")
        
    with open(gitmodules_path, 'r') as f:
        content = f.read()

    # The actual implementation points to official sources natively.
    # Check if a developer accidentally mapped a standard submodule path to a personal fork.
    if "normanheckscher" in content:
        fail("SOTA Breach: Detected 'normanheckscher' branch static fork inside .gitmodules. The orchestrator must track official QW-Group upstream sources dynamically for pure SOTA tracking!")
    else:
        ok("Architecture is currently tracking true SOTA upstream repositories.")

if __name__ == "__main__":
    # Natively align execution directory to the organic absolute repository root structure
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(colored("=== QUAKE-GANT ARCHITECTURAL SENTINEL ===", "36;1"))
    scan_sh_files()
    scan_ci_strategy()
    scan_gitmodules_sota()
    print(colored("\nAll Sentinel Integrity Checks Passed. Proceeding...", GREEN))
    sys.exit(0)
