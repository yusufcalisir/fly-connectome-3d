"""Comprehensive test suite verifying the official Janelia MaleCNS v1.0 166.7K connectome."""

import json
from pathlib import Path
import numpy as np
import scipy.sparse as sp
import pytest

from connectome_engine.data.circuits import load_malecns_v1_connectome
from connectome_engine.simulation.lif_kernel import SpikingConnectomeEngine
from connectome_engine.config import CONFIG


def test_malecns_v1_topology_integrity():
    """Verify exact 166,700 neuron count and 25,582,938 synaptic connections."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)

    assert n_nodes == 166700, f"Expected 166,700 neurons, got {n_nodes}"
    assert adj.shape == (166700, 166700), f"Expected shape (166700, 166700), got {adj.shape}"
    assert adj.nnz == 25582938, f"Expected 25,582,938 synapses, got {adj.nnz}"
    assert len(neuron_ids) == 166700

    # Verify key biological circuits
    assert len(circuits.pam11_dopamine_reward) == 15, "Expected 15 PAM11 dopamine cells"
    assert len(circuits.ppl101_dopamine_aversive) == 2, "Expected 2 PPL101 dopamine cells"
    assert len(circuits.kenyon_cells) > 3000, "Expected >3000 Kenyon cells"
    assert len(circuits.r1_r6_photoreceptors) > 3000, "Expected >3000 R1-R6 photoreceptors"
    assert len(circuits.r8_photoreceptors) > 1000, "Expected >1000 R8 photoreceptors"
    assert len(circuits.looming_threat_lc4) > 300, "Expected >300 LC4 looming threat cells"
    assert len(circuits.dna02_left) == 1, "Expected bilateral DNa02 Left"
    assert len(circuits.dna02_right) == 1, "Expected bilateral DNa02 Right"
    assert len(circuits.giant_fiber_escape) == 2, "Expected bilateral Giant Fiber cells"


def test_real_connectome_lif_dopamine_propagation():
    """Verify real LIF spike propagation through the 25.6M synaptic matrix upon PAM11 stimulation."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)

    engine = SpikingConnectomeEngine(n_nodes, adj, CONFIG)

    # Inject +20 mV into the 15 PAM11 cells
    engine.inject_current(circuits.pam11_dopamine_reward, 20.0)

    # Run 50 ms chunk
    telemetry = engine.step_chunk(50.0)

    assert telemetry.total_spikes > 0, "Expected real action potentials to be emitted"
    assert np.any(telemetry.spiking_neuron_indices), "Expected active spiking neurons"
