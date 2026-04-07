# Quake-GANT Orchestrator

Quake-GANT is an AVX-512 optimized QuakeWorld Server running the MVDSV Engine and KTX Matchless mechanics seamlessly out of the box, controlled via a dynamic Web UI.

## Quick Installation

Deploy the Quake-GANT server instantaneously by binding your legally obtained `id1` directory (`pak0.pak` and `pak1.pak`), and dynamically injecting your secure password.

```bash
docker run -d \
  --name quake-gant \
  -p 27500:27500/udp \
  -p 8500:8000/tcp \
  -e ADMIN_PASSWORD="your-strong-password" \
  -v /path/to/your/legal/id1:/quake/id1:ro \
  normanjames/quake-gant:latest
```

### Architecture Tags
The pipeline dynamically compiles two variants depending on your hardware limits:
- **`latest`**: Generic configuration optimized for standard environments and mainstream computing.
- **`avx512-latest`**: Brutally optimized native architecture meant explicitly for modern hardware (like Intel Xeon Scalable processors) wielding AVX-512 instruction layers.

## Security & Volumes
- **`ADMIN_PASSWORD`**: Effectively required. By injecting this environment variable, you lock down the internal Web API port running on `8000/tcp` and natively protect your raw engine RCON layers from exploits.
- **`id1` Volume**: Mandatory mapping so the Quake engine can execute geometry boundaries. Keep it mapped `:ro` (Read-Only) to mathematically isolate your assets from the dynamic container memory block.

## Access the Control Dashboard
Navigate your web browser to `http://<your-server-ip>:8500/` and login with:
- **Username:** `admin`
- **Password:** `<The ADMIN_PASSWORD string you executed>`

Full source code, architectural boundaries, and orchestration parameters are available strictly on [GitHub](https://github.com/normanheckscher/quake-gant).
