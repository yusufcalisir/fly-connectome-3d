"""Compiler script for real 3D soma coordinates from Janelia MaleCNS v1.0.

Extracts 141,781 real neuron soma coordinates from annotations.feather,
isotropically normalizes them into Three.js anatomical space, assigns circuit
functional groups and Dale polarity, and packages them into high-performance
binary format.

Zero-mock, zero-random: 100% biological data grounded in EM tracings.
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("compile_coordinates")

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "malecns_v1"
ANNOTATIONS_FILE = DATA_DIR / "annotations.feather"
GRAPH_FILE = DATA_DIR / "malecns_v1_graph.npz"

OUTPUT_BIN = DATA_DIR / "soma_coordinates_141k.bin"
OUTPUT_METADATA = DATA_DIR / "soma_metadata.json"

MAGIC_NUMBER = 0x464C5933  # "FLY3" in ASCII

# Circuit functional categories (uint8)
CIRCUIT_TAGS = {
    "central_brain": 0,
    "optic_lobe": 1,
    "mushroom_body": 2,
    "central_complex": 3,
    "descending_motor": 4,
    "vnc_motor_cord": 5,
}

CIRCUIT_COLORS_HEX = {
    "central_brain": "#38bdf8",     # Translucent Bioluminescent Blue
    "optic_lobe": "#00f0ff",        # High-energy Cyan
    "mushroom_body": "#10b981",     # Emerald Green (Kenyon cells)
    "central_complex": "#f59e0b",   # Amber / Gold (Heading compass)
    "descending_motor": "#ef4444",  # Fiery Coral / Red (Giant Fiber)
    "vnc_motor_cord": "#a855f7",    # Electric Purple / Thoracic cord
}


@dataclass
class SomaMetadata:
    total_somas: int
    matched_in_graph: int
    em_bounds_min: list
    em_bounds_max: list
    em_center: list
    scale_factor: float
    three_bounds_min: list
    three_bounds_max: list
    circuit_counts: Dict[str, int]
    polarity_counts: Dict[str, int]
    circuit_colors: Dict[str, str]


def classify_soma_circuit(row: pd.Series) -> int:
    """Classify a neuron into one of 6 anatomical circuit categories based on superclass and type."""
    superclass = str(row.get("superclass", "") or "")
    ntype = str(row.get("type", "") or "")

    # 1. Mushroom Body (Kenyon cells & MBONs)
    if ntype.startswith("KC") or "MBON" in ntype or ntype in ("APL", "DPM"):
        return CIRCUIT_TAGS["mushroom_body"]

    # 2. Central Complex (EPG, PEG, PEN, etc.)
    if any(k in ntype for k in ["EPG", "PEG", "PEN", "P-EN", "Delta", "FB", "EB", "PB", "NO"]):
        return CIRCUIT_TAGS["central_complex"]

    # 3. Descending Motor & Giant Fiber
    if superclass == "descending_neuron" or "GF" in ntype or "DNa" in ntype or "DNp" in ntype:
        return CIRCUIT_TAGS["descending_motor"]

    # 4. Optic Lobe (Intrinsic, Projection, Centrifugal, Sensory)
    if "ol_" in superclass or "visual_" in superclass or "LC" in ntype or "LPLC" in ntype:
        return CIRCUIT_TAGS["optic_lobe"]

    # 5. Ventral Nerve Cord (Thoracic & Abdominal)
    if "vnc_" in superclass or superclass in ("ascending_neuron", "sensory_ascending", "efferent_ascending"):
        return CIRCUIT_TAGS["vnc_motor_cord"]

    # 6. Default: Central Brain Intrinsic
    return CIRCUIT_TAGS["central_brain"]


def extract_and_compile_coordinates() -> Tuple[Path, Path]:
    """Extract, align, package and write real soma coordinates."""
    if not ANNOTATIONS_FILE.exists():
        raise FileNotFoundError(f"Annotations file not found: {ANNOTATIONS_FILE}")
    if not GRAPH_FILE.exists():
        raise FileNotFoundError(f"Graph file not found: {GRAPH_FILE}")

    logger.info("Loading annotations from %s...", ANNOTATIONS_FILE)
    df = pd.read_feather(ANNOTATIONS_FILE)

    # Filter non-null soma locations
    df_soma = df[df["somaLocation"].notna()].copy()
    total_somas = len(df_soma)
    logger.info("Total somas with non-null coordinates: %d", total_somas)

    # Stack raw EM coordinates: shape (N, 3)
    em_coords = np.vstack(df_soma["somaLocation"].values).astype(np.float64)

    # Load graph neuron_ids and polarity
    logger.info("Loading graph from %s...", GRAPH_FILE)
    graph = np.load(GRAPH_FILE, allow_pickle=True)
    graph_neuron_ids = graph["neuron_ids"]
    graph_polarity = graph.get("polarity", None)

    # Create mapping bodyId -> graph_index
    body_id_to_graph_idx = {int(bid): idx for idx, bid in enumerate(graph_neuron_ids)}

    body_ids = df_soma["bodyId"].astype(np.int64).values
    graph_indices = np.full(total_somas, -1, dtype=np.int32)
    polarities = np.zeros(total_somas, dtype=np.int8)

    matched_count = 0
    for i, bid in enumerate(body_ids):
        g_idx = body_id_to_graph_idx.get(bid, -1)
        if g_idx >= 0:
            graph_indices[i] = g_idx
            matched_count += 1
            if graph_polarity is not None:
                polarities[i] = int(graph_polarity[g_idx])

    logger.info("Matched %d / %d somas to active simulation graph.", matched_count, total_somas)

    # Calculate anatomical center & isotropic scaling
    # Brain somas (Z < 50,000) determine the cranial head fit
    brain_mask = em_coords[:, 2] < 50000.0
    brain_coords = em_coords[brain_mask]

    c_x = (brain_coords[:, 0].min() + brain_coords[:, 0].max()) / 2.0
    c_y = (brain_coords[:, 1].min() + brain_coords[:, 1].max()) / 2.0
    c_z = (brain_coords[:, 2].min() + brain_coords[:, 2].max()) / 2.0
    em_center = np.array([c_x, c_y, c_z], dtype=np.float64)

    # Brain mediolateral width span
    span_x = brain_coords[:, 0].max() - brain_coords[:, 0].min()
    target_brain_width = 0.44  # Fits comfortably in 0.52 head width (eye spacing 0.42)
    scale_factor = target_brain_width / span_x
    logger.info("EM Center: %s, Span X: %.1f, Isotropic Scale: %e", em_center, span_x, scale_factor)

    # Transform all somas into Three.js coordinates
    # In Three.js: +X is Right (-X Left), +Y is Dorsal/Up, +Z is Anterior/Eyes (-Z Posterior/VNC)
    three_x = -(em_coords[:, 0] - c_x) * scale_factor
    three_y = -(em_coords[:, 1] - c_y) * scale_factor
    three_z = -(em_coords[:, 2] - c_z) * scale_factor

    three_positions = np.column_stack([three_x, three_y, three_z]).astype(np.float32)

    # Classify circuit tags
    logger.info("Classifying circuit functional categories...")
    circuit_tags = np.array([classify_soma_circuit(row) for _, row in df_soma.iterrows()], dtype=np.uint8)

    # Calculate counts
    tag_to_name = {v: k for k, v in CIRCUIT_TAGS.items()}
    circuit_counts = {}
    for tag_val, name in tag_to_name.items():
        circuit_counts[name] = int(np.sum(circuit_tags == tag_val))

    polarity_counts = {
        "excitatory": int(np.sum(polarities == 1)),
        "inhibitory": int(np.sum(polarities == -1)),
        "unknown": int(np.sum(polarities == 0)),
    }

    logger.info("Circuit counts: %s", circuit_counts)
    logger.info("Polarity counts: %s", polarity_counts)

    # Binary packaging
    logger.info("Packaging into binary format at %s...", OUTPUT_BIN)
    with open(OUTPUT_BIN, "wb") as f:
        # Header (16 bytes)
        # 4 bytes magic, 4 bytes count, 4 bytes scale (float32), 4 bytes reserved
        header = np.array([MAGIC_NUMBER, total_somas], dtype=np.uint32).tobytes()
        f.write(header)
        f.write(np.float32(scale_factor).tobytes())
        f.write(np.uint32(0).tobytes())  # reserved

        # Section 1: Positions (Float32, shape N*3)
        f.write(three_positions.tobytes())

        # Section 2: Circuit tags (Uint8, shape N)
        f.write(circuit_tags.tobytes())

        # Section 3: Polarities (Int8, shape N)
        f.write(polarities.tobytes())

        # Section 4: Graph node indices (Int32, shape N)
        f.write(graph_indices.tobytes())

    file_size = OUTPUT_BIN.stat().st_size
    expected_size = 16 + (total_somas * 12) + (total_somas * 1) + (total_somas * 1) + (total_somas * 4)
    logger.info("Wrote binary file: %d bytes (expected %d bytes)", file_size, expected_size)
    assert file_size == expected_size, f"Binary size mismatch: {file_size} != {expected_size}"

    # Metadata JSON
    metadata = SomaMetadata(
        total_somas=total_somas,
        matched_in_graph=matched_count,
        em_bounds_min=[float(v) for v in em_coords.min(axis=0)],
        em_bounds_max=[float(v) for v in em_coords.max(axis=0)],
        em_center=[float(v) for v in em_center],
        scale_factor=float(scale_factor),
        three_bounds_min=[float(v) for v in three_positions.min(axis=0)],
        three_bounds_max=[float(v) for v in three_positions.max(axis=0)],
        circuit_counts=circuit_counts,
        polarity_counts=polarity_counts,
        circuit_colors=CIRCUIT_COLORS_HEX,
    )

    with open(OUTPUT_METADATA, "w", encoding="utf-8") as f:
        json.dump(asdict(metadata), f, indent=2)

    logger.info("Wrote metadata to %s.", OUTPUT_METADATA)
    return OUTPUT_BIN, OUTPUT_METADATA


if __name__ == "__main__":
    extract_and_compile_coordinates()
