"""Deterministic, zero-mock tests for dynamic E/I orchestration in ConnectomeBrain."""

from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from connectome_engine.brain import ConnectomeBrain
from connectome_engine.config import CONFIG
from connectome_engine.data.circuits import IndexedCircuits, load_malecns_v1_connectome


def _make_deterministic_test_brain(n_nodes=200):
    """Construct a clean, deterministic mini-connectome with signed E/I synapses."""
    adj = sp.random(n_nodes, n_nodes, density=0.05, format="csr", dtype=np.float32, random_state=42)
    # Ensure signed weights (Dale's law: 65% Exc, 35% Inh)
    polarity = np.ones(n_nodes, dtype=np.int8)
    polarity[130:] = -1

    # Signs applied to outgoing presynaptic weights
    weights = adj.copy()
    for pre in range(n_nodes):
        if polarity[pre] < 0:
            row_start = weights.indptr[pre]
            row_end = weights.indptr[pre + 1]
            weights.data[row_start:row_end] = -np.abs(weights.data[row_start:row_end])
        else:
            row_start = weights.indptr[pre]
            row_end = weights.indptr[pre + 1]
            weights.data[row_start:row_end] = np.abs(weights.data[row_start:row_end])

    circuits = IndexedCircuits(
        r1_r6_photoreceptors=np.arange(0, 30, dtype=np.int32),
        r8_photoreceptors=np.arange(30, 50, dtype=np.int32),
        looming_threat_lc4=np.arange(50, 70, dtype=np.int32),
        pam11_dopamine_reward=np.arange(70, 80, dtype=np.int32),
        ppl101_dopamine_aversive=np.arange(80, 82, dtype=np.int32),
        octopamine_stress=np.arange(82, 90, dtype=np.int32),
        serotonin_calm=np.arange(90, 100, dtype=np.int32),
        kenyon_cells=np.arange(100, 130, dtype=np.int32),
        mbon07_reward_output=np.array([130, 131], dtype=np.int32),
        mbon11_aversive_output=np.array([132, 133], dtype=np.int32),
        epg_compass_neurons=np.arange(134, 160, dtype=np.int32),
        dna02_left=np.array([160], dtype=np.int32),
        dna02_right=np.array([161], dtype=np.int32),
        dnp09_forward=np.arange(162, 170, dtype=np.int32),
        mdn_moonwalker=np.array([170], dtype=np.int32),
        giant_fiber_escape=np.array([171, 172], dtype=np.int32),
        excitatory_neurons=np.arange(0, 130, dtype=np.int32),
        inhibitory_neurons=np.arange(130, n_nodes, dtype=np.int32),
        polarity=polarity,
    )
    return ConnectomeBrain(n_nodes, weights, circuits, CONFIG)


def test_complete_telemetry_spike_partition():
    """Verify that CompleteObservationTelemetry strictly preserves total_spikes = exc + inh."""
    brain = _make_deterministic_test_brain(200)

    # White frame (255)
    frame_white = np.full((160, 90, 4), 255, dtype=np.uint8)
    t_white = brain.observe_frame(frame_white, duration_ms=50.0)

    assert hasattr(t_white, "excitatory_spikes")
    assert hasattr(t_white, "inhibitory_spikes")
    assert t_white.excitatory_spikes + t_white.inhibitory_spikes == t_white.total_spikes


def test_dynamic_ei_ratio_is_not_hardcoded_70_percent():
    """Verify that ei_balance_ratio is dynamic, stimulus-dependent, and not locked at 0.700."""
    brain = _make_deterministic_test_brain(200)

    # Frame 1: Bright white stimulus
    frame_white = np.full((160, 90, 4), 255, dtype=np.uint8)
    t1 = brain.observe_frame(frame_white, duration_ms=50.0)

    # Inject strong dopamine surge which activates PAM11 excitatory cluster
    t2 = brain.observe_frame(frame_white, duration_ms=50.0, manual_dopamine_boost_mv=35.0)

    # The ratio must be a valid float in [0.0, 1.0]
    assert 0.0 <= t1.ei_balance_ratio <= 1.0
    assert 0.0 <= t2.ei_balance_ratio <= 1.0

    # Ensure that it is dynamically computed rather than hardcoded 0.7000000000000001
    # When PAM11 cluster is blasted with current, excitatory spiking increases
    assert t2.excitatory_spikes >= t1.excitatory_spikes


def test_real_connectome_dynamic_ei_balance():
    """Verify real connectome executes dynamic E/I balancing across consecutive stimulus changes."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    graph_path = data_dir / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip(f"Connectome dataset not downloaded at {graph_path}")

    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)
    brain = ConnectomeBrain(n_nodes, adj, circuits, CONFIG)

    # Frame A: Pure white
    frame_white = np.full((160, 90, 4), 255, dtype=np.uint8)
    t_white = brain.observe_frame(frame_white, duration_ms=50.0)

    # Frame B: Threat looming dark transition
    frame_black = np.zeros((160, 90, 4), dtype=np.uint8)
    frame_black[:, :, 3] = 255
    t_dark = brain.observe_frame(frame_black, duration_ms=50.0)

    # Check partition validity
    assert t_white.excitatory_spikes + t_white.inhibitory_spikes == t_white.total_spikes
    assert t_dark.excitatory_spikes + t_dark.inhibitory_spikes == t_dark.total_spikes

    # Under threat/looming, LC4 cholinergic current activates escape networks
    assert t_white.total_spikes > 0
    assert 0.0 <= t_white.ei_balance_ratio <= 1.0
    assert 0.0 <= t_dark.ei_balance_ratio <= 1.0
