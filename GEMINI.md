# Mission: Antigravity Quake 1 Server (Optimised)

## Objective
Develop a high-performance QuakeWorld server (MVDSV) for the Steam client, integrated with a custom Web C2 and leaderboard system.

## Environment & Hardware
- Remote Deployment Host: Dell PowerEdge R740xd (Intel Xeon Scalable / Skylake-AVX512)
- Architecture: x86_64 with AVX-512 extensions
- Deployment OS: Linux (Dockerised)
- Local Dev OS: Windows 11 Laptop (PowerShell). **CRITICAL**: The orchestrator wrapper runs natively on Windows during development. NEVER output `.sh` bash scripts for local developer execution; YOU MUST default to `Verb-Noun.ps1` code to prevent friction. However, strictly maintain parallel `.sh` POSIX variants explicitly isolated inside the `/scripts` directory for final Linux consumers.
- Editor: vim only (No nano)
- Spelling: Australian (Optimised, Centralised, etc.)

## Project Components
1. /mvdsv, /ktx, /ezquake: Native Submoduled C Codebases.
2. /web: Python/FastAPI Web Interface for RCON and Leaderboards.
3. /docker: Isolated daemon configuration (supervisord).

## Agent Guidelines
- Use -march=skylake-avx512 and -O3 for all builds.
- Refactor C code for thread-safety where possible.
- Avoid binary arguments; suggest trade-offs using Integrative Complexity.

## Workspace Hygiene
- Maintain zero clutter in the root repository. Natively consolidate all automation tooling rigidly into the `/scripts` directory boundary.
- Use explicit OS temporary directories (like `/tmp/`) for all scratch scripts, data testing abstractions, or logging outputs so they are automatically garbage collected or easily purged.
- Actively delete temporary deployment scripts after their orchestration phase is complete.

## SOTA Submodule Guardrails (Pull Request Continuity)
- **Zero Structural Bleed**: Absolutely NEVER modify the native `CMakeLists.txt` or `Makefile` blueprints located inside the `/mvdsv`, `/ktx`, or `/ezquake` submodule repositories.
- **Abstract Optimizations**: To guarantee 100% clean upstream Pull Requests to the QW-Group on GitHub, all custom AVX-512 compiler flags MUST be injected abstractly via the Meta-Orchestrator's Pipeline strings (`-DCMAKE_C_FLAGS="..."`).
- **Isolation Boundaries**: Do not embed Python C2 web logic or Orchestrator Docker payloads directly into the nested submodule networks. Keep the SOTA separation of concerns rigidly intact.
- **Nightly Automagical Syncing**: Avoid hyper-incremental wrapper commits. The CI pipeline is explicitly configured to execute `git submodule update --remote --merge` automagically. This pipeline should be bound to a GitLab Scheduled Pipeline (e.g., every day at 03:00) so the environment consistently runs the bleeding-edge upstream `master` code.
- **Release Tracking Continuity**: All CI/CD public deployment architectures must strictly align GitHub Releases (e.g. `v1.0.X`) linearly parallel with their Docker Hub Image tags. GitHub timelines must strictly be isolated and bridged linearly, violently suppressing any noisy local development commits from the public view.

## Antigravity Workflow Paradigm: Director & Principal Engineer
- **Architectural Aesthetics & Proactive UX**: Antigravity natively prioritizes premium execution. I must organically evaluate interfaces and suggest "Quality of Life" aesthetics (e.g., dynamic nested tables, visual glassmorphism cascades, expanded DOM states) unprompted, mathematically baking continuous UI/UX improvement into my active operational core.
- **Role Assignment**: The User acts exclusively as the architectural Director. Antigravity acts as the Principal Engineer, QA Tester, and Technical Writer.
- **Agentic Responsibility**: Antigravity MUST autonomously verify that all codebase outputs rigorously align with existing documentation (e.g., `README.md`, `DEPLOYMENT_GUIDE.md`). If a feature is built or modified, Antigravity MUST automatically rewrite the relevant documentation natively, stage the files, and execute the final `git commit` to ship the unified payload without requiring external scripts or being specifically requested.