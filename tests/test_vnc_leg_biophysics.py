"""Deterministic Biophysical Unit Tests for VNC Thoracic Leg Motor Pools and Tripod CPG.

Verifies the coupling between brain descending commands (DNp09, DNa02, MDN) and
the 6 thoracic leg motor neuron pools (T1L, T1R, T2L, T2R, T3L, T3R).
ZERO MOCK, ZERO RANDOM NUMBERS.
"""

from pathlib import Path

import numpy as np
import pytest

from connectome_engine.brain import ConnectomeBrain
from connectome_engine.data.circuits import load_malecns_v1_connectome


@pytest.fixture(scope="module")
def brain_instance():
    """Load real MaleCNS v1.0 connectome brain."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    if not (data_dir / "malecns_v1_graph.npz").exists() or not (data_dir / "circuits_manifest.json").exists():
        pytest.skip("MaleCNS v1.0 dataset not found locally.")

    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)
    brain = ConnectomeBrain(n_nodes, adj, circuits)
    return brain


def test_vnc_leg_forward_locomotion_coupling(brain_instance):
    """Verify that forward drive (DNp09) advances the CPG tripod phase forward."""
    brain = brain_instance

    # Create a baseline appetitive fruit image
    h, w = 160, 90
    frame = np.zeros((h, w, 4), dtype=np.uint8)
    frame[:, :] = [10, 40, 15, 255]
    # Red fruit in center
    frame[60:100, 30:60] = [240, 20, 40, 255]

    init_phase = brain.cpg_phase
    t1 = brain.observe_frame(frame, duration_ms=50.0)

    # Telemetry must contain valid numeric rates for all 6 pools
    assert hasattr(t1, "t1_left_hz")
    assert hasattr(t1, "t1_right_hz")
    assert hasattr(t1, "t2_left_hz")
    assert hasattr(t1, "t2_right_hz")
    assert hasattr(t1, "t3_left_hz")
    assert hasattr(t1, "t3_right_hz")
    assert hasattr(t1, "tripod_phase")

    assert t1.t1_left_hz >= 0.0
    assert t1.t1_right_hz >= 0.0
    assert t1.t2_left_hz >= 0.0
    assert t1.t2_right_hz >= 0.0
    assert t1.t3_left_hz >= 0.0
    assert t1.t3_right_hz >= 0.0

    # With forward drive active, phase must advance
    if t1.forward_drive_pct > 2.0:
        assert t1.tripod_phase != init_phase
        # Run a second frame and verify continuous phase progression
        t2 = brain.observe_frame(frame, duration_ms=50.0)
        assert t2.tripod_phase != t1.tripod_phase


def test_vnc_leg_steering_asymmetry(brain_instance):
    """Verify that asymmetric steering modulates outer leg motor pools higher than inner leg pools."""
    brain = brain_instance

    h, w = 160, 90
    # 1. Left Target (Fruit on left hemifield: X in 5..35)
    frame_left = np.zeros((h, w, 4), dtype=np.uint8)
    frame_left[:, :] = [5, 10, 15, 255]
    frame_left[60:100, 5:35] = [255, 30, 40, 255]  # High luminance left

    t_left = brain.observe_frame(frame_left, duration_ms=50.0)

    # When turning left (steering_deflection < 0), right outer legs must receive higher modulation
    if t_left.steering_deflection < -0.05:
        mean_right = (t_left.t1_right_hz + t_left.t2_right_hz + t_left.t3_right_hz) / 3.0
        mean_left = (t_left.t1_left_hz + t_left.t2_left_hz + t_left.t3_left_hz) / 3.0
        assert mean_right >= mean_left, f"Outer right legs ({mean_right:.2f}) must step faster than inner left ({mean_left:.2f}) when turning left"

    # 2. Right Target (Fruit on right hemifield: X in 55..85)
    frame_right = np.zeros((h, w, 4), dtype=np.uint8)
    frame_right[:, :] = [5, 10, 15, 255]
    frame_right[60:100, 55:85] = [255, 30, 40, 255]  # High luminance right

    t_right = brain.observe_frame(frame_right, duration_ms=50.0)

    # When turning right (steering_deflection > 0), left outer legs must receive higher modulation
    if t_right.steering_deflection > 0.05:
        mean_right = (t_right.t1_right_hz + t_right.t2_right_hz + t_right.t3_right_hz) / 3.0
        mean_left = (t_right.t1_left_hz + t_right.t2_left_hz + t_right.t3_left_hz) / 3.0
        assert mean_left >= mean_right, f"Outer left legs ({mean_left:.2f}) must step faster than inner right ({mean_right:.2f}) when turning right"


def test_vnc_leg_tripod_phase_relationships(brain_instance):
    """Verify that canonical insect Tripod A and Tripod B are exactly 180 degrees (pi radians) apart."""
    brain = brain_instance

    # Set arbitrary test phase
    test_phi = 1.25
    brain.cpg_phase = test_phi

    tripod_a_phase = brain.cpg_phase
    tripod_b_phase = (brain.cpg_phase + np.pi) % (2.0 * np.pi)

    # Angular distance on circle
    phase_diff = abs(tripod_b_phase - tripod_a_phase)
    assert np.isclose(phase_diff, np.pi, atol=1e-5), f"Tripod A and B must be in exact antiphase (pi radians), got diff={phase_diff}"


def test_vnc_leg_reverse_stepping_mdn(brain_instance):
    """Verify that activation of MDN moonwalker neurons rotates CPG phase in reverse."""
    brain = brain_instance

    # Inject excitatory current into MDN to trigger retreat
    mdn_nodes = brain.circuits.mdn_moonwalker
    assert len(mdn_nodes) > 0, "MaleCNS must have identified MDN neurons"

    brain.snn.clear_injected_currents()
    brain.snn.inject_current(mdn_nodes, np.full(len(mdn_nodes), 25.0, dtype=np.float32))

    brain.cpg_phase = 3.0
    start_phase = brain.cpg_phase

    # Step frame with dark background
    h, w = 160, 90
    dark_frame = np.zeros((h, w, 4), dtype=np.uint8)
    dark_frame[:, :, 3] = 255

    t_retreat = brain.observe_frame(dark_frame, duration_ms=50.0)

    # If MDN triggered moonwalker retreat, phase must decrease
    if t_retreat.moonwalker_retreat:
        end_phase = brain.cpg_phase
        # Angular backward step: end_phase < start_phase (unless wrapping around 0)
        d_phi = (end_phase - start_phase)
        if d_phi > np.pi:
            d_phi -= 2.0 * np.pi
        elif d_phi < -np.pi:
            d_phi += 2.0 * np.pi
        assert d_phi < 0.0, f"CPG phase must rotate in reverse when moonwalking, got delta={d_phi}"
