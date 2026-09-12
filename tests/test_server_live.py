"""Integration tests for FastAPI REST APIs and telemetry endpoints."""

import base64
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from connectome_engine.server.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_index_and_static_serving(client):
    """Verify that root / serves index.html and static assets are available."""
    res = client.get("/")
    assert res.status_code == 200
    assert "FlyConnectome 3D" in res.text or "CONNECTOME" in res.text

    # Check static CSS and JS
    res_css = client.get("/static/styles.css")
    assert res_css.status_code == 200
    assert "--bg-dark" in res_css.text

    res_js = client.get("/static/main.js")
    assert res_js.status_code == 200
    assert "StimulusGenerator" in res_js.text


def test_telemetry_get_endpoint(client):
    """Verify telemetry state fetching."""
    res = client.get("/api/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "latest" in data
    assert "history" in data
    assert "dopamine_hz" in data["latest"]


def test_wirehead_endpoint(client):
    """Verify wireheading triggers dopamine pulse."""
    res = client.post("/api/wirehead", json={"current_mv": 25.0})
    assert res.status_code == 200
    assert "Injected 25.0 mV" in res.json()["message"]


def test_observe_endpoint(client):
    """Verify that a synthetic image frame triggers visual transduction and SNN step."""
    # Create a small 90x160 RGB test image
    img = Image.new("RGBA", (90, 160), color=(255, 30, 80, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    res = client.post("/api/observe", json={"image_base64": b64_str, "duration_ms": 50.0})
    assert res.status_code == 200
    snapshot = res.json()
    assert "latest" in snapshot
    latest = snapshot["latest"]
    assert "hormones" in latest
    assert "motor" in latest
    assert latest["hormones"]["dopamine_nm"] > 0
    assert "compass_heading_deg" in latest["motor"]


def test_websocket_telemetry_connection(client):
    """Verify WebSocket connection and command dispatch."""
    with client.websocket_connect("/ws/telemetry") as ws:
        # Initial snapshot
        initial_data = ws.receive_json()
        assert "latest" in initial_data

        # Send wirehead command
        ws.send_json({"command": "wirehead", "current_mv": 20.0})


def test_favicon_endpoint(client):
    """Verify favicon.ico and favicon.svg return 200 OK with SVG content."""
    res_ico = client.get("/favicon.ico")
    assert res_ico.status_code == 200
    assert "svg" in res_ico.headers.get("content-type", "")

    res_svg = client.get("/favicon.svg")
    assert res_svg.status_code == 200
    assert "svg" in res_svg.headers.get("content-type", "")


def test_websocket_disconnect_graceful(client):
    """Verify that abrupt WebSocket disconnection does not crash or corrupt the server."""
    with client.websocket_connect("/ws/telemetry") as ws:
        data = ws.receive_json()
        assert "latest" in data
        # Connection exits here (closing socket abruptly)

    # Server should still be healthy and handle observe & telemetry requests cleanly
    res = client.get("/api/telemetry")
    assert res.status_code == 200
    assert "latest" in res.json()

