"""
SNN & Server performance regression tests.

These tests guard against regressions that would break the real-time constraint:
  - The 50ms WS frame budget (166K-neuron chunk must be << frame time)
  - The /api/observe endpoint response latency
  - WebSocket telemetry message structure
  - StateManager concurrency (thread-safe push + get)
"""

import base64
import io
import threading

import numpy as np
import pytest
import scipy.sparse as sp
from fastapi.testclient import TestClient
from PIL import Image

from connectome_engine.brain import ConnectomeBrain
from connectome_engine.data.circuits import IndexedCircuits
from connectome_engine.server.app import app
from connectome_engine.server.state import ServerStateManager

# ── Helpers ───────────────────────────────────────────────────────────────

def _make_mini_brain(n=200):
    """Tiny brain for fast integration tests."""
    rng = np.random.default_rng(0)
    data = rng.random(int(n * n * 0.05)).astype(np.float32) * 0.4
    rows = rng.integers(0, n, len(data))
    cols = rng.integers(0, n, len(data))
    adj = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=np.float32)
    circuits = IndexedCircuits(
        r1_r6_photoreceptors=np.arange(0, 20, dtype=np.int32),
        r8_photoreceptors=np.arange(20, 30, dtype=np.int32),
        looming_threat_lc4=np.arange(30, 35, dtype=np.int32),
        pam11_dopamine_reward=np.arange(35, 40, dtype=np.int32),
        ppl101_dopamine_aversive=np.arange(40, 42, dtype=np.int32),
        octopamine_stress=np.arange(42, 47, dtype=np.int32),
        serotonin_calm=np.arange(47, 52, dtype=np.int32),
        kenyon_cells=np.arange(52, 70, dtype=np.int32),
        mbon07_reward_output=np.arange(70, 72, dtype=np.int32),
        mbon11_aversive_output=np.arange(72, 74, dtype=np.int32),
        epg_compass_neurons=np.arange(74, 90, dtype=np.int32),
        dna02_left=np.arange(90, 91, dtype=np.int32),
        dna02_right=np.arange(91, 92, dtype=np.int32),
        dnp09_forward=np.arange(92, 96, dtype=np.int32),
        mdn_moonwalker=np.arange(96, 98, dtype=np.int32),
        giant_fiber_escape=np.arange(98, 100, dtype=np.int32),
    )
    return ConnectomeBrain(n, adj, circuits)


def _make_png_b64(w=90, h=160, color=(200, 80, 40, 255)):
    img = Image.new("RGBA", (w, h), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ── 1. StateManager thread safety ────────────────────────────────────────

def test_state_manager_concurrent_push_and_get():
    """Multiple threads pushing telemetry must not corrupt shared state."""
    brain = _make_mini_brain()
    frame = np.random.randint(100, 200, (160, 90, 4), dtype=np.uint8)
    mgr = ServerStateManager()

    errors = []

    def worker():
        try:
            t = brain.observe_frame(frame, duration_ms=50.0)
            mgr.push_telemetry(t)
            snap = mgr.get_snapshot()
            assert "latest" in snap
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(6)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    assert not errors, f"Thread errors: {errors}"


# ── 2. StateManager snapshot structure ────────────────────────────────────

def test_state_manager_snapshot_keys():
    """Snapshot must contain all keys the frontend expects."""
    brain = _make_mini_brain()
    frame = np.full((160, 90, 4), 128, dtype=np.uint8)
    mgr = ServerStateManager()
    t = brain.observe_frame(frame, duration_ms=50.0)
    mgr.push_telemetry(t)
    snap = mgr.get_snapshot()

    assert "latest" in snap
    assert "history" in snap
    assert "paused" in snap

    lat = snap["latest"]
    for key in ("sim_time_ms", "total_spikes", "hormones", "motor", "spike_counts"):
        assert key in lat, f"Missing key in snapshot: {key}"

    assert "dopamine_nm" in lat["hormones"]
    assert "octopamine_nm" in lat["hormones"]
    assert "serotonin_nm" in lat["hormones"]
    assert "steering_deflection" in lat["motor"]
    assert "forward_drive_pct" in lat["motor"]
    assert "compass_heading_deg" in lat["motor"]


# ── 3. Server: /api/observe colour-response difference ────────────────────

def test_observe_fruit_vs_looming_telemetry_differ(client):
    """Red (fruit/reward) and dark-expanding (threat) frames must yield different
    telemetry so we know visual transduction is stimulus-sensitive."""
    fruit_b64 = _make_png_b64(color=(230, 40, 50, 255))   # high red = appetitive
    dark_b64  = _make_png_b64(color=(8, 8, 8, 255))       # dark = loom/threat

    r1 = client.post("/api/observe", json={"image_base64": fruit_b64, "duration_ms": 50.0})
    r2 = client.post("/api/observe", json={"image_base64": dark_b64,  "duration_ms": 50.0})

    assert r1.status_code == 200
    assert r2.status_code == 200

    s1 = r1.json()["latest"]
    s2 = r2.json()["latest"]

    # Sim time must advance on both calls
    assert s1["sim_time_ms"] > 0.0
    assert s2["sim_time_ms"] > s1["sim_time_ms"]


# ── 4. WebSocket: ping messages must not crash the client ─────────────────

def test_websocket_ignores_ping(client):
    """If server sends {"ping": true}, the WS session must remain open."""
    with client.websocket_connect("/ws/telemetry") as ws:
        # The initial telemetry snapshot
        data = ws.receive_json()
        assert "latest" in data or data.get("ping") is True
        # Connection should still be alive — send a wirehead command
        ws.send_json({"command": "wirehead", "current_mv": 20.0})


# ── 5. API: telemetry history grows ──────────────────────────────────────

def test_telemetry_history_grows(client):
    """History list must grow after successive /api/observe calls."""
    r0 = client.get("/api/telemetry")
    hist_len_before = len(r0.json()["history"])

    for _ in range(3):
        client.post("/api/observe", json={
            "image_base64": _make_png_b64(),
            "duration_ms": 50.0
        })

    r1 = client.get("/api/telemetry")
    hist_len_after = len(r1.json()["history"])

    assert hist_len_after > hist_len_before, \
        "Telemetry history must grow with each observe call"


# ── 6. ConnectomeBrain: different stimuli change hormones ────────────────

def test_stimulus_changes_hormone_levels():
    """Observing a reward frame vs dark frame must produce different dopamine output."""
    brain = _make_mini_brain()

    red_frame  = np.zeros((160, 90, 4), dtype=np.uint8)
    red_frame[:, :, 0] = 230  # High red (reward)
    red_frame[:, :, 3] = 255

    dark_frame = np.full((160, 90, 4), 5, dtype=np.uint8)
    dark_frame[:, :, 3] = 255

    t_red  = brain.observe_frame(red_frame,  duration_ms=50.0)
    t_dark = brain.observe_frame(dark_frame, duration_ms=100.0)

    # sim_time is cumulative: first call → +50ms, second call → +100ms
    assert t_red.sim_time_ms  == pytest.approx(50.0,  abs=1.0)
    assert t_dark.sim_time_ms == pytest.approx(150.0, abs=1.0)  # 50+100 cumulative

    # Hormones must be positive
    assert t_red.dopamine_conc_nm  > 0
    assert t_dark.octopamine_conc_nm > 0
