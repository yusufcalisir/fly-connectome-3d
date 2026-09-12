"""Deterministic Unit Tests for VNC (Ventral Nerve Cord) Thoracic Leg Motor Pools.

Verifies the biological extraction and segmentation of the 381 pure leg motor neurons
across the 6 legs (T1L, T1R, T2L, T2R, T3L, T3R) from Janelia MaleCNS v1.0.
ZERO MOCK, ZERO RANDOM NUMBERS.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from connectome_engine.data.circuits import (
    IndexedCircuits,
    load_malecns_v1_connectome,
)


@pytest.fixture(scope="module")
def malecns_data():
    """Load real Janelia MaleCNS v1.0 connectome circuits and raw annotations."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    if not (data_dir / "malecns_v1_graph.npz").exists() or not (data_dir / "circuits_manifest.json").exists():
        pytest.skip("MaleCNS v1.0 dataset not found locally.")

    n_nodes, adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)
    ann_df = pd.read_feather(data_dir / "annotations.feather")
    return circuits, neuron_ids, ann_df


def test_vnc_leg_pools_disjoint_and_complete(malecns_data):
    """Verify that the 6 VNC leg motor pools are mutually disjoint and contain exactly 381 biological neurons."""
    circuits, neuron_ids, _ = malecns_data

    pools = [
        circuits.vnc_t1_left,
        circuits.vnc_t1_right,
        circuits.vnc_t2_left,
        circuits.vnc_t2_right,
        circuits.vnc_t3_left,
        circuits.vnc_t3_right,
    ]

    # Verify expected counts for each leg
    assert len(circuits.vnc_t1_left) == 68, f"Expected 68 T1L motor neurons, got {len(circuits.vnc_t1_left)}"
    assert len(circuits.vnc_t1_right) == 67, f"Expected 67 T1R motor neurons, got {len(circuits.vnc_t1_right)}"
    assert len(circuits.vnc_t2_left) == 58, f"Expected 58 T2L motor neurons, got {len(circuits.vnc_t2_left)}"
    assert len(circuits.vnc_t2_right) == 58, f"Expected 58 T2R motor neurons, got {len(circuits.vnc_t2_right)}"
    assert len(circuits.vnc_t3_left) == 66, f"Expected 66 T3L motor neurons, got {len(circuits.vnc_t3_left)}"
    assert len(circuits.vnc_t3_right) == 64, f"Expected 64 T3R motor neurons, got {len(circuits.vnc_t3_right)}"

    total_leg_motors = sum(len(p) for p in pools)
    assert total_leg_motors == 381, f"Expected 381 total biological leg motor neurons, got {total_leg_motors}"

    # Verify mutual disjointness across all 6 pools
    sets = [set(p) for p in pools]
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            overlap = sets[i].intersection(sets[j])
            assert len(overlap) == 0, f"Pools {i} and {j} overlap on nodes: {overlap}"


