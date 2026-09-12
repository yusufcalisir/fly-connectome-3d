"""Deterministic, zero-mock biophysical tests for LIF E/I dynamics and potassium reversal clamping."""

from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from connectome_engine.config import CONFIG, BiophysicalConstants
from connectome_engine.data.circuits import load_malecns_v1_connectome
from connectome_engine.simulation.lif_kernel import SpikingConnectomeEngine


def test_epsp_depolarization():
    """Verify that an excitatory presynaptic spike depolarizes the postsynaptic membrane."""
    n = 2
    # Neuron 0 is Excitatory, connected to Neuron 1 with positive weight (+5.0)
    weights = sp.csr_matrix(([5.0], ([0], [1])), shape=(n, n), dtype=np.float32)
    polarity = np.array([1, 1], dtype=np.int8)

    engine = SpikingConnectomeEngine(n, weights, CONFIG, polarity=polarity)
    v_rest = engine.v_rest

    # Pre-synaptic neuron 0 spikes
    engine.spikes[0] = True
    engine.step_substep()

    # Post-synaptic neuron 1 must have depolarized (voltage > v_rest)
    assert engine.v[1] > v_rest, f"Expected depolarization (v > {v_rest}), got {engine.v[1]}"


def test_ipsp_hyperpolarization():
    """Verify that an inhibitory presynaptic spike hyperpolarizes the postsynaptic membrane."""
    n = 2
    # Neuron 0 is Inhibitory, connected to Neuron 1 with negative weight (-5.0)
    weights = sp.csr_matrix(([-5.0], ([0], [1])), shape=(n, n), dtype=np.float32)
    polarity = np.array([-1, 1], dtype=np.int8)

    engine = SpikingConnectomeEngine(n, weights, CONFIG, polarity=polarity)
    v_rest = engine.v_rest

    # Pre-synaptic neuron 0 spikes
    engine.spikes[0] = True
    engine.step_substep()

    # Post-synaptic neuron 1 must have hyperpolarized (voltage < v_rest)
    assert engine.v[1] < v_rest, f"Expected hyperpolarization (v < {v_rest}), got {engine.v[1]}"


def test_potassium_reversal_clamp():
    """Verify that extreme inhibitory currents cannot drive voltage below E_K (-85.0 mV)."""
    n = 1
    weights = sp.csr_matrix((n, n), dtype=np.float32)
    cfg = BiophysicalConstants(v_lower_bound_mv=-85.0)
    engine = SpikingConnectomeEngine(n, weights, cfg)

    # Inject massive inhibitory current (-1000 pA) for 100 substeps
    engine.inject_current(np.array([0]), np.array([-1000.0], dtype=np.float32))

    for _ in range(100):
        engine.step_substep()

    # Must be clamped at exactly or above -85.0 mV
    assert engine.v[0] >= -85.0, f"Voltage dropped below reversal potential: {engine.v[0]}"
    assert np.isclose(engine.v[0], -85.0, atol=1e-3), f"Expected clamp at -85.0 mV, got {engine.v[0]}"


def test_vectorized_ei_spike_partition():
    """Verify that excitatory and inhibitory spikes are accurately partitioned in step_chunk."""
    n = 10
    # 6 Excitatory neurons (0..5), 4 Inhibitory neurons (6..9)
    polarity = np.array([1, 1, 1, 1, 1, 1, -1, -1, -1, -1], dtype=np.int8)
    weights = sp.csr_matrix((n, n), dtype=np.float32)
    engine = SpikingConnectomeEngine(n, weights, CONFIG, polarity=polarity)

    # Force depolarizing currents: drive 2 excitatory neurons and 1 inhibitory neuron past threshold
    currents = np.zeros(n, dtype=np.float32)
    currents[0] = 50.0  # Exc 0
    currents[1] = 50.0  # Exc 1
    currents[6] = 50.0  # Inh 6
    engine.inject_current(np.arange(n), currents)

    telemetry = engine.step_chunk(chunk_ms=50.0)

    # Sum of exc and inh spikes must strictly equal total_spikes
    assert telemetry.excitatory_spikes + telemetry.inhibitory_spikes == telemetry.total_spikes
    assert telemetry.excitatory_spikes > 0, "Excitatory spikes should have been detected"
    assert telemetry.inhibitory_spikes > 0, "Inhibitory spikes should have been detected"
    assert 0.0 <= telemetry.excitatory_ratio <= 1.0


def test_real_connectome_ei_clamping_and_counting():
    """Verify clamping and E/I counting on the full MaleCNS v1.0 connectome."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    graph_path = data_dir / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip(f"Connectome dataset not downloaded at {graph_path}")

    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)
    engine = SpikingConnectomeEngine(n_nodes, adj, CONFIG, polarity=circuits.polarity)

    # Step one chunk
    telemetry = engine.step_chunk(chunk_ms=50.0)

    # Minimum membrane voltage across all 166.7K neurons must respect E_K (-85 mV)
    assert telemetry.voltage_min_mv >= -85.001, f"Voltage min violated E_K: {telemetry.voltage_min_mv}"
    assert telemetry.excitatory_spikes + telemetry.inhibitory_spikes == telemetry.total_spikes
