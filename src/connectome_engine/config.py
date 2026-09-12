"""Central configuration, file paths, and biophysical neural constants."""

from pathlib import Path
from dataclasses import dataclass

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "malecns_v1"
STIMULI_DIR = ROOT_DIR / "stimuli"


@dataclass(frozen=True)
class BiophysicalConstants:
    """Leaky Integrate-and-Fire (LIF) parameters and kinetic rate constants."""

    # Membrane dynamics
    tau_m_ms: float = 20.0        # Membrane time constant (ms)
    v_rest_mv: float = -65.0      # Resting membrane potential (mV)
    v_thresh_mv: float = -50.0    # Action potential trigger threshold (mV)
    v_reset_mv: float = -70.0     # Post-spike reset potential (mV)
    tau_ref_ms: float = 2.0       # Absolute refractory period (ms)
    r_membrane_mohm: float = 10.0 # Membrane resistance (Megaohms)

    # Numerical integration
    dt_ms: float = 0.1            # SNN sub-step integration step (ms)
    chunk_ms: float = 50.0        # SNN time per video/photo observation frame (ms)
    substeps_per_chunk: int = 500 # chunk_ms / dt_ms (500 steps)

    # Synaptic scale
    synaptic_weight_scale: float = 0.275 # Scaling multiplier for raw synapse counts

    # Optical eye resolution
    frame_width: int = 90
    frame_height: int = 160


@dataclass(frozen=True)
class HormoneKineticsConstants:
    """Kinetics for neuromodulators and plasticity."""

    # Dopamine (Reward / Appetitive)
    da_synthesis_rate: float = 0.85    # nM per PAM11 spike
    da_decay_tau_ms: float = 120.0     # Transporter clearance decay constant (ms)
    da_baseline_nm: float = 5.0        # Tonic baseline concentration (nM)

    # Octopamine (Stress / Adrenaline)
    oa_synthesis_rate: float = 1.20    # nM per sensory shock / threat spike
    oa_decay_tau_ms: float = 180.0     # Clearance decay constant (ms)
    oa_baseline_nm: float = 2.0        # Tonic baseline concentration (nM)

    # Serotonin (Calm / Satiety)
    serotonin_synthesis_rate: float = 0.60
    serotonin_decay_tau_ms: float = 250.0
    serotonin_baseline_nm: float = 8.0


CONFIG = BiophysicalConstants()
HORMONE_CONFIG = HormoneKineticsConstants()
