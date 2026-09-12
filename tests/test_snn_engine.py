"""Unit tests for biophysical Leaky Integrate-and-Fire simulation engine."""

import numpy as np
import scipy.sparse as sp

from connectome_engine.config import CONFIG
from connectome_engine.simulation.lif_kernel import SpikingConnectomeEngine


def test_subthreshold_membrane_decay():
    """Verify that membrane potential decays exponentially toward V_rest."""
    num_neurons = 10
    weights = sp.csr_matrix((num_neurons, num_neurons), dtype=np.float32)
    engine = SpikingConnectomeEngine(num_neurons, weights)

    # Set initial voltage elevated above V_rest
    initial_v = -55.0  # below V_thresh (-50 mV)
    engine.v.fill(initial_v)

    # Step for tau_m (20 ms = 200 substeps of 0.1 ms)
    steps = int(round(CONFIG.tau_m_ms / CONFIG.dt_ms))
    for _ in range(steps):
        engine.step_substep()

    # Analytical expectation: V(t) = V_rest + (V0 - V_rest) * e^(-1)
    expected_v = CONFIG.v_rest_mv + (initial_v - CONFIG.v_rest_mv) * np.exp(-1.0)
    np.testing.assert_allclose(engine.v, expected_v, atol=0.2)


def test_action_potential_generation_and_refractory():
    """Verify threshold crossing generates spikes and enters refractory period."""
    num_neurons = 5
    weights = sp.csr_matrix((num_neurons, num_neurons), dtype=np.float32)
    engine = SpikingConnectomeEngine(num_neurons, weights)

    # Inject strong current to trigger action potentials
    engine.inject_current(np.arange(num_neurons), np.full(num_neurons, 15.0, dtype=np.float32))

    # Run one 50 ms chunk
    telemetry = engine.step_chunk(chunk_ms=50.0)

    assert telemetry.total_spikes > 0
    assert telemetry.mean_firing_rate_hz > 0.0
    # Membrane potential should be within physical limits
    assert telemetry.voltage_min_mv >= CONFIG.v_reset_mv - 1.0
    assert telemetry.voltage_max_mv <= CONFIG.v_thresh_mv + 5.0


def test_checkpoint_save_and_restore():
    """Verify state checkpointing preserves continuous biophysical states."""
    num_neurons = 20
    weights = sp.csr_matrix((num_neurons, num_neurons), dtype=np.float32)
    engine = SpikingConnectomeEngine(num_neurons, weights)

    engine.inject_current(np.array([0, 1]), np.array([10.0, 10.0], dtype=np.float32))
    engine.step_chunk(chunk_ms=25.0)

    checkpoint = engine.save_checkpoint()

    # Create fresh engine and restore
    new_engine = SpikingConnectomeEngine(num_neurons, weights)
    new_engine.load_checkpoint(checkpoint)

    np.testing.assert_allclose(new_engine.v, engine.v)
    np.testing.assert_array_equal(new_engine.refractory_steps, engine.refractory_steps)
    assert new_engine.total_sim_ms == engine.total_sim_ms
