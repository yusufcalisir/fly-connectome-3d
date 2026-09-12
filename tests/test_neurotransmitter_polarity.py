"""Deterministic zero-mock tests for neurotransmitter polarity and E/I partition."""

from pathlib import Path

import numpy as np
import pytest

from connectome_engine.data.circuits import IndexedCircuits, load_malecns_v1_connectome


def _get_data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "malecns_v1"


def test_indexed_circuits_dataclass_backward_compatibility():
    """Verify IndexedCircuits can be instantiated with default polarity fields."""
    circuits = IndexedCircuits(
        r1_r6_photoreceptors=np.array([1, 2], dtype=np.int32),
        r8_photoreceptors=np.array([3], dtype=np.int32),
        looming_threat_lc4=np.array([4], dtype=np.int32),
        pam11_dopamine_reward=np.array([5], dtype=np.int32),
        ppl101_dopamine_aversive=np.array([6], dtype=np.int32),
        octopamine_stress=np.array([7], dtype=np.int32),
        serotonin_calm=np.array([8], dtype=np.int32),
        kenyon_cells=np.array([9], dtype=np.int32),
        mbon07_reward_output=np.array([10], dtype=np.int32),
        mbon11_aversive_output=np.array([11], dtype=np.int32),
        epg_compass_neurons=np.array([12], dtype=np.int32),
        dna02_left=np.array([13], dtype=np.int32),
        dna02_right=np.array([14], dtype=np.int32),
        dnp09_forward=np.array([15], dtype=np.int32),
        mdn_moonwalker=np.array([16], dtype=np.int32),
        giant_fiber_escape=np.array([17], dtype=np.int32),
    )
    assert hasattr(circuits, "excitatory_neurons")
    assert hasattr(circuits, "inhibitory_neurons")
    assert hasattr(circuits, "polarity")
    assert isinstance(circuits.excitatory_neurons, np.ndarray)
    assert isinstance(circuits.inhibitory_neurons, np.ndarray)
    assert len(circuits.excitatory_neurons) == 0
    assert len(circuits.inhibitory_neurons) == 0
    assert circuits.polarity is None


def test_malecns_v1_polarity_integrity():
    """Verify exact biological neurotransmitter polarity on official MaleCNS v1.0."""
    data_dir = _get_data_dir()
    graph_path = data_dir / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip(f"Connectome dataset not downloaded at {graph_path}")

    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)

    assert n_nodes == 166700
    assert circuits.polarity is not None
    assert circuits.polarity.shape == (166700,)

    # Polarity must only contain +1 (Excitatory) or -1 (Inhibitory)
    unique_polarities = np.unique(circuits.polarity)
    assert set(unique_polarities).issubset({-1, 1})

    # Exact biological counts (107,438 ACh/excitatory, 59,262 GABA/Glu/Histamine inhibitory)
    n_exc = len(circuits.excitatory_neurons)
    n_inh = len(circuits.inhibitory_neurons)
    assert n_exc == 107438, f"Expected 107,438 excitatory neurons, got {n_exc}"
    assert n_inh == 59262, f"Expected 59,262 inhibitory neurons, got {n_inh}"
    assert n_exc + n_inh == n_nodes

    # Mutual exclusivity: E and I sets must be strictly disjoint
    overlap = np.intersect1d(circuits.excitatory_neurons, circuits.inhibitory_neurons)
    assert len(overlap) == 0, f"Excitatory and inhibitory sets must be disjoint! Found overlap: {overlap}"


def test_known_circuits_biological_polarity():
    """Verify that identified circuits have biologically consistent neurotransmitter polarities."""
    data_dir = _get_data_dir()
    graph_path = data_dir / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip(f"Connectome dataset not downloaded at {graph_path}")

    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)
    pol = circuits.polarity

    # LC4 looming detectors: primarily cholinergic (excitatory)
    if len(circuits.looming_threat_lc4) > 0:
        lc4_pol = pol[circuits.looming_threat_lc4]
        # Vast majority of LC4 are excitatory (+1)
        assert np.mean(lc4_pol == 1) > 0.90, "LC4 neurons should be predominantly excitatory"

    # Kenyon Cells (Mushroom Body): predominantly cholinergic
    if len(circuits.kenyon_cells) > 0:
        kc_pol = pol[circuits.kenyon_cells]
        assert np.mean(kc_pol == 1) > 0.85, "Kenyon cells should be predominantly excitatory"

    # Photoreceptors R1-R6: insect photoreceptors use Histamine (inhibitory to laminar cells)
    if len(circuits.r1_r6_photoreceptors) > 0:
        r1_r6_pol = pol[circuits.r1_r6_photoreceptors]
        # Histaminergic cells are classified as -1 in our sign mapping
        assert np.mean(r1_r6_pol == -1) > 0.80, "R1-R6 photoreceptors should be predominantly histaminergic (-1)"
