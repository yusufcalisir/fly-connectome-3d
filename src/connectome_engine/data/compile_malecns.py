"""Official MaleCNS v1.0 (166,700 Neurons, 25.6M Synapses) Graph Compiler.

Compiles the downloaded Janelia MaleCNS v1.0 feather files into a high-performance
sparse CSR graph and exact biological circuit index map.
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from pyarrow import feather

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "malecns_v1"
OUTPUT_NPZ = DATA_DIR / "malecns_v1_graph.npz"
CIRCUITS_JSON = DATA_DIR / "circuits_manifest.json"


def exact_ids(values) -> np.ndarray:
    """Ensure exact uint64 integer IDs without loss of precision."""
    items = np.asarray(values)
    if items.dtype.kind == "f":
        raise ValueError("Neuron IDs cannot be floats.")
    return items.astype(np.uint64)


def transmitter_signs(neurotransmitters: pd.Series) -> np.ndarray:
    """Map biological neurotransmitter annotations to synaptic signs.

    Biological rules from Janelia / FlyWire:
    - Acetylcholine (ACh): Excitatory (+1.0)
    - GABA: Fast inhibitory (-1.0)
    - Glutamate: Inhibitory in insect motor/CNS via GluCl channels (-1.0)
    - Histamine: Inhibitory in insect visual system (-1.0)
    - Others / unpredicted: Defaults to excitatory (+1.0)
    """
    cleaned = neurotransmitters.fillna("").str.lower().to_numpy()
    signs = np.ones(len(cleaned), dtype=np.float32)
    for i, t in enumerate(cleaned):
        if "gaba" in t or "glutamate" in t or "histamine" in t:
            signs[i] = -1.0
        elif "acetylcholine" in t or "ach" in t:
            signs[i] = 1.0
        else:
            signs[i] = 1.0
    return signs


def compile_connectome():
    print("=" * 70)
    print("COMPILING OFFICIAL JANELIA MCNS v1.0 CONNECTOME GRAPH")
    print("=" * 70)
    start_total = time.time()

    # 1. Load and filter annotations (166,700 neurons)
    print("\n[1/4] Loading annotations.feather...")
    ann_path = DATA_DIR / "annotations.feather"
    if not ann_path.exists():
        raise FileNotFoundError(f"Missing {ann_path}")
    ann_df = feather.read_table(ann_path).to_pandas()
    print(f"      Total objects in raw annotation file: {len(ann_df):,}")

    # Retain neurons according to standard Janelia MaleCNS criteria (exclude Glia and empty superclass)
    retain_mask = (
        ann_df.superclass.notna()
        & ann_df.superclass.astype(str).ne("")
        & (~ann_df.status.eq("Glia"))
    )
    nodes_df = ann_df.loc[retain_mask].copy().sort_values("bodyId").reset_index(drop=True)
    num_nodes = len(nodes_df)
    print(f"      Retained biological neurons: {num_nodes:,} (Exact MCNS v1.0 standard)")
    assert num_nodes == 166700, f"Expected 166,700 neurons, got {num_nodes}"

    neuron_ids = exact_ids(nodes_df.bodyId.to_numpy())

    # 2. Map consensus neurotransmitters
    print("\n[2/4] Mapping neurotransmitter identities...")
    nt_path = DATA_DIR / "neurotransmitters.feather"
    nt_df = feather.read_table(nt_path).to_pandas().set_index("body")
    consensus_nt = nodes_df.bodyId.map(nt_df.consensus_nt).fillna("unknown")
    signs = transmitter_signs(consensus_nt)
    print(f"      Mapped {len(signs):,} neuron transmitter signs (Excitatory: {np.count_nonzero(signs > 0):,}, Inhibitory: {np.count_nonzero(signs < 0):,})")

    # 3. Process edges and build sparse graph
    print("\n[3/4] Processing edges.feather (synaptic connections)...")
    edges_path = DATA_DIR / "edges.feather"
    edges_table = feather.read_table(edges_path, columns=["body_pre", "body_post", "weight"])
    pre_raw = exact_ids(edges_table.column("body_pre").to_numpy())
    post_raw = exact_ids(edges_table.column("body_post").to_numpy())
    weight_raw = edges_table.column("weight").to_numpy().astype(np.float32)
    print(f"      Total candidate edge entries in file: {len(pre_raw):,}")

    # Binary search to index edges within retained neurons
    print("      Indexing edges against 166,700 retained neurons...")
    idx_pre = np.searchsorted(neuron_ids, pre_raw)
    idx_post = np.searchsorted(neuron_ids, post_raw)

    valid_mask = (
        (idx_pre < num_nodes)
        & (idx_post < num_nodes)
        & (neuron_ids[np.minimum(idx_pre, num_nodes - 1)] == pre_raw)
        & (neuron_ids[np.minimum(idx_post, num_nodes - 1)] == post_raw)
    )

    retained_pre = idx_pre[valid_mask].astype(np.int32)
    retained_post = idx_post[valid_mask].astype(np.int32)
    retained_weights = weight_raw[valid_mask] * signs[retained_pre]

    num_retained_edges = len(retained_pre)
    print(f"      Retained directed synaptic edges: {num_retained_edges:,}")

    # Build Sparse CSR matrix
    print("      Building Compressed Sparse Row (CSR) matrix...")
    adj_matrix = sp.csr_matrix(
        (retained_weights, (retained_pre, retained_post)),
        shape=(num_nodes, num_nodes),
        dtype=np.float32,
    )

    # 4. Extract verified biological circuit indices
    print("\n[4/4] Extracting identified cell-type circuits...")
    types = nodes_df["type"].fillna("").astype(str)
    soma_side = (
        nodes_df.get("somaSide", pd.Series("", index=nodes_df.index))
        .fillna(nodes_df.get("rootSide", pd.Series("", index=nodes_df.index)))
        .fillna("")
        .astype(str)
    )

    subclass = (
        nodes_df.get("subclass", pd.Series("", index=nodes_df.index))
        .fillna("")
        .astype(str)
    )
    superclass = (
        nodes_df.get("superclass", pd.Series("", index=nodes_df.index))
        .fillna("")
        .astype(str)
    )
    is_leg_motor = superclass.eq("vnc_motor")

    r1_r6_l = np.flatnonzero(types.eq("R1-R6") & soma_side.eq("L")).tolist()
    r1_r6_r = np.flatnonzero(types.eq("R1-R6") & soma_side.eq("R")).tolist()
    r8_l = np.flatnonzero(types.str.startswith("R8") & soma_side.eq("L")).tolist()
    r8_r = np.flatnonzero(types.str.startswith("R8") & soma_side.eq("R")).tolist()

    vnc_t1_l = np.flatnonzero(is_leg_motor & subclass.eq("fl") & soma_side.eq("L")).tolist()
    vnc_t1_r = np.flatnonzero(is_leg_motor & subclass.eq("fl") & soma_side.eq("R")).tolist()
    vnc_t2_l = np.flatnonzero(is_leg_motor & subclass.eq("ml") & soma_side.eq("L")).tolist()
    vnc_t2_r = np.flatnonzero(is_leg_motor & subclass.eq("ml") & soma_side.eq("R")).tolist()
    vnc_t3_l = np.flatnonzero(is_leg_motor & subclass.eq("hl") & soma_side.eq("L")).tolist()
    vnc_t3_r = np.flatnonzero(is_leg_motor & subclass.eq("hl") & soma_side.eq("R")).tolist()

    circuits = {
        "r1_r6_photoreceptors": np.flatnonzero(types.eq("R1-R6")).tolist(),
        "r1_r6_left": r1_r6_l,
        "r1_r6_right": r1_r6_r,
        "r8_photoreceptors": np.flatnonzero(types.str.startswith("R8")).tolist(),
        "r8_left": r8_l,
        "r8_right": r8_r,
        "looming_threat_lc4": np.flatnonzero(types.str.startswith("LC4") | types.str.startswith("LPLC2")).tolist(),
        "pam11_dopamine_reward": np.flatnonzero(types.eq("PAM11")).tolist(),
        "ppl101_dopamine_aversive": np.flatnonzero(types.eq("PPL101")).tolist(),
        "octopamine_stress": np.flatnonzero(types.str.contains("TDC2") | types.str.contains("VUM") | types.str.startswith("OA-")).tolist(),
        "serotonin_calm": np.flatnonzero(types.str.contains("5-HT") | types.str.startswith("CSD") | types.str.startswith("5HT-")).tolist(),
        "kenyon_cells": np.flatnonzero(types.str.startswith("KC")).tolist(),
        "mbon07_reward_output": np.flatnonzero(types.eq("MBON07")).tolist(),
        "mbon11_aversive_output": np.flatnonzero(types.eq("MBON11")).tolist(),
        "epg_compass_neurons": np.flatnonzero(types.str.startswith("EPG")).tolist(),
        "dna02_left": np.flatnonzero(types.eq("DNa02") & soma_side.eq("L")).tolist(),
        "dna02_right": np.flatnonzero(types.eq("DNa02") & soma_side.eq("R")).tolist(),
        "dnp09_forward": np.flatnonzero(types.isin(["DNp09", "MN9"])).tolist(),
        "mdn_moonwalker": np.flatnonzero(types.eq("MDN") | types.str.startswith("MDN")).tolist(),
        "giant_fiber_escape": np.flatnonzero(types.isin(["DNp01", "GF"]) | types.str.startswith("Giant_Fiber")).tolist(),
        "excitatory_neurons": np.flatnonzero(signs > 0).tolist(),
        "inhibitory_neurons": np.flatnonzero(signs < 0).tolist(),
        "vnc_t1_left": vnc_t1_l,
        "vnc_t1_right": vnc_t1_r,
        "vnc_t2_left": vnc_t2_l,
        "vnc_t2_right": vnc_t2_r,
        "vnc_t3_left": vnc_t3_l,
        "vnc_t3_right": vnc_t3_r,
    }

    for name, indices in circuits.items():
        print(f"      - {name:25s}: {len(indices):6d} identified neurons")

    # Save outputs
    print(f"\n[*] Saving compiled graph to {OUTPUT_NPZ}...")
    np.savez_compressed(
        OUTPUT_NPZ,
        indptr=adj_matrix.indptr,
        indices=adj_matrix.indices,
        data=adj_matrix.data,
        shape=adj_matrix.shape,
        neuron_ids=neuron_ids,
        polarity=signs.astype(np.int8),
    )

    print(f"[*] Saving circuits manifest to {CIRCUITS_JSON}...")
    with open(CIRCUITS_JSON, "w") as f:
        json.dump(circuits, f, indent=2)

    elapsed = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"MCNS v1.0 COMPILATION SUCCESSFUL in {elapsed:.1f}s!")
    print(f"Neurons: {num_nodes:,} | Synaptic Edges: {num_retained_edges:,}")
    print(f"Graph file size: {OUTPUT_NPZ.stat().st_size / (1024*1024):.1f} MB")
    print("=" * 70)


if __name__ == "__main__":
    compile_connectome()
