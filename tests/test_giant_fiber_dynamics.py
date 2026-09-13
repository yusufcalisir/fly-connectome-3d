"""Verification and regression tests for Giant Fiber escape jump biological gating and reset dynamics."""

import numpy as np
import pytest

from connectome_engine.brain import ConnectomeBrain
from connectome_engine.config import DATA_DIR
from connectome_engine.data.circuits import load_malecns_v1_connectome
from connectome_engine.simulation.motor_decoder import MotorBehavioralDecoder


def test_motor_decoder_giant_fiber_gating():
    """Verify that MotorBehavioralDecoder requires looming threat gating to fire jump."""
    decoder = MotorBehavioralDecoder()

    # Spontaneous connectome spikes in GF without looming threat must NOT trigger jump
    telemetry_no_threat = decoder.decode(
        dna02_left_spikes=0,
        dna02_right_spikes=0,
        dnp09_forward_spikes=4,
        mdn_reverse_spikes=0,
        giant_fiber_spikes=5,  # Spontaneous recurrent spikes
        looming_threat=False,
    )
    assert not telemetry_no_threat.giant_fiber_jump, (
        "Giant Fiber jump must be False when looming_threat is False, even if GF neurons spike"
    )

    # GF spikes with active looming threat MUST trigger emergency escape jump
    telemetry_threat = decoder.decode(
        dna02_left_spikes=0,
        dna02_right_spikes=0,
        dnp09_forward_spikes=0,
        mdn_reverse_spikes=0,
        giant_fiber_spikes=5,
        looming_threat=True,
    )
    assert telemetry_threat.giant_fiber_jump, (
        "Giant Fiber jump must be True when looming_threat is True and GF neurons spike"
    )


def test_giant_fiber_looming_and_reset_sequence():
    """Verify that in the integrated connectome, giant_fiber_jump fires during looming and resets thereafter."""
    graph_path = DATA_DIR / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip("MaleCNS v1.0 graph not found, skipping full connectome test.")

    n_nodes, adj, circuits, _neuron_ids = load_malecns_v1_connectome(DATA_DIR)
    brain = ConnectomeBrain(n_nodes, adj, circuits)

    white = np.full((160, 90, 4), 255, dtype=np.uint8)
    black = np.full((160, 90, 4), 0, dtype=np.uint8)

    # 1. Baseline ambient frame: no threat
    t1 = brain.observe_frame(white, duration_ms=50.0)
    assert not t1.looming_threat_detected
    assert not t1.giant_fiber_jump

    # 2. Rapid darkening frame: triggers looming threat and GF jump
    t2 = brain.observe_frame(black, duration_ms=50.0)
    assert t2.looming_threat_detected
    assert t2.giant_fiber_jump

    # 3. Subsequent static dark frame: threat has subsided, jump must cleanly reset
    t3 = brain.observe_frame(black, duration_ms=50.0)
    assert not t3.looming_threat_detected
    assert not t3.giant_fiber_jump, "giant_fiber_jump must reset to False when looming threat subsides"
