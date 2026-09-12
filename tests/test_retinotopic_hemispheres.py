"""Deterministic tests for biological retinal hemispheric partitioning.

Zero mock, zero random numbers. Validates exact connectome annotations and circuit extraction.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from connectome_engine.data.circuits import (
    IndexedCircuits,
    extract_circuits_from_annotations,
    load_malecns_v1_connectome,
)


def test_indexed_circuits_hemispheric_fields():
    """Verify IndexedCircuits dataclass fields, defaults, and deterministic post-init."""
    flat_r16 = np.array([10, 20, 30, 40], dtype=np.int32)
    flat_r8 = np.array([1, 2], dtype=np.int32)

    circuits = IndexedCircuits(
        r1_r6_photoreceptors=flat_r16,
        r8_photoreceptors=flat_r8,
        looming_threat_lc4=np.empty(0, dtype=np.int32),
        pam11_dopamine_reward=np.empty(0, dtype=np.int32),
        ppl101_dopamine_aversive=np.empty(0, dtype=np.int32),
        octopamine_stress=np.empty(0, dtype=np.int32),
        serotonin_calm=np.empty(0, dtype=np.int32),
        kenyon_cells=np.empty(0, dtype=np.int32),
        mbon07_reward_output=np.empty(0, dtype=np.int32),
        mbon11_aversive_output=np.empty(0, dtype=np.int32),
        epg_compass_neurons=np.empty(0, dtype=np.int32),
        dna02_left=np.array([100], dtype=np.int32),
        dna02_right=np.array([200], dtype=np.int32),
        dnp09_forward=np.empty(0, dtype=np.int32),
        mdn_moonwalker=np.empty(0, dtype=np.int32),
        giant_fiber_escape=np.empty(0, dtype=np.int32),
    )

    # Automatic fallback partitioning splits flat arrays evenly
    assert len(circuits.r1_r6_left) == 2
    assert len(circuits.r1_r6_right) == 2
    assert np.array_equal(circuits.r1_r6_left, np.array([10, 20]))
    assert np.array_equal(circuits.r1_r6_right, np.array([30, 40]))
    assert np.array_equal(circuits.r8_left, np.array([1]))
    assert np.array_equal(circuits.r8_right, np.array([2]))


def test_extract_circuits_synthetic_partitioning():
    """Verify deterministic separation of left vs right hemiretina on deterministic annotations."""
    df = pd.DataFrame(
        {
            "bodyId": [101, 102, 103, 104, 105, 106, 107, 108],
            "type": ["R1-R6", "R1-R6", "R1-R6", "R8a", "R8b", "DNa02", "DNa02", "DNp09"],
            "somaSide": ["L", "R", None, "L", "R", "L", "R", "R"],
            "rootSide": [None, None, "R", None, None, None, None, None],
        }
    )
    ids = np.array([101, 102, 103, 104, 105, 106, 107, 108])

    circuits = extract_circuits_from_annotations(df, ids)

    # R1-R6 (101: L, 102: R, 103: rootSide R)
    assert np.array_equal(circuits.r1_r6_left, np.array([0]))       # index of 101
    assert np.array_equal(circuits.r1_r6_right, np.array([1, 2]))    # indices of 102, 103
    assert len(circuits.r1_r6_photoreceptors) == 3

    # R8 (104: L, 105: R)
    assert np.array_equal(circuits.r8_left, np.array([3]))           # index of 104
    assert np.array_equal(circuits.r8_right, np.array([4]))          # index of 105

    # DNa02 (106: L, 107: R)
    assert np.array_equal(circuits.dna02_left, np.array([5]))
    assert np.array_equal(circuits.dna02_right, np.array([6]))

    # Disjointness check
    assert np.intersect1d(circuits.r1_r6_left, circuits.r1_r6_right).size == 0
    assert np.intersect1d(circuits.r8_left, circuits.r8_right).size == 0
    assert np.intersect1d(circuits.dna02_left, circuits.dna02_right).size == 0


def test_malecns_v1_ground_truth_hemispheres():
    """Verify exact real connectome biological counts from Janelia MaleCNS v1.0."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "malecns_v1"
    graph_path = data_dir / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip("MaleCNS v1.0 dataset not found locally.")
    num_nodes, _adj, circuits, neuron_ids = load_malecns_v1_connectome(data_dir)

    assert num_nodes == 166700
    assert len(neuron_ids) == 166700

    # R1-R6 Outer Photoreceptors
    assert len(circuits.r1_r6_left) == 1112, f"Expected 1112 left R1-R6, got {len(circuits.r1_r6_left)}"
    assert len(circuits.r1_r6_right) == 2265, f"Expected 2265 right R1-R6, got {len(circuits.r1_r6_right)}"
    assert len(circuits.r1_r6_photoreceptors) == 3377
    assert np.intersect1d(circuits.r1_r6_left, circuits.r1_r6_right).size == 0

    # R8 Inner Chromatic Photoreceptors
    assert len(circuits.r8_left) == 625, f"Expected 625 left R8, got {len(circuits.r8_left)}"
    assert len(circuits.r8_right) == 704, f"Expected 704 right R8, got {len(circuits.r8_right)}"
    assert len(circuits.r8_photoreceptors) == 1329
    assert np.intersect1d(circuits.r8_left, circuits.r8_right).size == 0

    # Descending Steering Neurons DNa02
    assert len(circuits.dna02_left) == 1
    assert len(circuits.dna02_right) == 1
    assert circuits.dna02_left[0] == 131957
    assert circuits.dna02_right[0] == 332
    assert circuits.dna02_left[0] != circuits.dna02_right[0]
