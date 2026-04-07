import os
import json
import logging
import asyncio
import aiohttp
import zipfile
import io
import time
import socket
import subprocess
import secrets
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import init_db, get_leaderboard, start_player_session, update_live_session, update_session_match_end

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quake_c2")

app = FastAPI(title="Antigravity Quake C2", version="1.1.0")
security = HTTPBasic()
init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# =====================================================================
# ARCHITECTURAL DESIGN PATTERN: Declarative State Reconciliation
# =====================================================================
# To prevent engine volatility (e.g. Quake Matchless rotations) from 
# polluting Orchestrator logic organically, we cleanly isolate memory.
# 
# active_servers[port] = {
#     "engine_state": {...}, # Ephemeral volatile data fetched natively
#     "target_state": {...}, # Orchestrator enforced baseline configurations
#     "meta": {...}          # Immutable deployment targets
# }
# =====================================================================

DEFAULT_BOT_MAP_QUEUE = "2towers aerowalk amphi2 anarena anarena10 anarena2 anarena3 anarena4 anarena5 anarena6 anarena7 anarena8 anarena9 anwalked_test arenazap aztek bravado catalyst cmt1b cmt3 cmt4 defer dm2dmm4 dm3 dm3hill dm4 dm6 dmm4_1 dmm4_3 e1m2 endif forsaken frobodm2 katt marena2 marena3 metron monsoon nacmidair noentry obsidian oldcrat outpost phantombase pkeg1 pocket povdmm4 povdmm4b ptucket pushdmm4 q1q3monsoon#td qobblestone qube rarena3 ravageqwb8 rocka sabbath schloss shifter skull spinev2 steam stroggopolis stronghold subterfuge ukooldm2 ukooldm3 ukooldm6 ukooldm8 ukpak2 ultrav ztndm1 ztndm2 ztndm3 ztndm4 ztndm5 ztndm6"

active_servers = {
    27500: {
        "meta": {"mod": "ktx", "pid": "SUPERVISORD"},
        "engine_state": {"map": "dm3", "players": "0/16", "roster": []},
        "target_state": {"timelimit": "3", "fraglimit": "8", "bot_skill1": "2", "minplayers": 4, "queue": DEFAULT_BOT_MAP_QUEUE}
    }
}
active_procs = {}
global_delta_tracker = {}

NEXT_PORT = 27501
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    # Standard Username/Password as requested
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "server": {"engine": "MVDSV AVX-512"}})

