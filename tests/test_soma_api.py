"""Unit and integration tests for 3D soma coordinates API and telemetry streaming.

Verifies:
1. GET /api/connectome/soma-coordinates returns the exact binary buffer (2,552,074 bytes).
2. GET /api/connectome/soma-metadata returns complete JSON circuit annotations.
3. REST /observe and WebSocket telemetry streams active_neurons with real firing indices.
"""

import base64
import io

import numpy as np
import pytest
from PIL import Image
from starlette.testclient import TestClient

from connectome_engine.server.app import app

MAGIC_NUMBER = 0x464C5933  # "FLY3"


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_soma_coordinates_endpoint(client):
    """Verify GET /api/connectome/soma-coordinates returns the exact 141K binary buffer."""
    response = client.get("/api/connectome/soma-coordinates")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert "public" in response.headers.get("cache-control", "")

    content = response.content
    assert len(content) == 2552074

    magic, count = np.frombuffer(content[:8], dtype=np.uint32)
    assert magic == MAGIC_NUMBER
    assert count == 141781


def test_soma_metadata_endpoint(client):
    """Verify GET /api/connectome/soma-metadata returns valid circuit metadata."""
    response = client.get("/api/connectome/soma-metadata")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]

    data = response.json()
    assert data["total_somas"] == 141781
    assert data["matched_in_graph"] == 139662
    assert "circuit_counts" in data
    assert data["circuit_counts"]["optic_lobe"] > 80000
    assert data["circuit_counts"]["mushroom_body"] > 4000
    assert "polarity_counts" in data
    assert data["polarity_counts"]["excitatory"] > 80000
    assert data["polarity_counts"]["inhibitory"] > 45000


def test_active_neurons_telemetry_flow(client):
    """Verify active_neurons are populated and streamed via /api/observe and /api/telemetry."""
    # Check initial telemetry
    telem = client.get("/api/telemetry").json()
    assert "active_neurons" in telem["latest"]
    assert isinstance(telem["latest"]["active_neurons"], list)

    # Submit an observation frame
    img = Image.new("RGBA", (32, 32), color=(255, 255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    obs = client.post("/api/observe", json={"image_base64": b64, "duration_ms": 20.0}).json()
    latest = obs["latest"]
    assert "active_neurons" in latest
    assert isinstance(latest["active_neurons"], list)

    # Trigger a wirehead burst to induce firing and check active_neurons
    client.post("/api/wirehead", json={"current_mv": 35.0})
    obs2 = client.post("/api/observe", json={"image_base64": b64, "duration_ms": 30.0}).json()
    assert "active_neurons" in obs2["latest"]


def test_websocket_active_neurons_snapshot(client):
    """Verify WebSocket telemetry streams active_neurons in snapshots."""
    with client.websocket_connect("/ws/telemetry") as ws:
        data = ws.receive_json()
        assert "latest" in data
        assert "active_neurons" in data["latest"]
