"""FastAPI application providing WebSocket telemetry streaming and REST APIs."""

import asyncio
import base64
import io
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from .state import ServerStateManager
from ..brain import ConnectomeBrain
from ..data.circuits import IndexedCircuits, load_malecns_v1_connectome
import scipy.sparse as sp

app = FastAPI(title="Connectome Telemetry Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_MANAGER = ServerStateManager()

candidate_frontend = Path(__file__).resolve().parents[3] / "frontend"
if not candidate_frontend.exists():
    candidate_frontend = Path(__file__).resolve().parents[2] / "frontend"
FRONTEND_DIR = candidate_frontend

# Active WebSocket connections
CONNECTED_SOCKETS = set()

# Global Brain Instance (initialized on startup)
GLOBAL_BRAIN: Optional[ConnectomeBrain] = None
IS_PROCESSING_FRAME = False


def initialize_default_brain():
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
        )

        GLOBAL_BRAIN = ConnectomeBrain(n_nodes, adj, circuits)


initialize_default_brain()


class WireheadRequest(BaseModel):
    current_mv: float = 20.0


class FrameSubmissionRequest(BaseModel):
    image_base64: str  # Base64 encoded JPEG or PNG
    duration_ms: float = 50.0


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


@app.post("/api/wirehead")
async def trigger_wirehead(req: WireheadRequest):
    """Trigger immediate artificial dopamine surge (+20 mV default)."""
    STATE_MANAGER.trigger_wirehead(req.current_mv)
    return {"status": "ok", "message": f"Injected {req.current_mv} mV dopamine pulse"}


@app.post("/api/observe")
async def submit_frame(req: FrameSubmissionRequest):
    """Submit a virtual screen observation frame and step the biological brain."""
    try:
        snapshot = _process_frame(req.image_base64, req.duration_ms)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Observation failed: {e}")

    # Broadcast to active WebSockets
    for ws in list(CONNECTED_SOCKETS):
        try:
            await ws.send_json(snapshot)
        except Exception:
            CONNECTED_SOCKETS.discard(ws)

    return snapshot


@app.get("/api/telemetry")
async def get_telemetry():
    """Fetch current telemetry and rolling chart history."""
    return STATE_MANAGER.get_snapshot()


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """Real-time bi-directional telemetry and command stream."""
    await websocket.accept()
    CONNECTED_SOCKETS.add(websocket)
    try:
        # Send initial snapshot
        await websocket.send_json(STATE_MANAGER.get_snapshot())
        while True:
            # Keep connection alive and receive incoming client commands
            data = await websocket.receive_json()
            cmd = data.get("command")
            if cmd == "wirehead":
                boost = float(data.get("current_mv", 20.0))
                STATE_MANAGER.trigger_wirehead(boost)
            elif cmd == "observe":
                global IS_PROCESSING_FRAME
                img_b64 = data.get("image_base64", "")
                dur = float(data.get("duration_ms", 50.0))
                if img_b64 and not IS_PROCESSING_FRAME:
                    IS_PROCESSING_FRAME = True
                    try:
                        snapshot = await asyncio.to_thread(_process_frame, img_b64, dur)
                        for ws in list(CONNECTED_SOCKETS):
                            try:
                                await ws.send_json(snapshot)
                            except Exception:
                                CONNECTED_SOCKETS.discard(ws)
                    finally:
                        IS_PROCESSING_FRAME = False
            elif cmd == "pause":
                STATE_MANAGER.is_paused = True
            elif cmd == "resume":
                STATE_MANAGER.is_paused = False
    except WebSocketDisconnect:
        CONNECTED_SOCKETS.discard(websocket)
    except Exception:
        CONNECTED_SOCKETS.discard(websocket)


# Mount static frontend files if directory exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