@app.get("/api/servers")
async def get_servers():
    # Dynamically extract Active Bot Skill Level assigned inside the Quake Engine configuration
    global_bot_skill = "2"
    try:
        with open("/quake/qw/server.cfg", "r") as f:
            for cfg_line in f:
                if "set k_fb_skill " in cfg_line:
                    global_bot_skill = cfg_line.strip().split()[-1]
                    break
    except Exception:
        pass
        
    # Dynamically extract active SQLite Leaderboard ranks natively to match human entities
    current_lb = get_leaderboard()
    lb_ranks = {p["name"]: f"Rank #{idx + 1}" for idx, p in enumerate(current_lb)}
    
    payload_response = {}
    
    for port, srv in active_servers.items():
        # Override global_bot_skill with dynamic runtime orchestrator memory if available
        if "bot_skill1" in srv.get("target_state", {}):
            global_bot_skill = srv["target_state"]["bot_skill1"]
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.5)
            # Fetch Live Leaderboard Match & Rules 
            sock.sendto(b'\xff\xff\xff\xffstatus\n', ("127.0.0.1", port))
            data, _ = sock.recvfrom(4096)
            text = data.decode('utf-8', errors='ignore')
            lines = text.split('\n')
            
            if len(lines) > 0 and 'n\\' in lines[0]:
                info = lines[0]
                
                r_players = []
                for line in lines[1:]:
                    line = line.strip()
                    if not line: continue
                    p_parts = line.split('"')
                    if len(p_parts) >= 2:
                        name = p_parts[1]
                        meta = p_parts[0].strip().split()
                        
                        if len(meta) >= 4: # Standard QW Status: userid frags time ping
                            userid = meta[0]
                            frags = meta[1]
                            time_curr = meta[2]
                            ping = meta[3]
                        else:
                            frags = meta[0] if len(meta) > 0 else "0"
                            ping = meta[1] if len(meta) > 1 else "0"
                        
                        # KTX natively emulates ping ~9 for Frogbots, but universally applies '/ ' or '\\ ' clan prefixes depending on k_fb_prefix
                        is_bot = ("bot" in name.lower() or "frog" in name.lower() or name.startswith("/ ") or name.startswith("\\ "))
                        
                        if is_bot:
                            skill = f"Level {global_bot_skill}"
                        else:
                            skill = lb_ranks.get(name, "Unranked")
                            # Trigger Asynchronous Session Mapping directly into SQLite live tracker!
                            try:
                                current_frags_int = int(frags)
                                
                                if name not in global_delta_tracker:
                                    s_id = f"{name}_{int(time.time())}_{port}"
                                    global_delta_tracker[name] = {"last_frags": current_frags_int, "session_id": s_id}
                                    start_player_session(s_id, name, current_frags_int, len(lines)-1)
                                else:
                                    s_id = global_delta_tracker[name]["session_id"]
                                    delta_frags = current_frags_int - global_delta_tracker[name]["last_frags"]
                                    # 3 seconds injected into Time-In-Game metric seamlessly
                                    if delta_frags > 0:
                                        update_live_session(s_id, delta_frags, 3)
                                    else:
                                        update_live_session(s_id, 0, 3)
                                    global_delta_tracker[name]["last_frags"] = current_frags_int
                                    
                            except Exception:
                                pass
                        
                        r_players.append({
                            "name": name,
                            "frags": frags,
                            "type": "Neural AI" if is_bot else "Human",
                            "skill": skill
                        })
                
                info_parts = info.split('\\')
                f_limit = info_parts[info_parts.index("fraglimit") + 1] if "fraglimit" in info_parts else "0"
                t_limit = info_parts[info_parts.index("timelimit") + 1] if "timelimit" in info_parts else "0"
                
                map_name = srv.get("engine_state", {}).get("map", "dm3")
                max_players = "16"
                if "map" in info_parts:
                    map_name = info_parts[info_parts.index("map") + 1]
                if "maxclients" in info_parts:
                    max_players = info_parts[info_parts.index("maxclients") + 1]
                
                srv.setdefault("engine_state", {})
                srv["engine_state"]["map"] = map_name
                srv["engine_state"]["players"] = f"{len(r_players)}/{max_players}"
                srv["engine_state"]["roster"] = r_players
                srv["engine_state"]["fraglimit"] = f_limit
                srv["engine_state"]["timelimit"] = t_limit
        except Exception:
            pass
            
        # Dynamically compile Flat Payload format so UI array blocks parse cleanly natively
        payload_response[port] = {
            "mod": srv.get("meta", {}).get("mod", "ktx"),
            "pid": srv.get("meta", {}).get("pid", "N/A"),
            **srv.get("engine_state", {}),
            **srv.get("target_state", {})
        }
            
    return payload_response

@app.get("/api/leaderboard")
async def get_stats(timeframe: str = "all_time"):
    return get_leaderboard(timeframe)

@app.get("/debug")
async def debug():
    # Attempt a dry-run of mvdsv to capture why it's silently terminating.
    import subprocess
    cmd = ["/quake/mvdsv", "-port", "27501", "+exec", "server.cfg"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, cwd="/quake", timeout=3)
        return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
    except subprocess.TimeoutExpired as e:
        return {"stdout": e.stdout.decode() if e.stdout else "TIMEOUT: Engine stayed alive for 3 seconds!", "stderr": e.stderr.decode() if e.stderr else ""}
    except Exception as e:
        return {"error": str(e)}

