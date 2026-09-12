"""Integration test for the unified ConnectomeBrain engine."""

import numpy as np
import pytest
import scipy.sparse as sp

from connectome_engine.brain import ConnectomeBrain
from connectome_engine.data.circuits import IndexedCircuits


def test_connectome_brain_end_to_end_loop():
    """Verify that ConnectomeBrain processes an image frame and yields complete telemetry."""
    n_neurons = 100
    # Sparse random connected graph
    adj = sp.random(n_neurons, n_neurons, density=0.05, format="csr", dtype=np.float32)

    circuits = IndexedCircuits(
        r1_r6_photoreceptors=np.arange(0, 15, dtype=np.int32),
        r8_photoreceptors=np.arange(15, 25, dtype=np.int32),
        looming_threat_lc4=np.arange(25, 30, dtype=np.int32),
        pam11_dopamine_reward=np.arange(30, 35, dtype=np.int32),
        ppl101_dopamine_aversive=np.arange(35, 37, dtype=np.int32),
        octopamine_stress=np.arange(37, 42, dtype=np.int32),
        serotonin_calm=np.arange(42, 47, dtype=np.int32),
        kenyon_cells=np.arange(47, 60, dtype=np.int32),
        mbon07_reward_output=np.arange(60, 62, dtype=np.int32),
        mbon11_aversive_output=np.arange(62, 64, dtype=np.int32),
        epg_compass_neurons=np.arange(64, 80, dtype=np.int32),
        dna02_left=np.arange(80, 82, dtype=np.int32),
        dna02_right=np.arange(82, 84, dtype=np.int32),
        dnp09_forward=np.arange(84, 88, dtype=np.int32),
        mdn_moonwalker=np.arange(88, 90, dtype=np.int32),
        giant_fiber_escape=np.arange(90, 92, dtype=np.int32),
    )

    brain = ConnectomeBrain(n_neurons, adj, circuits)

    # Generate a sample 90x160 RGBA frame
    frame = np.random.randint(0, 256, size=(160, 90, 4), dtype=np.uint8)

    telemetry = brain.observe_frame(frame, duration_ms=50.0)

    # Verify all telemetry fields are computed and physically bounded
    assert telemetry.sim_time_ms == pytest.approx(50.0)
    assert telemetry.dopamine_conc_nm > 0.0
    assert telemetry.octopamine_conc_nm > 0.0
    assert telemetry.serotonin_conc_nm > 0.0
    assert 0.0 <= telemetry.forward_drive_pct <= 100.0
    assert -1.0 <= telemetry.steering_deflection <= 1.0
    assert 0.0 <= telemetry.compass_heading_deg < 360.0
    assert isinstance(telemetry.active_landmarks, list)
