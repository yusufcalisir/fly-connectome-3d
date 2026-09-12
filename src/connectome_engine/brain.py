"""Central unified Brain Engine orchestrating sensory inputs, SNN dynamics, hormones, and motor decoding."""

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp

from .config import CONFIG, BiophysicalConstants
from .data.circuits import IndexedCircuits
from .simulation.hormones import HormoneDynamicsEngine
from .simulation.lif_kernel import SpikingConnectomeEngine
from .simulation.motor_decoder import MotorBehavioralDecoder
from .simulation.visual_transduction import VisualTransductionEngine


@dataclass
class CompleteObservationTelemetry:
    """Consolidated telemetry packet streamed to the 3D dashboard."""

    sim_time_ms: float
    total_spikes: int
    mean_firing_rate_hz: float

    # Neurochemical Hormones
    dopamine_hz: float
    dopamine_conc_nm: float
    octopamine_hz: float
    octopamine_conc_nm: float
    serotonin_hz: float
    serotonin_conc_nm: float
    ei_balance_ratio: float
    learned_knowledge_index: float

    # Motor Telemetry
    steering_deflection: float
    forward_drive_pct: float
    moonwalker_retreat: bool
    giant_fiber_jump: bool
    front_leg_swipe_angle: float
    compass_heading_deg: float

    # Visual State
    mean_luminance: float
    color_temperature_k: float
    looming_threat_detected: bool

    # Raster activity for top landmark neurons (indices of active cells in chunk)
    active_landmarks: list

    # Biological E/I spike partition (Dale's Principle)
    excitatory_spikes: int = 0
    inhibitory_spikes: int = 0

    # Active spiking neuron indices across the connectome for 3D point cloud wave
    active_neurons: list = field(default_factory=list)


