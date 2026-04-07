# Antigravity Quake: CI/CD & Deployment Guide

This document outlines the Continuous Integration, Continuous Deployment (CI/CD), and infrastructure setup requirements for the Antigravity Quake Orchestrator project. It is designed to ensure strict adherence to our project guardrails (submodule sovereignty and abstraction) while providing a transparent blueprint for deploying this environment on external platforms.

## 0. Critical Pre-Requisite Assets

> [!WARNING]
> **Commercial Asset Hygiene**
> By law, Quake cannot be shipped with id Software's proprietary retail packages. 
> To launch this environment, you MUST natively establish an `id1` folder and place your authentic `pak0.pak` and `pak1.pak` binaries inside it prior to mapping Docker volumes!
>
> **Community Bot Maps**
> KTX heavily maps automated Frogbots running against custom community vectors. Your host `qw/maps` architecture requires pre-caching these elements dynamically. 
> *A native downloader has been completely abstracted for you: Launch `scripts\Sync-BotMaps.ps1` locally inside Windows to automatically pull these vectors securely from `maps.quakeworld.nu` !*

## 1. Core Architecture & Guardrails

The deployment pipeline is built entirely around maintaining **Pull Request Continuity** with the upstream QuakeWorld projects:

- **Zero Structural Bleed**: The `mvdsv`, `ktx`, and `ezquake` Git submodules are dynamically pulled and compiled. Their native `CMakeLists.txt` and `Makefile` blueprints must **never** be manually modified or checked into our wrapper codebase.
- **Abstract Optimizations**: Hardware-specific flags designed for modern servers (e.g., `-march=skylake-avx512`, `-O3`, `-mstackrealign`) are injected fluidly via `.gitlab-ci.yml` pipeline matrices through `-DCMAKE_C_FLAGS`.
- **Environment Hygiene**: All deployment scripts and test publishing workflows strictly enforce `--no-cache` on `docker build` arguments and run `docker system prune -f` during teardown to prevent dirty layers or runtime ghosting during rapid testing iterations. 
- **Isolation Boundaries**: Python C2 web logic (`/web`) runs parallel to the deeply-nested C engines via `supervisord.conf`. Absolutely no integration logic is structurally embedded inside the nested C repository boundaries.
- **Architectural Sentinel**: A native Python agent (`scripts/sentinel.py`) actively executes logic validation at the absolute top of the GitLab pipeline framework prior to compilation, violently refusing pipelines attempting to inject invalid scripting paradigms (like Windows non-compliant `.sh` logic) or corrupting our optimized submodule download matrices (`GIT_SUBMODULE_STRATEGY: none`).

## 2. GitLab CI/CD Variable Setup

To bootstrap this deployment pipeline on a new GitLab instance, navigate to **Settings > CI/CD > Variables** and inject the following securely masked environment variables:

### Remote Deployment Server (Testing/Staging Node)
*   **`BUILDER_REGISTRY`**: The absolute DNS or IPv4 port registry cache mapping (e.g., `10.0.0.61:5050`) explicitly ensuring public Github pushes avoid hardcoded developer IP strings.
*   **`ADMIN_PASSWORD`**: Required. Organically drops standard security locking across your RCON layer via parameter payload injections.
*   **`DEPLOY_HOST`**: The IPv4 or FQDN of the deployment target (e.g., isolated testing server).
*   **`DEPLOY_USER`**: The SSH authorized Linux user. Must have permissions to execute `docker` suite commands.
*   **`DEPLOY_PATH`**: Absolute host directory path where the pipeline will deliver payloads (e.g., `/opt/quake-env`). **Critically**, this path must contain:
    - An `id1` subdirectory pre-populated with commercial Quake assets (`pak0.pak`).
    - A `qw/maps` subdirectory pre-populated with `.bsp` community map variants (like `aerowalk`).
*   **`SSH_PRIVATE_KEY`**: Your ED25519 or RSA Private Key block matching the authorized keys of the `DEPLOY_USER`.

### DockerHub Publisher Integrations
*   **`DOCKERHUB_USERNAME`**: Your repository username (e.g., `normanjames`).
*   **`DOCKERHUB_TOKEN`**: A secure Personal Access Token granting pull/push pipeline accessibility.