@app.post("/admin/launch-server")
async def launch_server(request: Request, username: str = Depends(authenticate)):
    global NEXT_PORT
    data = await request.json()
    map_name = data.get("map_name", "random")
    mod = data.get("mod", "ktx")
    
    if map_name.lower() == "random":
        import random
        map_name = random.choice(DEFAULT_BOT_MAP_QUEUE.split())
        
    port = NEXT_PORT
    NEXT_PORT += 1
    if NEXT_PORT > 27510:
        NEXT_PORT = 27501 # Reset to start of range
    
    # Spawn Quake Engine inside Docker on new port dynamically
    cmd = ["/quake/mvdsv", "-port", str(port), "+exec", "server.cfg", "+rcon_password", ADMIN_PASSWORD, "+map", map_name]
    logger.info(f"Spawning Sub-Server on Port {port} with Map {map_name} ({mod})")
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd="/quake", 
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL, 
            stderr=asyncio.subprocess.DEVNULL
        )
        import random
        minp_val = random.randint(1, 4)
        skill_val = str(random.randint(1, 3))
        
        active_servers[port] = {
            "meta": {"mod": mod, "pid": proc.pid},
            "engine_state": {
                "map": map_name, 
                "players": "0/16", 
                "roster": []
            },
            "target_state": {
                "timelimit": "3",
                "fraglimit": "8",
                "bot_skill1": skill_val,
                "minplayers": minp_val,
                "queue": DEFAULT_BOT_MAP_QUEUE
            }
        }
        active_procs[port] = proc
        return {"status": "success", "port": port, "pid": proc.pid}
    except Exception as e:
        logger.error(f"Failed to spawn server: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/admin/fetch-asset")
async def fetch_map_mod(request: Request, username: str = Depends(authenticate)):
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"status": "error", "message": "No URL provided"}
    
    qw_maps_dir = "/quake/qw/maps"
    os.makedirs(qw_maps_dir, exist_ok=True)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {"status": "error", "message": f"HTTP {resp.status}"}
                zip_data = await resp.read()
                
                # Dynamically extract maps straight into engine active volume
                with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                    for file_info in z.infolist():
                        if file_info.filename.endswith('.bsp'):
                            z.extract(file_info, qw_maps_dir)
                            logger.info(f"Ingested MAP: {file_info.filename}")
        return {"status": "success", "message": "Asset Extracted"}
    except Exception as e:
        logger.error(f"Asset ingestion failed: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/admin/rcon")
