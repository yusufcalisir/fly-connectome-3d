"""Biological circuit definitions and cell-type indexing for Drosophila connectomes."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp


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

    # Hemispheric Vision Partition (Defaults to empty or automatically split from flat photoreceptors)
    r1_r6_left: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))
    r1_r6_right: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))
    r8_left: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))
    r8_right: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))

    # Biological Neurotransmitter Polarity (Dale's Principle)
    excitatory_neurons: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))
    inhibitory_neurons: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))
    polarity: np.ndarray | None = None

    # VNC (Ventral Nerve Cord) Hexapod Leg Motor Pools (T1..T3, L/R)
    vnc_t1_left: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))   # Prothoracic Left (Front Leg L1)
    vnc_t1_right: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))  # Prothoracic Right (Front Leg R1)
    vnc_t2_left: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))   # Mesothoracic Left (Middle Leg L2)
    vnc_t2_right: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))  # Mesothoracic Right (Middle Leg R2)
    vnc_t3_left: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))   # Metathoracic Left (Hind Leg L3)
    vnc_t3_right: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int32))  # Metathoracic Right (Hind Leg R3)

    def __post_init__(self):
        """Ensure hemispheric arrays are initialized if only flat arrays were provided."""
        if len(self.r1_r6_left) == 0 and len(self.r1_r6_right) == 0 and len(self.r1_r6_photoreceptors) > 0:
            mid = len(self.r1_r6_photoreceptors) // 2
            self.r1_r6_left = self.r1_r6_photoreceptors[:mid]
            self.r1_r6_right = self.r1_r6_photoreceptors[mid:]
        if len(self.r8_left) == 0 and len(self.r8_right) == 0 and len(self.r8_photoreceptors) > 0:
            mid = len(self.r8_photoreceptors) // 2
            self.r8_left = self.r8_photoreceptors[:mid]
            self.r8_right = self.r8_photoreceptors[mid:]


def map_transmitter_signs(transmitters: pd.Series) -> tuple[np.ndarray, np.ndarray]:
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

    signs[cleaned == "acetylcholine"] = 1.0
    signs[cleaned == "gaba"] = -1.0
    signs[cleaned == "glutamate"] = -1.0
    signs[cleaned == "histamine"] = -1.0
    signs[cleaned == "dopamine"] = 1.0
    signs[cleaned == "serotonin"] = 1.0
    signs[cleaned == "octopamine"] = 1.0

    unmapped = np.count_nonzero(cleaned == "") + np.count_nonzero(cleaned == "unknown")
    return signs, np.array([unmapped], dtype=np.int32)


def extract_circuits_from_annotations(
    annotations_df: pd.DataFrame,
    ids: np.ndarray,
    transmitters_df: pd.DataFrame | None = None,
) -> IndexedCircuits:
    """Extract and validate all functional circuits from annotations dataframe."""
    df = annotations_df.copy()
    if "bodyId" in df.columns:
        df = df.set_index("bodyId")

    # Reindex to match the exact order of the graph nodes
    df_aligned = df.reindex(ids)
    types = df_aligned["type"].fillna("").astype(str)
    soma_side = (
        df_aligned.get("somaSide", pd.Series("", index=df_aligned.index))
        .fillna(df_aligned.get("rootSide", pd.Series("", index=df_aligned.index)))
        .fillna("")
        .astype(str)
    )

    # Photoreceptors: Bilateral Hemispheric Retinotopic Partitioning
    r1_r6_l = np.flatnonzero(types.eq("R1-R6") & soma_side.eq("L")).astype(np.int32)
    r1_r6_r = np.flatnonzero(types.eq("R1-R6") & soma_side.eq("R")).astype(np.int32)
    if len(r1_r6_l) > 0 or len(r1_r6_r) > 0:
        r1_r6 = np.r_[r1_r6_l, r1_r6_r].astype(np.int32)
    else:
        r1_r6 = np.flatnonzero(types.eq("R1-R6")).astype(np.int32)

    r8_l = np.flatnonzero(types.str.startswith("R8") & soma_side.eq("L")).astype(np.int32)
    r8_r = np.flatnonzero(types.str.startswith("R8") & soma_side.eq("R")).astype(np.int32)
    if len(r8_l) > 0 or len(r8_r) > 0:
        r8 = np.r_[r8_l, r8_r].astype(np.int32)
    else:
        r8 = np.flatnonzero(types.str.startswith("R8")).astype(np.int32)

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
    gf = np.flatnonzero(types.isin(["DNp01", "GF"]) | types.str.startswith("Giant_Fiber")).astype(np.int32)

    # VNC (Ventral Nerve Cord) Thoracic Leg Motor Neurons
    subclass = (
        df_aligned["subclass"].fillna("").astype(str)
        if "subclass" in df_aligned.columns
        else pd.Series("", index=df_aligned.index)
    )
    superclass = (
        df_aligned["superclass"].fillna("").astype(str)
        if "superclass" in df_aligned.columns
        else pd.Series("", index=df_aligned.index)
    )
    is_leg_motor = superclass.eq("vnc_motor")

    vnc_t1_l = np.flatnonzero(is_leg_motor & subclass.eq("fl") & soma_side.eq("L")).astype(np.int32)
    vnc_t1_r = np.flatnonzero(is_leg_motor & subclass.eq("fl") & soma_side.eq("R")).astype(np.int32)
    vnc_t2_l = np.flatnonzero(is_leg_motor & subclass.eq("ml") & soma_side.eq("L")).astype(np.int32)
    vnc_t2_r = np.flatnonzero(is_leg_motor & subclass.eq("ml") & soma_side.eq("R")).astype(np.int32)
    vnc_t3_l = np.flatnonzero(is_leg_motor & subclass.eq("hl") & soma_side.eq("L")).astype(np.int32)
    vnc_t3_r = np.flatnonzero(is_leg_motor & subclass.eq("hl") & soma_side.eq("R")).astype(np.int32)

    # Polarity
    exc_neurons = np.empty(0, dtype=np.int32)
    inh_neurons = np.empty(0, dtype=np.int32)
    polarity = None
    if transmitters_df is not None and "consensus_nt" in transmitters_df.columns:
        trans_series = df_aligned.index.map(transmitters_df["consensus_nt"]).fillna("")
        signs, _ = map_transmitter_signs(trans_series)
        exc_neurons = np.flatnonzero(signs > 0).astype(np.int32)
        inh_neurons = np.flatnonzero(signs < 0).astype(np.int32)
        polarity = signs.astype(np.int8)

    return IndexedCircuits(
        r1_r6_photoreceptors=r1_r6,
        r8_photoreceptors=r8,
        looming_threat_lc4=lc4,
        r1_r6_left=r1_r6_l,
        r1_r6_right=r1_r6_r,
        r8_left=r8_l,
        r8_right=r8_r,
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
        excitatory_neurons=exc_neurons,
        inhibitory_neurons=inh_neurons,
        polarity=polarity,
        vnc_t1_left=vnc_t1_l,
        vnc_t1_right=vnc_t1_r,
        vnc_t2_left=vnc_t2_l,
        vnc_t2_right=vnc_t2_r,
        vnc_t3_left=vnc_t3_l,
        vnc_t3_right=vnc_t3_r,
    )


def load_malecns_v1_connectome(
    data_dir: Path | None = None,
) -> tuple[int, sp.csr_matrix, IndexedCircuits, np.ndarray]:
    """Load the official compiled Janelia MaleCNS v1.0 (166,700 neurons, 25,582,938 synapses) connectome."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[3] / "data" / "malecns_v1"

    graph_path = data_dir / "malecns_v1_graph.npz"
    manifest_path = data_dir / "circuits_manifest.json"

    if not graph_path.exists() or not manifest_path.exists():
        raise FileNotFoundError(
            f"Compiled connectome not found at {graph_path}. Run downloader and compiler first."
        )

    with np.load(graph_path) as npz:
        indptr = npz["indptr"]
        indices = npz["indices"]
        data = npz["data"]
        shape = tuple(npz["shape"])
        neuron_ids = npz["neuron_ids"]
        polarity = npz.get("polarity", None)

    adj = sp.csr_matrix((data, indices, indptr), shape=shape, dtype=np.float32)

    with open(manifest_path, "r") as f:
        c_dict = json.load(f)

    if polarity is not None:
        exc_neurons = np.flatnonzero(polarity > 0).astype(np.int32)
        inh_neurons = np.flatnonzero(polarity < 0).astype(np.int32)
    elif "excitatory_neurons" in c_dict:
        exc_neurons = np.array(c_dict["excitatory_neurons"], dtype=np.int32)
        inh_neurons = np.array(c_dict["inhibitory_neurons"], dtype=np.int32)
        polarity = np.zeros(shape[0], dtype=np.int8)
        polarity[exc_neurons] = 1
        polarity[inh_neurons] = -1
    else:
        exc_neurons = np.arange(shape[0], dtype=np.int32)
        inh_neurons = np.empty(0, dtype=np.int32)
        polarity = np.ones(shape[0], dtype=np.int8)

    r1_r6_l = np.array(c_dict.get("r1_r6_left", []), dtype=np.int32)
    r1_r6_r = np.array(c_dict.get("r1_r6_right", []), dtype=np.int32)
    r8_l = np.array(c_dict.get("r8_left", []), dtype=np.int32)
    r8_r = np.array(c_dict.get("r8_right", []), dtype=np.int32)

    vnc_t1_l = np.array(c_dict.get("vnc_t1_left", []), dtype=np.int32)
    vnc_t1_r = np.array(c_dict.get("vnc_t1_right", []), dtype=np.int32)
    vnc_t2_l = np.array(c_dict.get("vnc_t2_left", []), dtype=np.int32)
    vnc_t2_r = np.array(c_dict.get("vnc_t2_right", []), dtype=np.int32)
    vnc_t3_l = np.array(c_dict.get("vnc_t3_left", []), dtype=np.int32)
    vnc_t3_r = np.array(c_dict.get("vnc_t3_right", []), dtype=np.int32)

    circuits = IndexedCircuits(
        r1_r6_photoreceptors=np.array(c_dict["r1_r6_photoreceptors"], dtype=np.int32),
        r8_photoreceptors=np.array(c_dict["r8_photoreceptors"], dtype=np.int32),
        looming_threat_lc4=np.array(c_dict["looming_threat_lc4"], dtype=np.int32),
        r1_r6_left=r1_r6_l,
        r1_r6_right=r1_r6_r,
        r8_left=r8_l,
        r8_right=r8_r,
        pam11_dopamine_reward=np.array(c_dict["pam11_dopamine_reward"], dtype=np.int32),
        ppl101_dopamine_aversive=np.array(c_dict["ppl101_dopamine_aversive"], dtype=np.int32),
        octopamine_stress=np.array(c_dict["octopamine_stress"], dtype=np.int32),
        serotonin_calm=np.array(c_dict["serotonin_calm"], dtype=np.int32),
        kenyon_cells=np.array(c_dict["kenyon_cells"], dtype=np.int32),
        mbon07_reward_output=np.array(c_dict["mbon07_reward_output"], dtype=np.int32),
        mbon11_aversive_output=np.array(c_dict["mbon11_aversive_output"], dtype=np.int32),
        epg_compass_neurons=np.array(c_dict["epg_compass_neurons"], dtype=np.int32),
        dna02_left=np.array(c_dict["dna02_left"], dtype=np.int32),
        dna02_right=np.array(c_dict["dna02_right"], dtype=np.int32),
        dnp09_forward=np.array(c_dict["dnp09_forward"], dtype=np.int32),
        mdn_moonwalker=np.array(c_dict["mdn_moonwalker"], dtype=np.int32),
        giant_fiber_escape=np.array(c_dict["giant_fiber_escape"], dtype=np.int32),
        excitatory_neurons=exc_neurons,
        inhibitory_neurons=inh_neurons,
        polarity=polarity,
        vnc_t1_left=vnc_t1_l,
        vnc_t1_right=vnc_t1_r,
        vnc_t2_left=vnc_t2_l,
        vnc_t2_right=vnc_t2_r,
        vnc_t3_left=vnc_t3_l,
        vnc_t3_right=vnc_t3_r,
    )

    return shape[0], adj, circuits, neuron_ids
