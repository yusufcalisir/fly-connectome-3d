"""Zero-mock, zero-random tests for 3D soma coordinates extraction and binary packaging.

Verifies:
1. Exact 141,781 soma extraction from Janelia MaleCNS annotations.feather.
2. True isotropic scaling and anatomical bounding boxes matching Three.js fly head.
3. Binary buffer layout, magic header, and byte-exact alignment.
4. Circuit classifications (Optic Lobe, Mushroom Body, Central Complex, Descending Motor).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "malecns_v1"
ANNOTATIONS_FILE = DATA_DIR / "annotations.feather"
BIN_FILE = DATA_DIR / "soma_coordinates_141k.bin"
METADATA_FILE = DATA_DIR / "soma_metadata.json"

MAGIC_NUMBER = 0x464C5933  # "FLY3"


@pytest.fixture(scope="module")
def annotations_df():
    assert ANNOTATIONS_FILE.exists(), f"Missing annotations file: {ANNOTATIONS_FILE}"
    return pd.read_feather(ANNOTATIONS_FILE)


@pytest.fixture(scope="module")
def metadata():
    assert METADATA_FILE.exists(), f"Missing metadata file: {METADATA_FILE}"
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_raw_soma_extraction_integrity(annotations_df, metadata):
    """Verify that all 141,781 somas are extracted from raw annotations without mock."""
    raw_soma_count = annotations_df["somaLocation"].notna().sum()
    assert raw_soma_count == 141781, f"Expected 141781 somas in raw data, got {raw_soma_count}"
    assert metadata["total_somas"] == 141781
    assert metadata["matched_in_graph"] == 139662

    # Verify bounds match raw EM data exactly
    somas = np.vstack(annotations_df["somaLocation"].dropna().values)
    assert not np.isnan(somas).any(), "Found NaN in raw soma coordinates"
    assert not np.isinf(somas).any(), "Found Inf in raw soma coordinates"

    np.testing.assert_allclose(somas.min(axis=0), metadata["em_bounds_min"])
    np.testing.assert_allclose(somas.max(axis=0), metadata["em_bounds_max"])


def test_isotropic_scaling_and_bounds(metadata):
    """Verify isotropic scaling preserves exact Euclidean distance ratios (zero distortion)."""
    em_min = np.array(metadata["em_bounds_min"])
    em_max = np.array(metadata["em_bounds_max"])
    em_span = em_max - em_min

    three_min = np.array(metadata["three_bounds_min"])
    three_max = np.array(metadata["three_bounds_max"])
    three_span = three_max - three_min

    scale = metadata["scale_factor"]
    assert scale > 0

    # Span in Three.js must equal span in EM multiplied by scale
    np.testing.assert_allclose(three_span, em_span * scale, rtol=1e-5)

    # Brain X width in Three.js must fit inside fly head width (<= 0.50)
    assert three_max[0] <= 0.25
    assert three_min[0] >= -0.25

    # Center must be origin for X axis (symmetric left-right)
    assert abs(three_max[0] + three_min[0]) < 1e-4


def test_binary_pack_alignment_and_read():
    """Verify binary file byte-level layout, header, and content unpack."""
    assert BIN_FILE.exists(), f"Missing binary file: {BIN_FILE}"
    file_bytes = BIN_FILE.read_bytes()

    total_somas = 141781
    expected_size = 16 + (total_somas * 12) + (total_somas * 1) + (total_somas * 1) + (total_somas * 4)
    assert len(file_bytes) == expected_size, f"Size mismatch: {len(file_bytes)} != {expected_size}"

    # Header
    magic, count = np.frombuffer(file_bytes[:8], dtype=np.uint32)
    assert magic == MAGIC_NUMBER, f"Bad magic number: {hex(magic)}"
    assert count == total_somas, f"Count mismatch: {count} != {total_somas}"

    scale = np.frombuffer(file_bytes[8:12], dtype=np.float32)[0]
    assert scale > 0

    offset = 16
    # Positions (141781 * 3 floats)
    pos_bytes = total_somas * 12
    positions = np.frombuffer(file_bytes[offset : offset + pos_bytes], dtype=np.float32).reshape(-1, 3)
    offset += pos_bytes
    assert positions.shape == (total_somas, 3)
    assert not np.isnan(positions).any()
    assert not np.isinf(positions).any()

    # Circuit tags (141781 uint8)
    circuit_bytes = total_somas
    circuits = np.frombuffer(file_bytes[offset : offset + circuit_bytes], dtype=np.uint8)
    offset += circuit_bytes
    assert circuits.shape == (total_somas,)
    assert set(np.unique(circuits)).issubset({0, 1, 2, 3, 4, 5})

    # Polarities (141781 int8)
    polarity_bytes = total_somas
    polarities = np.frombuffer(file_bytes[offset : offset + polarity_bytes], dtype=np.int8)
    offset += polarity_bytes
    assert polarities.shape == (total_somas,)
    assert set(np.unique(polarities)).issubset({-1, 0, 1})

    # Graph indices (141781 int32)
    graph_idx_bytes = total_somas * 4
    graph_indices = np.frombuffer(file_bytes[offset : offset + graph_idx_bytes], dtype=np.int32)
    offset += graph_idx_bytes
    assert offset == expected_size
    assert graph_indices.shape == (total_somas,)
    assert np.sum(graph_indices >= 0) == 139662


def test_circuit_tag_accuracy(annotations_df):
    """Verify circuit tags accurately identify key biological neural circuits."""
    df_soma = annotations_df[annotations_df["somaLocation"].notna()].reset_index(drop=True)

    file_bytes = BIN_FILE.read_bytes()
    offset = 16 + (len(df_soma) * 12)
    circuits = np.frombuffer(file_bytes[offset : offset + len(df_soma)], dtype=np.uint8)

    # 1. Kenyon Cells -> Tag 2 (mushroom_body)
    kc_mask = df_soma["type"].str.startswith("KC", na=False).values
    assert kc_mask.sum() > 3000
    assert np.all(circuits[kc_mask] == 2), "Some Kenyon cells were not tagged as mushroom_body"

    # 2. LC4 Looming Threat -> Tag 1 (optic_lobe)
    lc4_mask = df_soma["type"].str.contains("LC4", na=False).values
    assert lc4_mask.sum() > 200
    assert np.all(circuits[lc4_mask] == 1), "Some LC4 neurons were not tagged as optic_lobe"

    # 3. Giant Fiber -> Tag 4 (descending_motor)
    gf_mask = (df_soma["type"].str.contains("GF", na=False) | (df_soma["superclass"] == "descending_neuron")).values
    assert gf_mask.sum() > 1000
    assert np.all(circuits[gf_mask] == 4), "Some Giant Fiber / Descending neurons were not tagged as descending_motor"