def test_vnc_leg_pools_neuromere_and_subclass_consistency(malecns_data):
    """Verify that all extracted leg motor neurons belong to superclass 'vnc_motor' and correct thoracic neuromeres."""
    circuits, neuron_ids, ann_df = malecns_data

    # Map graph indices to annotation records
    ann_aligned = ann_df.set_index("bodyId").reindex(neuron_ids)

    # 1. Front Legs (T1): subclass must be 'fl' and somaNeuromere must be 'T1'
    t1_nodes = np.concatenate([circuits.vnc_t1_left, circuits.vnc_t1_right])
    t1_records = ann_aligned.iloc[t1_nodes]
    assert (t1_records["superclass"] == "vnc_motor").all(), "All T1 leg neurons must have superclass 'vnc_motor'"
    assert (t1_records["subclass"] == "fl").all(), "All T1 leg neurons must have subclass 'fl'"
    assert (t1_records["somaNeuromere"] == "T1").all(), "All T1 leg neurons must have somaNeuromere 'T1'"

    # 2. Middle Legs (T2): subclass must be 'ml' and somaNeuromere must be 'T2'
    t2_nodes = np.concatenate([circuits.vnc_t2_left, circuits.vnc_t2_right])
    t2_records = ann_aligned.iloc[t2_nodes]
    assert (t2_records["superclass"] == "vnc_motor").all(), "All T2 leg neurons must have superclass 'vnc_motor'"
    assert (t2_records["subclass"] == "ml").all(), "All T2 leg neurons must have subclass 'ml'"
    assert (t2_records["somaNeuromere"] == "T2").all(), "All T2 leg neurons must have somaNeuromere 'T2'"

    # 3. Hind Legs (T3): subclass must be 'hl' and somaNeuromere must be 'T3'
    t3_nodes = np.concatenate([circuits.vnc_t3_left, circuits.vnc_t3_right])
    t3_records = ann_aligned.iloc[t3_nodes]
    assert (t3_records["superclass"] == "vnc_motor").all(), "All T3 leg neurons must have superclass 'vnc_motor'"
    assert (t3_records["subclass"] == "hl").all(), "All T3 leg neurons must have subclass 'hl'"
    assert (t3_records["somaNeuromere"] == "T3").all(), "All T3 leg neurons must have somaNeuromere 'T3'"

    # 4. Verify Left / Right sides
    side_series = ann_aligned["somaSide"].fillna(ann_aligned["rootSide"])
    assert (side_series.iloc[circuits.vnc_t1_left] == "L").all(), "T1L must be Left"
    assert (side_series.iloc[circuits.vnc_t1_right] == "R").all(), "T1R must be Right"
    assert (side_series.iloc[circuits.vnc_t2_left] == "L").all(), "T2L must be Left"
    assert (side_series.iloc[circuits.vnc_t2_right] == "R").all(), "T2R must be Right"
    assert (side_series.iloc[circuits.vnc_t3_left] == "L").all(), "T3L must be Left"
    assert (side_series.iloc[circuits.vnc_t3_right] == "R").all(), "T3R must be Right"


def test_vnc_leg_backward_compatibility():
    """Verify that IndexedCircuits initializes cleanly with default empty VNC leg motor pools."""
    dummy_c = IndexedCircuits(
        r1_r6_photoreceptors=np.array([1, 2, 3], dtype=np.int32),
        r8_photoreceptors=np.array([4, 5], dtype=np.int32),
        looming_threat_lc4=np.array([6], dtype=np.int32),
        pam11_dopamine_reward=np.array([7], dtype=np.int32),
        ppl101_dopamine_aversive=np.array([8], dtype=np.int32),
        octopamine_stress=np.array([9], dtype=np.int32),
        serotonin_calm=np.array([10], dtype=np.int32),
        kenyon_cells=np.array([11], dtype=np.int32),
        mbon07_reward_output=np.array([12], dtype=np.int32),
        mbon11_aversive_output=np.array([13], dtype=np.int32),
        epg_compass_neurons=np.array([14], dtype=np.int32),
        dna02_left=np.array([15], dtype=np.int32),
        dna02_right=np.array([16], dtype=np.int32),
        dnp09_forward=np.array([17], dtype=np.int32),
        mdn_moonwalker=np.array([18], dtype=np.int32),
        giant_fiber_escape=np.array([19], dtype=np.int32),
    )

    # VNC fields must be empty int32 arrays by default
    assert isinstance(dummy_c.vnc_t1_left, np.ndarray)
    assert len(dummy_c.vnc_t1_left) == 0
    assert len(dummy_c.vnc_t1_right) == 0
    assert len(dummy_c.vnc_t2_left) == 0
    assert len(dummy_c.vnc_t2_right) == 0
    assert len(dummy_c.vnc_t3_left) == 0
    assert len(dummy_c.vnc_t3_right) == 0
