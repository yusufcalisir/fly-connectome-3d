"""FastAPI application providing WebSocket telemetry streaming and REST APIs."""

import asyncio
import base64
import io
import sys
import traceback
from contextlib import asynccontextmanager, nullcontext
from pathlib import Path
from typing import Any, Dict, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np
import scipy.sparse as sp
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel
from starlette.websockets import WebSocketState

from ..brain import ConnectomeBrain
from ..data.circuits import IndexedCircuits, load_malecns_v1_connectome
from .state import ServerStateManager

# ---------------------------------------------------------------------------
# Module-level globals
# ---------------------------------------------------------------------------
STATE_MANAGER = ServerStateManager()

candidate_frontend = Path(__file__).resolve().parents[3] / "frontend"
if not candidate_frontend.exists():
    candidate_frontend = Path(__file__).resolve().parents[2] / "frontend"
FRONTEND_DIR = candidate_frontend

# Active WebSocket connections
CONNECTED_SOCKETS: set = set()

# Global Brain Instance (initialized at import time)
GLOBAL_BRAIN: Optional[ConnectomeBrain] = None

# Async lock – prevents concurrent frame processing across coroutines.
# Initialized in the lifespan handler so it belongs to the correct event loop.
_FRAME_LOCK: Optional[asyncio.Lock] = None


# ---------------------------------------------------------------------------
# Brain initialisation (synchronous, runs at import / module startup)
# ---------------------------------------------------------------------------
def initialize_default_brain() -> None:
    """Initialize the connectome brain with the official 166.7K Janelia MaleCNS v1.0 dataset."""
    global GLOBAL_BRAIN
    data_dir = Path(__file__).resolve().parents[3] / "data" / "malecns_v1"
    graph_path = data_dir / "malecns_v1_graph.npz"

    if graph_path.exists():
        print(f"[*] Loading official Janelia MCNS v1.0 connectome from {graph_path}...")
        n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)
        print(f"    [+] Successfully loaded {n_nodes:,} biological neurons and {adj.nnz:,} synapses!")
        GLOBAL_BRAIN = ConnectomeBrain(n_nodes, adj, circuits)
    else:
        print("[!] Official MCNS v1.0 graph not found, initializing representative bio-circuit graph.")
        n_nodes = 500
        adj = sp.random(n_nodes, n_nodes, density=0.04, format="csr", dtype=np.float32)

        # 64% Excitatory (ACh), 36% Inhibitory (GABA/Glu)
        exc_neurons = np.arange(0, 320, dtype=np.int32)
        inh_neurons = np.arange(320, 500, dtype=np.int32)
        polarity = np.ones(n_nodes, dtype=np.int8)
        polarity[320:] = -1

        circuits = IndexedCircuits(
            r1_r6_photoreceptors=np.arange(0, 80, dtype=np.int32),
            r8_photoreceptors=np.arange(80, 120, dtype=np.int32),
            looming_threat_lc4=np.arange(120, 150, dtype=np.int32),
            pam11_dopamine_reward=np.arange(150, 165, dtype=np.int32),
            ppl101_dopamine_aversive=np.arange(165, 167, dtype=np.int32),
            octopamine_stress=np.arange(167, 185, dtype=np.int32),
            serotonin_calm=np.arange(185, 205, dtype=np.int32),
            kenyon_cells=np.arange(205, 350, dtype=np.int32),
            mbon07_reward_output=np.arange(350, 354, dtype=np.int32),
            mbon11_aversive_output=np.arange(354, 356, dtype=np.int32),
            epg_compass_neurons=np.arange(356, 420, dtype=np.int32),
            dna02_left=np.arange(420, 422, dtype=np.int32),
            dna02_right=np.arange(422, 424, dtype=np.int32),
            dnp09_forward=np.arange(424, 432, dtype=np.int32),
            mdn_moonwalker=np.arange(432, 434, dtype=np.int32),
            giant_fiber_escape=np.arange(434, 436, dtype=np.int32),
            excitatory_neurons=exc_neurons,
            inhibitory_neurons=inh_neurons,
            polarity=polarity,
        )

        GLOBAL_BRAIN = ConnectomeBrain(n_nodes, adj, circuits)


initialize_default_brain()