### GitHub Release Integrations
*   **`GITHUB_TOKEN`**: A GitHub Personal Access Token mapped with "repo" access. The pipeline uses this to seamlessly mint automated GitHub Releases and push the raw cross-compiled `mvdsv-standard`, `mvdsv-avx512`, and `qwprogs.so` binaries upstream into `normanheckscher/quake-gant`.

## 3. Runner Target Characteristics

The GitLab pipeline expects a native Runner tagged with `avx512`. 
The build stage accelerates compilation using a localized Builder image defined securely by `$BUILDER_REGISTRY/norman/quake-antigravity/quake-builder:latest`. 

*Note: If setting up on an entirely new/isolated network, you must verify your container registry endpoint in `.gitlab-ci.yml` pointing to an image populated with `cmake`, `git`, and build-essential elements (like `Dockerfile.build_env`).*

## 4. Pipeline Execution Lifecycle

1. **`audit` (`audit-architecture`)**: Instantly bootstraps a lightweight container that formally clones the active orchestrator wrapper repository and natively launches the internal `scripts/sentinel.py` guardian algorithm to securely verify all SOTA alignments. It radically severs functionally corrupted commits immediately before any expensive automated compilation matrix triggers!
2. **`build` (`compile-quake`)**: Designed to be bound to a GitLab Scheduled Pipeline (e.g., Nightly builds at 03:00). Efficiently maps exact upstream pointers via `git submodule update --init --recursive --remote --merge mvdsv ktx` to guarantee automated server pipelines explicitly bypass heavy client submodules while acquiring latest `QW-Group` streams. Executes a parallel matrix build dynamically generating an `avx512` payload and a hardware-agnostic standard payload natively mapped structurally to explicitly bound Out-Of-Source CMake caches, securing blazing-fast sub-5-second compilation iterations on code pushed bypassing network limits! Exposes transient `build-<target>` directories as GitLab artifacts.
3. **`deploy` (`deploy-to-remote`)**: Explicitly isolates thick C-objects natively, packing the successful `avx512/mvdsv` binaries alongside `/web` REST logic into a stripped latency-free ~3MB `tar.gz` and efficiently triggers via SCP upload to the test environment. Initializes Docker leveraging the cleanly isolated `$ADMIN_PASSWORD` to shield architecture limits, before smoothly locally mounting a strictly permanent Host-bound `/db` volume mechanically preventing the erasure of the Global SQLite Rankings during extreme CI deployments!
4. **`publish`**:
    - **`publish-runtime-asset`**: (Manual Trigger) Packages a strict static base image module natively embedding the heavy Debian SDKs, Python dependencies, and `nQuake` maps, pushing it strictly securely natively into your internal architectural proxy registry (`$BUILDER_REGISTRY/norman/quake-antigravity/quake-gant-base`). This firmly limits external queries out of the network isolating structural data pipelines entirely locally!
    - **`publish-to-dockerhub`**: (Manual Trigger) Packages a production-standard footprint and pushes unified tags to DockerHub (`latest`, `avx512-latest`). Actively synchronizes the repository `DOCKERHUB.md` securely over the backend REST APIs.
    - **`publish-to-github`**: (Manual Trigger) Leverages a dynamic `rsync` directory bridge over public APIs to perfectly copy codebase deltas structurally into Github, ensuring a pristine linear timeline completely shielded from messy local Git histories! Leverages the robust GitHub API to dynamically bind pre-compiled standard and AVX-512 engines to new tag releases.

### Local Setup / Standalone Testing

To test integration on a local Linux instance without the runner environment:
1. Initialize structure: `git clone --recursive <repository-url-for-normanheckscher>`
2. Execute compiler flags identical to `.gitlab-ci.yml` to generate your `mvdsv` / `ktx` binaries to a `build-standard` directory.
3. Build sandbox: `docker build --no-cache --build-arg TARGET_DIR=build-standard -t quake-sandbox -f Dockerfile.hub .`
4. Copy `.env.example` to `.env` locally ensuring `ADMIN_PASSWORD` is injected safely.
5. Ensure you have the commercial game assets available locally (e.g., at `/path/to/id1` containing your `pak` files).
6. Deploy sandbox container: `docker run -d --env-file .env -v /path/to/id1:/quake/id1:ro -p 27500:27500/udp -p 8500:8000/tcp quake-sandbox`