async def execute_rcon(request: Request, username: str = Depends(authenticate)):
    data = await request.json()
    port = data.get("port")
    cmd = data.get("command")
    
    if not port or not cmd:
        return {"status": "error", "message": "Missing port or command"}
        
    proc = active_procs.get(int(port))
    if not proc:
        # SUPERVISORD 27500 relies on external rcon utility. For orchestrator we lock to subs.
        return {"status": "error", "message": f"No active native subprocess memory found targeting Port {port}"}
    
    try:
        proc.stdin.write(f"{cmd}\n".encode())
        await proc.stdin.drain()
        return {"status": "success", "message": f"Command '{cmd}' physically injected into Port {port} Memory Space"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/admin/config")
async def update_config(request: Request, username: str = Depends(authenticate)):
    data = await request.json()
    try:
        port_target = data.get('port')
        queue = data.get('map_queue')
        if not queue: queue = DEFAULT_BOT_MAP_QUEUE
        
        minp = data.get('minplayers') or 4
        bskill = data.get('bot_skill1') or 2
        t_limit = data.get('timelimit') or 3
        f_limit = data.get('fraglimit') or 8
        
        if not port_target:
            return {"status": "error", "message": "Explicit Port required for local orchestration!"}
            
        port_target = int(port_target)
        
        # REAL-TIME SECURE ORCHESTRATION INJECTION (Bypasses Subprocess Restarts)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        
        try:
            # Formally emit discrete RCON packets chronologically to bypass Quake's semicolon token dropping constraint natively!
            maps = queue.strip().split()
            
            # Store Target State purely inside immutable Orchestrator isolation matrix
            if port_target in active_servers:
                active_servers[port_target].setdefault("target_state", {})
                active_servers[port_target]["target_state"]["bot_skill1"] = str(bskill)
                active_servers[port_target]["target_state"]["timelimit"] = str(t_limit)
                active_servers[port_target]["target_state"]["fraglimit"] = str(f_limit)
                active_servers[port_target]["target_state"]["minplayers"] = minp
                active_servers[port_target]["target_state"]["queue"] = " ".join(maps)
                
            cmds = [
                f"localinfo minplayers {minp}",
                f"set k_fb_autoadd_limit {minp}",
                f"set k_fb_skill {bskill}",
                f"fraglimit {f_limit}",
                f"localinfo fraglimit {f_limit}",
                f"timelimit {t_limit}",
                f"localinfo timelimit {t_limit}",
                "samelevel 0",
                "set k_matchless 1",
                "set k_random_maplist 1",
                "set k_defmode ffa",
                "set deathmatch 1"
            ]
            
            # Map Rotation arrays explicitly use k_ml_0, k_ml_1 in Matchless FFA Mode
            # Dynamically sizing the loop natively ensures we cleanly override extreme arrays like the 71-map queue
            for i in range(max(len(maps) + 5, 20)):
                if i < len(maps):
                    cmds.append(f'set k_ml_{i} "{maps[i]}"')
                else:
                    cmds.append(f'set k_ml_{i} ""')

            for cmd in cmds:
                sock.sendto(b"\xff\xff\xff\xffrcon " + ADMIN_PASSWORD.encode('utf-8') + b" " + cmd.encode('utf-8') + b"\n", ("127.0.0.1", port_target))
            
        except Exception:
            return {"status": "error", "message": "Failed UDP Handshake on Target Port!"}
            
        return {"status": "success", "message": f"Engine array rewritten dynamically on Port {port_target}."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/admin/nextmap")
async def rotate_next_map(request: Request, username: str = Depends(authenticate)):
    data = await request.json()
    port_target = data.get('port')
    
    if not port_target:
        return {"status": "error", "message": "Explicit Port required for local orchestration!"}
        
    port_target = int(port_target)
    
    if port_target in active_servers:
        queue_str = active_servers[port_target].get("target_state", {}).get("queue", DEFAULT_BOT_MAP_QUEUE)
        cur_map = active_servers[port_target].get("engine_state", {}).get("map", "")
        maps = queue_str.strip().split()
        
        if maps:
            import random
            # Safely extract all vectors excluding the currently active map geometry
            available_maps = [m for m in maps if m != cur_map] or maps
            next_tgt = random.choice(available_maps)
                
            # Send mapping packet directly to engine (Burst x3 to negate raw UDP network dropped packets natively)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = b"\xff\xff\xff\xffrcon " + ADMIN_PASSWORD.encode('utf-8') + b" map " + next_tgt.encode('utf-8') + b"\n"
            for _ in range(3):
                sock.sendto(payload, ("127.0.0.1", port_target))
            
            return {"status": "success", "message": f"Server forcefully rotated to Target: {next_tgt}"}
            
    return {"status": "error", "message": "Server memory block uninitialized or missing map array!"}

# Passive JSON Stats Scanner
async def stats_monitor():
    """Polls KTX output folder for standard JSON match stat dumps and enforces active parameters continuously."""
    stats_dir = "/quake/qw/stats/json"
    processed = set()
    os.makedirs(stats_dir, exist_ok=True)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        try:
            RCON_MAPPINGS = {
                "fraglimit": ["fraglimit {v}", "localinfo fraglimit {v}"],
                "timelimit": ["timelimit {v}", "localinfo timelimit {v}"],
                "minplayers": ["localinfo minplayers {v}", "set k_fb_autoadd_limit {v}"],
                "bot_skill1": ["set k_fb_skill {v}"]
            }
            
            # Heartbeat Enforcer Loop: Protects limits from KTX Matchless mode resets natively
            for port, srv in active_servers.items():
                targets = srv.get("target_state", {})
                queue_str = targets.get("queue", DEFAULT_BOT_MAP_QUEUE)
                maps = queue_str.strip().split()

                heartbeat_cmds = [
                    "set k_matchless 1",
                    "set k_random_maplist 1",
                    "set k_defmode ffa",
                    "set deathmatch 1",
                    "samelevel 0"
                ]

                # Dynamically construct KTX's native cyclic rotation array mechanically!
                for i in range(len(maps)):
                    heartbeat_cmds.append(f'set k_ml_{i} "{maps[i]}"')
                
                for key, templates in RCON_MAPPINGS.items():
                    if key in targets:
                        for template in templates:
                            heartbeat_cmds.append(template.format(v=targets[key]))
                for c in heartbeat_cmds:
                    sock.sendto(b"\xff\xff\xff\xffrcon " + ADMIN_PASSWORD.encode('utf-8') + b" " + c.encode('utf-8') + b"\n", ("127.0.0.1", port))
                    
            for file in os.listdir(stats_dir):
                if file.endswith(".json") and file not in processed:
                    path = os.path.join(stats_dir, file)
                    with open(path, 'r') as f:
                        data = json.load(f)
                        # Minimal KTX JSON interpretation
                        if "players" in data:
                            # Safely extract maximum match frags to natively dictate organic match winners
                            max_frags = -9999
                            for p in data["players"]:
                                f = p.get("stats", {}).get("frags", 0)
                                if f > max_frags: max_frags = f
                                
                            for p in data["players"]:
                                name = p.get("name", "Unknown")
                                stats_block = p.get("stats", {})
                                p_frags = stats_block.get("frags", 0)
                                deaths = stats_block.get("deaths", 0)
                                
                                if "bot" not in name.lower() and "frog" not in name.lower():
                                    is_win = (p_frags == max_frags and p_frags > 0)
                                    # Terminate Session Explicitly
                                    sess_id = global_delta_tracker.get(name, {}).get("session_id")
                                    if sess_id:
                                        update_session_match_end(sess_id, deaths=deaths, is_win=is_win)
                                        # Reset Live Tracker
                                        global_delta_tracker.pop(name, None)
                    
                    # FUNDAMENTAL ORCHESTRATION OVERRIDE: Mechanical native rotation upon Match Finalization
                    # This completely bypasses any native KTX Matchless stalling natively!
                    try:
                        import random
                        fallback_port = 27500
                        # Extract port from JSON if natively available, else rely on Root Node Port 27500
                        active_port = data.get("server", {}).get("port", fallback_port)
                        queue_str = active_servers.get(active_port, {}).get("target_state", {}).get("queue", DEFAULT_BOT_MAP_QUEUE)
                        available_maps = queue_str.strip().split()
                        
                        if available_maps:
                            cur_map = active_servers.get(active_port, {}).get("engine_state", {}).get("map", "")
                            safe_maps = [m for m in available_maps if m != cur_map] or available_maps
                            next_tgt = random.choice(safe_maps)
                            
                            # Fire triple-burst manual map override straight to engine
                            for _ in range(3):
                                sock.sendto(b"\xff\xff\xff\xffrcon " + ADMIN_PASSWORD.encode('utf-8') + b" map " + next_tgt.encode('utf-8') + b"\n", ("127.0.0.1", active_port))
                    except Exception:
                        pass
                        
                    processed.add(file)
        except Exception as e:
            pass # Suppress poll errors
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    import random
    # Force the base Daemon Server (Port 27500) to immediately rotate randomly specifically escaping the legacy 'dm3' server.cfg trap!
    startup_map = random.choice(DEFAULT_BOT_MAP_QUEUE.split())
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"\xff\xff\xff\xffrcon " + ADMIN_PASSWORD.encode('utf-8') + b" map " + startup_map.encode('utf-8') + b"\n", ("127.0.0.1", 27500))
    except Exception:
        pass
    asyncio.create_task(stats_monitor())