# ---------------------------------------------------------------------------
# FastAPI lifespan – creates the asyncio.Lock in the correct event loop
# ---------------------------------------------------------------------------
@asynccontextmanager
async def _lifespan(application: "FastAPI"):
    global _FRAME_LOCK
    _FRAME_LOCK = asyncio.Lock()
    yield


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Connectome Telemetry Engine", version="0.1.0", lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------
class WireheadRequest(BaseModel):
    current_mv: float = 20.0


class FrameSubmissionRequest(BaseModel):
    image_base64: str  # Base64 encoded JPEG or PNG
    duration_ms: float = 50.0


# ---------------------------------------------------------------------------
# Frame processing (runs in a thread via asyncio.to_thread)
# ---------------------------------------------------------------------------
def _process_frame(image_base64: str, duration_ms: float = 50.0) -> Dict[str, Any]:
    """Process an incoming retinal frame, step the biophysical brain, and update state."""
    global GLOBAL_BRAIN
    if GLOBAL_BRAIN is None:
        raise RuntimeError("Brain not initialized")

    data = base64.b64decode(image_base64.split(",")[-1])
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    img = img.resize((90, 160))
    frame_rgba = np.array(img, dtype=np.uint8)

    manual_boost = STATE_MANAGER.consume_wirehead()
    telemetry = GLOBAL_BRAIN.observe_frame(
        frame_rgba,
        duration_ms=duration_ms,
        manual_dopamine_boost_mv=manual_boost,
    )
    STATE_MANAGER.push_telemetry(telemetry)

    return STATE_MANAGER.get_snapshot()


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------
@app.post("/api/wirehead")
async def trigger_wirehead(req: WireheadRequest):
    """Trigger immediate artificial dopamine surge (+20 mV default).

    Boundary note: This is a numerical current-injection stimulation check (+20 mV into
    the 15 PAM11 dopamine neurons), not evidence of reward, pleasure, or learned preference.
    No living fly is involved, and preference/addiction have not been established.
    """
    STATE_MANAGER.trigger_wirehead(req.current_mv)
    return {"status": "ok", "message": f"Injected {req.current_mv} mV dopamine pulse"}


@app.post("/api/observe")
async def submit_frame(req: FrameSubmissionRequest):
    """Submit a virtual screen observation frame and step the biological brain."""
    if _FRAME_LOCK is not None and _FRAME_LOCK.locked():
        # Previous frame still stepping SNN; drop frame to prevent queue backlog
        return STATE_MANAGER.get_snapshot()

    lock = _FRAME_LOCK if _FRAME_LOCK is not None else nullcontext()
    async with lock:
        try:
            snapshot = await asyncio.to_thread(_process_frame, req.image_base64, req.duration_ms)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Observation failed: {e}")

        # Broadcast to active WebSockets
        for ws in list(CONNECTED_SOCKETS):
            try:
                if ws.application_state == WebSocketState.CONNECTED:
                    await ws.send_json(snapshot)
                else:
                    CONNECTED_SOCKETS.discard(ws)
            except Exception:
                CONNECTED_SOCKETS.discard(ws)

        return snapshot


@app.get("/api/telemetry")
async def get_telemetry():
    """Fetch current telemetry and rolling chart history."""
    return STATE_MANAGER.get_snapshot()


