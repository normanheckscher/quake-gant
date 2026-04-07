# Quake GANT Server ⚔️

**Quake GANT** is a sovereign, AVX-512 optimized, "plug-and-play" QuakeWorld Server environment designed to push the boundaries of 1996 idTech engine performance on modern server hardware. 

This repository heavily refactors and modernizes the renowned **MVDSV** (Multi-View Demo Server) engine with native C vector optimisations, bundles the **KTX** (Kombat Teams eXtreme) framework directly, fully integrates **Frogbot AI**, and orchestrates it all using a modern **Python FastAPI Web Control Panel**—packaged immaculately inside an actively maintained Docker container.

---

## ⚡ The Technology Stack

* **Hardware Affinity:** The core `mvdsv` C-binary is heavily compiled with GCC 12 using explicit `-march=skylake-avx512 -O3 -mstackrealign` alignments, natively utilizing modern 64-byte vector boundaries to maximize calculation density within idSoftware's legacy Quake Virtual Machine arrays.
* **Physics Stability:** Advanced compiler flags actively enforce `-fno-strict-aliasing` limits, completely preventing `-O3` vectorizations from breaking Quake's legacy mathematical type-punning (e.g. `VectorNormalizeFast`).
* **Zero-Setup KTX Bots:** Pre-compiled standard KTX logic arrays and native `.bot` pathing waypoints are injected directly into the active memory layer.
* **Web C2 Front-End:** Out of the box, `supervisord` concurrently launches a dynamic FastAPI/Uvicorn Python web backend hosting a gorgeous glassmorphism Control API. This dashboard actively taps into the Quake engine via **raw, asynchronous UDP Network Polling** to render live sub-server statistics, while seamlessly offering one-click clipboard integrations to port seamlessly from browser to game client.
* **Automagical Nightly Pipeline:** The GitLab CI is configured to synchronize upstream submodule changes automatically directly before compilation (ideal for 03:00 scheduled testing pipelines). It autonomously compiles the bleeding-edge `mvdsv` and KTX binaries using AVX-512 constraints, pushing unified payloads out via SSH and releasing assets to DockerHub/GitHub on demand.

---

## 🚀 Quick Start / Deployment

Because KTX and the Web API are automatically orchestrated inside the single container runtime, your only actual prerequisite is providing your legally owned copy of the Quake `id1` directory (`pak0.pak` and `pak1.pak`). 

### 1. Configuration (Environment Variables)
Before deploying, duplicate the included blueprint to isolate your security:
```bash
cp .env.example .env
```
Inside `.env`, define `ADMIN_PASSWORD` to secure your web orchestrator natively.

### 2. Zero-Friction Map Syncing
We firmly believe in a near-zero installation experience. Instead of forcing you to hunt down modern community `.bsp` files to support the 77 natively-included Frogbot AI waypoints, we have completely abstracted the map acquisition process for you!

Simply run `scripts/Sync-BotMaps.ps1` (Windows) or `./scripts/sync_bot_maps.sh` (Linux). The orchestrator will safely and automatically pull all 77 automated Frogbot maps from standard repositories, extract the exact `.bsp` payloads directly into your host `qw/maps` folder, and instantly clean up the transient files!

### 3. The Magic Docker Pull
Deploying the complete environment seamlessly integrates your `.env` lock:

```bash
docker run -d \
  --name quake-gant \
  --env-file .env \
  -p 27500:27500/udp \
  -p 8500:8000/tcp \
  -v /path/to/your/legal/id1:/quake/id1:ro \
  normanjames/quake-gant:latest
```

*Note: The `:ro` parameter keeps your `id1` files strictly Read-Only to prevent accidental network corruption.*

#### Architecture Tags
Our pipeline supports dual tags natively for performance:
- Pull `:latest` for standard generic hardware.
- Pull `:avx512-latest` if your host natively wields CPU AVX-512 instruction sets for optimal latency.

### 4. Accessing the Web Dashboard
Navigate to `http://<your-server-ip>:8500/` in any modern web browser to access the dynamic Antigravity Command & Control overview, allowing live server stat digestion and bot control logic.

### 5. Integrated Bot Spawning
In Quake, connect to your server (`connect 127.0.0.1`), open your console (`~`), and run:
* `/botcmd enable`
* `/botcmd addbot`
* `/ready`

Frogbot Artificial Intelligence will dynamically analyze the internal `.bot` waypoints and initialize inside your match!

---

## 🛠️ Modifying the Docker Environment (Developers)

If you are developing locally or customizing the Web API modules, this repository operates using standard Dockerfile methodologies.

### Compile the Codebase
Make sure you have CMake 3.22+ and GCC installed:
```bash
# Generate Build Output
mkdir build-mvdsv && cd build-mvdsv
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-march=skylake-avx512 -O3 -fno-strict-aliasing" ../mvdsv
make -j$(nproc)
```

### Extending Server Logic (`server.cfg`)
Simply map a local `server.cfg` over the internal Docker configuration to overwrite match logic:
```bash
-v /my/custom/config/server.cfg:/quake/qw/server.cfg:ro
```

## 🌐 GitLab CI/CD Pipeline Configuration

This repository utilizes a highly optimized GitLab CI wrapper to dynamically compile custom AVX-512 engine states. It is explicitly structured to act as a **Scheduled Pipeline in GitLab (e.g., triggering automatically at 03:00 every night)**, guaranteeing your test server seamlessly floats atop the most bleeding-edge upstream QuakeWorld engine changes without requiring manual, incremental repository commits.

To enable the automated remote server deployment phase (`deploy-to-remote`) on your own hardware, you must define the following **CI/CD Variables** in your repository's settings (`Settings > CI/CD > Variables`):

* `BUILDER_REGISTRY`: Absolute path to your testing node cache (e.g., `10.0.0.61:5050`) ensuring the orchestrator avoids public IPs breaking native submodules!
* `ADMIN_PASSWORD`: A secure string the pipeline organically injects into the remote deployment node to harden your raw RCON.
* `DEPLOY_HOST`: The IPv4 or Hostname of your remote deployment server (e.g., `10.0.0.61`).
* `DEPLOY_USER`: The SSH authorized linux user on the host (e.g., `ubuntu` or `norman`).
* `DEPLOY_PATH`: The absolute host directory path where the pipeline will transfer and build the orchestrator (e.g., `/opt/quake-server`).
* `SSH_PRIVATE_KEY`: Your Private ED25519 or RSA Key formatted for GitLab runners to authenticate into `DEPLOY_HOST` without a password.

*If you simply want to build DockerHub images without deploying via SSH, leave these variables blank. The pipeline natively evaluates a strict `rules: if:` barrier and will intelligently drop the deployment stage to prevent Pipeline failures.*
