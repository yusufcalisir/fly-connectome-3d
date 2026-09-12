"""Biological circuit definitions and cell-type indexing for Drosophila connectomes."""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


@dataclass
class IndexedCircuits:
    """Indexed neuron subsets by biological function and neurotransmitter."""

    # Sensory: Vision
    r1_r6_photoreceptors: np.ndarray  # Luminance outer lattice (3,335 cells)
    r8_photoreceptors: np.ndarray     # Chromatic inner lattice (811 cells)
    looming_threat_lc4: np.ndarray    # Lobula columnar LC4/LPLC2 looming neurons

    # Neuromodulators
    pam11_dopamine_reward: np.ndarray   # 15 cells in PAM cluster (Reward/Appetitive)
    ppl101_dopamine_aversive: np.ndarray# 2 cells in PPL cluster (Punishment/Aversive)
    octopamine_stress: np.ndarray       # TDC2 / VUM cluster (Insect Adrenaline / Stress)
    serotonin_calm: np.ndarray          # 5-HT serotonergic clusters (Satiety / Calm)

    # Learning Compartments
    kenyon_cells: np.ndarray            # ~5,000 KC cells in Mushroom Body
    mbon07_reward_output: np.ndarray    # MBON07 (alpha1) appetitive output
    mbon11_aversive_output: np.ndarray  # MBON11 (gamma1pedc) aversive output

    # Navigation & Central Complex
    epg_compass_neurons: np.ndarray     # Ellipsoid body heading compass (Ring Attractor)

    # Descending Motor Outputs
    dna02_left: np.ndarray              # Steering turn left
    dna02_right: np.ndarray             # Steering turn right
    dnp09_forward: np.ndarray           # Forward walking / locomotion
    mdn_moonwalker: np.ndarray          # Backward reverse retreat
    giant_fiber_escape: np.ndarray      # Bilateral emergency jump/flight escape


def map_transmitter_signs(transmitters: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
    """Map biological neurotransmitter identities to synaptic signs.

    Fast transmission rules (verified from FlyWire/MaleCNS annotations):
    - Acetylcholine (ACh): Excitatory (+1.0)
    - GABA: Inhibitory (-1.0)
    - Glutamate: Inhibitory in insect nervous systems (-1.0 via GluCl channels)
    - Histamine: Inhibitory (-1.0 in insect visual system)
    - Modulators (Dopamine, Serotonin, Octopamine) or unknown: Defaults to +1.0
    """
    cleaned = transmitters.fillna("").str.lower().to_numpy()
    signs = np.ones(len(cleaned), dtype=np.float32)
    uncertain = np.zeros(len(cleaned), dtype=bool)

    for i, t in enumerate(cleaned):
        if "acetylcholine" in t or "ach" in t:
            signs[i] = 1.0
        elif "gaba" in t or "glutamate" in t or "histamine" in t:
            signs[i] = -1.0
        elif not t:
            uncertain[i] = True
            signs[i] = 1.0
        else:
            # Neuromodulators or mixed
            signs[i] = 1.0

    return signs, uncertain


def extract_circuits(annotations_df: pd.DataFrame, ids: np.ndarray) -> IndexedCircuits:
    """Extract and validate all functional circuits from annotations dataframe."""
    df = annotations_df.copy()
    if "bodyId" in df.columns:
        df = df.set_index("bodyId")
    
    # Reindex to match the exact order of the graph nodes
    df_aligned = df.reindex(ids)
    types = df_aligned["type"].fillna("").astype(str)
    soma_side = df_aligned.get("somaSide", pd.Series("", index=df_aligned.index)).fillna("").astype(str)

    # Photoreceptors
    r1_r6 = np.flatnonzero(types.eq("R1-R6")).astype(np.int32)
    r8 = np.flatnonzero(types.eq("R8")).astype(np.int32)
    lc4 = np.flatnonzero(types.str.startswith("LC4") | types.str.startswith("LPLC2")).astype(np.int32)

    # Neuromodulators
    pam11 = np.flatnonzero(types.eq("PAM11")).astype(np.int32)
    ppl101 = np.flatnonzero(types.eq("PPL101")).astype(np.int32)
    octopamine = np.flatnonzero(types.str.contains("TDC2") | types.str.contains("VUM") | types.str.startswith("OA-")).astype(np.int32)
    serotonin = np.flatnonzero(types.str.contains("5-HT") | types.str.startswith("CSD") | types.str.startswith("5HT-")).astype(np.int32)

    # Mushroom body
    kc = np.flatnonzero(types.str.startswith("KC")).astype(np.int32)
    mbon07 = np.flatnonzero(types.eq("MBON07")).astype(np.int32)
    mbon11 = np.flatnonzero(types.eq("MBON11")).astype(np.int32)

    # Central complex
    epg = np.flatnonzero(types.str.startswith("EPG")).astype(np.int32)

    # Motor descending
    dna02_l = np.flatnonzero(types.eq("DNa02") & soma_side.eq("L")).astype(np.int32)
    dna02_r = np.flatnonzero(types.eq("DNa02") & soma_side.eq("R")).astype(np.int32)
    dnp09 = np.flatnonzero(types.isin(["DNp09", "MN9"])).astype(np.int32)
    mdn = np.flatnonzero(types.eq("MDN") | types.str.startswith("MDN")).astype(np.int32)
    gf = np.flatnonzero(types.str.startswith("Giant_Fiber") | types.eq("GF")).astype(np.int32)

    return IndexedCircuits(
        r1_r6_photoreceptors=r1_r6,
        r8_photoreceptors=r8,
        looming_threat_lc4=lc4,
        pam11_dopamine_reward=pam11,
        ppl101_dopamine_aversive=ppl101,
        octopamine_stress=octopamine,
        serotonin_calm=serotonin,
        kenyon_cells=kc,
        mbon07_reward_output=mbon07,
        mbon11_aversive_output=mbon11,
        epg_compass_neurons=epg,
        dna02_left=dna02_l,
        dna02_right=dna02_r,
        dnp09_forward=dnp09,
        mdn_moonwalker=mdn,
        giant_fiber_escape=gf,
    )