# ---------------------------------------------------------------------------
# Connectome 3D Soma Coordinates & Metadata Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/connectome/soma-coordinates")
async def get_soma_coordinates():
    """Stream binary buffer of 141K real neuron soma coordinates."""
    data_dir = Path(__file__).resolve().parents[3] / "data" / "malecns_v1"
    bin_path = data_dir / "soma_coordinates_141k.bin"
    if not bin_path.exists():
        raise HTTPException(status_code=404, detail="Soma coordinates binary file not found")
    return FileResponse(
        str(bin_path),
        media_type="application/octet-stream",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/api/connectome/soma-metadata")
async def get_soma_metadata():
    """Return JSON metadata of soma coordinates, bounds, and circuit distribution."""
    data_dir = Path(__file__).resolve().parents[3] / "data" / "malecns_v1"
    meta_path = data_dir / "soma_metadata.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Soma metadata JSON file not found")
    return FileResponse(
        str(meta_path),
        media_type="application/json",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """Real-time bi-directional telemetry and command stream."""
    await websocket.accept()
    CONNECTED_SOCKETS.add(websocket)
    client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "web client"
    print(f"[WS] [+] Cockpit connected ({client_info}) - real-time telemetry streaming active.", flush=True)
    try:
        # Send initial snapshot immediately on connect
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_json(STATE_MANAGER.get_snapshot())

        while True:
            # Check for disconnect before blocking on receive
            if (
                websocket.client_state == WebSocketState.DISCONNECTED
                or websocket.application_state == WebSocketState.DISCONNECTED
            ):
                break

            # Receive client command with a timeout so we can send keep-alive pings
            # when the observation loop is paused or slow.
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
            except asyncio.TimeoutError:
                # No message in 10 s → send a lightweight ping to keep the connection alive
                try:
                    if websocket.application_state == WebSocketState.CONNECTED:
                        await websocket.send_json({"ping": True})
                    else:
                        break
                except Exception:
                    break  # socket is genuinely dead
                continue
            except (WebSocketDisconnect, RuntimeError, ConnectionResetError, OSError):
                # Client closed socket, refreshed tab, or socket died cleanly
                break

            if not isinstance(data, dict):
                continue

            cmd = data.get("command")

            if cmd == "pong":
                # Heartbeat acknowledgement from browser client
                continue

            elif cmd == "wirehead":
                boost = float(data.get("current_mv", 20.0))
                STATE_MANAGER.trigger_wirehead(boost)
                print(f"[Neural Surge] [*] Wirehead stimulation pulse: +{boost:.1f} mV", flush=True)

            elif cmd == "stimulus_preset":
                preset = data.get("preset", "unknown")
                name = data.get("name", preset)
                valence = data.get("valence", "NEUTRAL")
                print(f"[Stimulus Arena] [*] Selected preset: {name} | Valence: {valence}", flush=True)

            elif cmd == "target_position":
                pos = str(data.get("position", "center")).upper()
                print(f"[Phototaxis] [*] Target position shifted to: {pos} | Asymmetric retinal illumination active", flush=True)

            elif cmd == "threat_trigger":
                print("[Threat Alert] [!] LC4 looming pulse triggered | Rapid visual shadow -> Giant Fiber escape jump", flush=True)

            elif cmd == "leg_swipe":
                print("[Motor Circuit] [*] DNp09 descending command -> T1 prothoracic leg sweep activated", flush=True)

            elif cmd == "custom_photo":
                fname = data.get("name", "Custom Photo")
                valence = data.get("valence", "CUSTOM")
                print(f"[Stimulus Arena] [*] Custom image mapped to retina: {fname} | Spectral: {valence}", flush=True)

            elif cmd == "observe":
                img_b64 = data.get("image_base64", "")
                dur = float(data.get("duration_ms", 50.0))
                if img_b64:
                    lock = _FRAME_LOCK if _FRAME_LOCK is not None else nullcontext()
                    async with lock:
                        try:
                            snapshot = await asyncio.to_thread(_process_frame, img_b64, dur)
                            for ws in list(CONNECTED_SOCKETS):
                                try:
                                    if ws.application_state == WebSocketState.CONNECTED:
                                        await ws.send_json(snapshot)
                                    else:
                                        CONNECTED_SOCKETS.discard(ws)
                                except Exception:
                                    CONNECTED_SOCKETS.discard(ws)
                        except Exception as exc:
                            # Log the real error so it appears in the uvicorn console
                            print(f"[WS] Frame processing error: {exc}")
                            traceback.print_exc()

            elif cmd == "pause":
                STATE_MANAGER.is_paused = True

            elif cmd == "resume":
                STATE_MANAGER.is_paused = False

    except (WebSocketDisconnect, RuntimeError, ConnectionResetError, OSError):
        pass  # clean client-initiated close or disconnect – nothing to log
    except Exception as exc:
        print(f"[WS] Unexpected WebSocket error: {exc}")
        traceback.print_exc()
    finally:
        CONNECTED_SOCKETS.discard(websocket)
        print("[WS] [-] Cockpit disconnected.", flush=True)


# ---------------------------------------------------------------------------
# Static file serving & favicon
# ---------------------------------------------------------------------------
@app.get("/favicon.ico")
@app.get("/favicon.svg")
async def favicon():
    """Return logo.svg for browser tab favicon."""
    fav = FRONTEND_DIR / "logo.svg"
    if fav.exists():
        return FileResponse(str(fav), media_type="image/svg+xml")
    return Response(status_code=204)


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(
            str(FRONTEND_DIR / "index.html"),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
