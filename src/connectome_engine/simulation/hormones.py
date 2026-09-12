"""Neuromodulator hormone dynamics and synaptic plasticity kinetic engine."""

from dataclasses import dataclass
from typing import Dict
import numpy as np

from ..config import HORMONE_CONFIG, HormoneKineticsConstants


@dataclass
class HormoneTelemetry:
    """Current circulating neurochemical concentrations and firing rates."""

    dopamine_hz: float
    dopamine_conc_nm: float
    octopamine_hz: float
    octopamine_conc_nm: float
    serotonin_hz: float
    serotonin_conc_nm: float
    excitatory_inhibitory_ratio: float
    learned_knowledge_index: float


class HormoneDynamicsEngine:
    """Simulates real continuous neurochemical concentrations and plasticity.

    Models:
    - Dopamine ([DA]): Released by PAM11 cluster, cleared by DAT transporter.
    - Octopamine ([OA]): Released by TDC2 cluster upon acute sensory shock / looming threats.
    - Serotonin ([5-HT]): Baseline calmness and visual stability.
    - STDP Synaptic Plasticity: Dopamine-modulated reinforcement between Kenyon Cells and MBON.
    """

    def __init__(self, constants: HormoneKineticsConstants = HORMONE_CONFIG):
        self.cfg = constants

        # Circulating concentrations (nM)
        self.da_conc = self.cfg.da_baseline_nm
        self.oa_conc = self.cfg.oa_baseline_nm
        self.serotonin_conc = self.cfg.serotonin_baseline_nm

        # Firing rate smoothers (Hz)
        self.smoothed_da_hz = 0.0
        self.smoothed_oa_hz = 0.0
        self.smoothed_serotonin_hz = 0.0

        # Synaptic Plasticity accumulator (KC -> MBON learned weight drift)
        self.learned_weight_drift = 0.0

    def update(
        self,
        pam11_spikes: int,
        num_pam11: int,
        threat_spikes: int,
        num_threat_nodes: int,
        total_excitatory_spikes: int,
        total_inhibitory_spikes: int,
        kc_spikes: int,
        duration_ms: float = 50.0,
    ) -> HormoneTelemetry:
        """Step kinetic ODEs for one simulation chunk."""
        duration_sec = max(1e-5, duration_ms / 1000.0)

        # 1. Dopamine Dynamics
        inst_da_hz = (pam11_spikes / (max(1, num_pam11) * duration_sec))
        self.smoothed_da_hz = 0.7 * self.smoothed_da_hz + 0.3 * inst_da_hz
        da_decay = np.exp(-duration_ms / self.cfg.da_decay_tau_ms)
        self.da_conc = (
            self.cfg.da_baseline_nm
            + (self.da_conc - self.cfg.da_baseline_nm) * da_decay
            + (pam11_spikes * self.cfg.da_synthesis_rate)
        )

        # 2. Octopamine (Stress / Adrenaline) Dynamics
        inst_oa_hz = (threat_spikes / (max(1, num_threat_nodes) * duration_sec))
        self.smoothed_oa_hz = 0.7 * self.smoothed_oa_hz + 0.3 * inst_oa_hz
        oa_decay = np.exp(-duration_ms / self.cfg.oa_decay_tau_ms)
        self.oa_conc = (
            self.cfg.oa_baseline_nm
            + (self.oa_conc - self.cfg.oa_baseline_nm) * oa_decay
            + (threat_spikes * self.cfg.oa_synthesis_rate)
        )

        # 3. Serotonin (Calmness / Satiety) Dynamics
        # High stress suppresses serotonin; calm baseline promotes it
        stress_suppression = max(0.2, 1.0 - (self.oa_conc / 50.0))
        self.serotonin_conc = (
            self.cfg.serotonin_baseline_nm * stress_suppression
        )
        self.smoothed_serotonin_hz = 12.0 * stress_suppression

        # 4. E/I Balance (ACh vs GABA/Glutamate)
        total_flux = total_excitatory_spikes + total_inhibitory_spikes
        ei_ratio = (
            float(total_excitatory_spikes / max(1, total_flux))
            if total_flux > 0
            else 0.5
        )

        # 5. Dopamine-Modulated Synaptic Plasticity (STDP)
        # If Kenyon cells are active while Dopamine is high, associative memory increases
        if self.da_conc > (self.cfg.da_baseline_nm * 1.5) and kc_spikes > 0:
            plasticity_delta = 0.001 * (kc_spikes / 100.0) * (self.da_conc / self.cfg.da_baseline_nm)
            self.learned_weight_drift += plasticity_delta

        return HormoneTelemetry(
            dopamine_hz=float(self.smoothed_da_hz),
            dopamine_conc_nm=float(self.da_conc),
            octopamine_hz=float(self.smoothed_oa_hz),
            octopamine_conc_nm=float(self.oa_conc),
            serotonin_hz=float(self.smoothed_serotonin_hz),
            serotonin_conc_nm=float(self.serotonin_conc),
            excitatory_inhibitory_ratio=float(ei_ratio),
            learned_knowledge_index=float(self.learned_weight_drift),
        )

    def trigger_wirehead_surge(self, current_mv: float = 20.0):
        """Simulate direct artificial electrode stimulation of dopamine circuits."""
        self.da_conc += current_mv * 2.5
        self.smoothed_da_hz += current_mv * 1.8