class ConnectomeBrain:
    """Master controller wrapping the complete neural and biophysical pipeline."""

    def __init__(
        self,
        num_neurons: int,
        synaptic_weights: sp.csr_matrix,
        circuits: IndexedCircuits,
        constants: BiophysicalConstants = CONFIG,
    ):
        self.circuits = circuits
        self.snn = SpikingConnectomeEngine(
            num_neurons,
            synaptic_weights,
            constants,
            polarity=circuits.polarity,
        )
        self.hormones = HormoneDynamicsEngine()
        self.visual = VisualTransductionEngine(
            num_r1_r6=len(circuits.r1_r6_photoreceptors),
            num_r8=len(circuits.r8_photoreceptors),
            num_looming_lc4=len(circuits.looming_threat_lc4),
        )
        self.motor = MotorBehavioralDecoder()

        # Landmark subset for raster display (64 neurons)
        self.landmark_indices = np.r_[
            self.circuits.pam11_dopamine_reward[:8],
            self.circuits.ppl101_dopamine_aversive[:2],
            self.circuits.r1_r6_photoreceptors[:16],
            self.circuits.r8_photoreceptors[:8],
            self.circuits.looming_threat_lc4[:8],
            self.circuits.kenyon_cells[:12],
            self.circuits.dna02_left[:2],
            self.circuits.dna02_right[:2],
            self.circuits.dnp09_forward[:2],
            self.circuits.giant_fiber_escape[:2],
        ].astype(np.int32)

    def observe_frame(
        self,
        frame_rgba: np.ndarray,
        duration_ms: float = 50.0,
        manual_dopamine_boost_mv: float = 0.0,
    ) -> CompleteObservationTelemetry:
        """Process one visual frame from the virtual phone, advance SNN, and return full telemetry."""
        # 1. Visual Transduction
        vis_telemetry = self.visual.process_frame(frame_rgba)

        # Clear and inject fresh currents
        self.snn.clear_injected_currents()

        if len(self.circuits.r1_r6_photoreceptors) > 0:
            self.snn.inject_current(
                self.circuits.r1_r6_photoreceptors,
                vis_telemetry.r1_r6_currents[: len(self.circuits.r1_r6_photoreceptors)],
            )

        if len(self.circuits.r8_photoreceptors) > 0:
            self.snn.inject_current(
                self.circuits.r8_photoreceptors,
                vis_telemetry.r8_currents[: len(self.circuits.r8_photoreceptors)],
            )

        # If looming predator detected, blast current directly into LC4 threat circuit
        if vis_telemetry.looming_threat_detected and len(self.circuits.looming_threat_lc4) > 0:
            self.snn.inject_current(
                self.circuits.looming_threat_lc4,
                vis_telemetry.looming_currents[: len(self.circuits.looming_threat_lc4)],
            )

        # Manual Wireheading stimulation if triggered
        if manual_dopamine_boost_mv > 0.0 and len(self.circuits.pam11_dopamine_reward) > 0:
            self.snn.inject_current(
                self.circuits.pam11_dopamine_reward,
                np.full(len(self.circuits.pam11_dopamine_reward), manual_dopamine_boost_mv, dtype=np.float32),
            )
            self.hormones.trigger_wirehead_surge(manual_dopamine_boost_mv)

        # 2. Advance Biophysical SNN
        snn_telemetry = self.snn.step_chunk(chunk_ms=duration_ms)

        # 3. Read Circuit Spikes — use numpy for O(n) instead of O(n*m) Python loops
        if snn_telemetry.total_spikes > 0:
            spiking_arr = np.array(list(snn_telemetry.spiking_neuron_indices), dtype=np.int32)
        else:
            spiking_arr = np.empty(0, dtype=np.int32)

        def _count_hits(circuit_idx: np.ndarray) -> int:
            if len(circuit_idx) == 0 or len(spiking_arr) == 0:
                return 0
            return int(np.isin(circuit_idx, spiking_arr).sum())

        pam11_spk = _count_hits(self.circuits.pam11_dopamine_reward)
        threat_spk = _count_hits(self.circuits.looming_threat_lc4)
        kc_spk = _count_hits(self.circuits.kenyon_cells)
        dna02_l_spk = _count_hits(self.circuits.dna02_left)
        dna02_r_spk = _count_hits(self.circuits.dna02_right)
        dnp09_spk = _count_hits(self.circuits.dnp09_forward)
        mdn_spk = _count_hits(self.circuits.mdn_moonwalker)
        gf_spk = _count_hits(self.circuits.giant_fiber_escape)

        # 4. Step Hormonal Kinetics with real biological E/I spike counts
        hormone_telemetry = self.hormones.update(
            pam11_spikes=pam11_spk,
            num_pam11=len(self.circuits.pam11_dopamine_reward),
            threat_spikes=threat_spk,
            num_threat_nodes=len(self.circuits.looming_threat_lc4),
            total_excitatory_spikes=snn_telemetry.excitatory_spikes,
            total_inhibitory_spikes=snn_telemetry.inhibitory_spikes,
            kc_spikes=kc_spk,
            duration_ms=duration_ms,
        )

        # 5. Decode Motor Kinematics
        motor_telemetry = self.motor.decode(
            dna02_left_spikes=dna02_l_spk,
            dna02_right_spikes=dna02_r_spk,
            dnp09_forward_spikes=dnp09_spk,
            mdn_reverse_spikes=mdn_spk,
            giant_fiber_spikes=gf_spk,
        )

        # Landmark raster — vectorized
        active_landmarks = self.landmark_indices[np.isin(self.landmark_indices, spiking_arr)].tolist()

        return CompleteObservationTelemetry(
            sim_time_ms=snn_telemetry.simulated_time_ms,
            total_spikes=snn_telemetry.total_spikes,
            mean_firing_rate_hz=snn_telemetry.mean_firing_rate_hz,
            dopamine_hz=hormone_telemetry.dopamine_hz,
            dopamine_conc_nm=hormone_telemetry.dopamine_conc_nm,
            octopamine_hz=hormone_telemetry.octopamine_hz,
            octopamine_conc_nm=hormone_telemetry.octopamine_conc_nm,
            serotonin_hz=hormone_telemetry.serotonin_hz,
            serotonin_conc_nm=hormone_telemetry.serotonin_conc_nm,
            ei_balance_ratio=hormone_telemetry.excitatory_inhibitory_ratio,
            learned_knowledge_index=hormone_telemetry.learned_knowledge_index,
            excitatory_spikes=snn_telemetry.excitatory_spikes,
            inhibitory_spikes=snn_telemetry.inhibitory_spikes,
            steering_deflection=motor_telemetry.steering_deflection,
            forward_drive_pct=motor_telemetry.forward_drive_pct,
            moonwalker_retreat=motor_telemetry.moonwalker_retreat,
            giant_fiber_jump=motor_telemetry.giant_fiber_jump,
            front_leg_swipe_angle=motor_telemetry.front_leg_swipe_angle,
            compass_heading_deg=motor_telemetry.compass_heading_deg,
            mean_luminance=vis_telemetry.mean_luminance,
            color_temperature_k=vis_telemetry.color_temperature_k,
            looming_threat_detected=vis_telemetry.looming_threat_detected,
            active_landmarks=active_landmarks,
            active_neurons=spiking_arr.tolist(),
        )
