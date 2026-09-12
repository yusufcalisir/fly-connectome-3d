"""Deterministic biophysical tests for asymmetric optomotor phototaxis and DNa02 steering.

Zero mock, zero random numbers. Validates that directional visual stimuli drive
contrasting bilateral optomotor currents, DNa02 descending activity, and
physical left/right steering deflection.
"""

from pathlib import Path

import numpy as np
import pytest

from connectome_engine.brain import ConnectomeBrain
from connectome_engine.data.circuits import load_malecns_v1_connectome


def _make_test_brain() -> ConnectomeBrain:
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    graph_path = data_dir / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip("MaleCNS v1.0 dataset not found locally.")
    num_nodes, adj, circuits, _ids = load_malecns_v1_connectome(data_dir)
    return ConnectomeBrain(num_nodes, adj, circuits)


def test_left_light_phototaxis_steering():
    """Verify that light on the left visual field produces decisive negative (left) steering."""
    brain = _make_test_brain()

    frame_left = np.zeros((160, 90, 4), dtype=np.uint8)
    frame_left[:, :45, :3] = 255  # Left half pure white
    frame_left[:, :, 3] = 255

    tel = None
    for _ in range(3):
        tel = brain.observe_frame(frame_left)

    assert tel is not None
    assert tel.left_luminance > 0.99
    assert tel.right_luminance < 0.01
    assert tel.hemispheric_asymmetry < -0.95
    assert tel.steering_deflection < -0.25, f"Expected steering < -0.25, got {tel.steering_deflection}"


def test_right_light_phototaxis_steering():
    """Verify that light on the right visual field produces decisive positive (right) steering."""
    brain = _make_test_brain()

    frame_right = np.zeros((160, 90, 4), dtype=np.uint8)
    frame_right[:, 45:, :3] = 255  # Right half pure white
    frame_right[:, :, 3] = 255

    tel = None
    for _ in range(3):
        tel = brain.observe_frame(frame_right)

    assert tel is not None
    assert tel.right_luminance > 0.99
    assert tel.left_luminance < 0.01
    assert tel.hemispheric_asymmetry > 0.95
    assert tel.steering_deflection > 0.25, f"Expected steering > 0.25, got {tel.steering_deflection}"


def test_center_light_straight_locomotion():
    """Verify that centered / symmetric visual stimulation maintains straight navigation."""
    brain = _make_test_brain()

    frame_center = np.full((160, 90, 4), 160, dtype=np.uint8)
    frame_center[:, :, 3] = 255

    tel = None
    for _ in range(2):
        tel = brain.observe_frame(frame_center)

    assert tel is not None
    assert abs(tel.left_luminance - tel.right_luminance) < 1e-3
    assert abs(tel.hemispheric_asymmetry) < 1e-3
    assert abs(tel.steering_deflection) < 0.12, f"Expected near zero steering, got {tel.steering_deflection}"


def test_darkness_stability():
    """Verify that pure darkness produces zero visual asymmetry and neutral steering."""
    brain = _make_test_brain()

    frame_dark = np.zeros((160, 90, 4), dtype=np.uint8)
    frame_dark[:, :, 3] = 255

    tel = brain.observe_frame(frame_dark)

    assert tel.mean_luminance == 0.0
    assert tel.left_luminance == 0.0
    assert tel.right_luminance == 0.0
    assert tel.hemispheric_asymmetry == 0.0
    assert tel.steering_deflection == 0.0


def test_telemetry_packet_fields():
    """Verify all bilateral fields exist and are accurately typed on CompleteObservationTelemetry."""
    brain = _make_test_brain()

    frame = np.full((160, 90, 4), 200, dtype=np.uint8)
    tel = brain.observe_frame(frame)

    assert isinstance(tel.left_luminance, float)
    assert isinstance(tel.right_luminance, float)
    assert isinstance(tel.hemispheric_asymmetry, float)
    assert isinstance(tel.dna02_left_spikes, int)
    assert isinstance(tel.dna02_right_spikes, int)
    assert -1.0 <= tel.steering_deflection <= 1.0
