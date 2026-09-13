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
    # NOTE: dopamine_hz is the firing rate (Hz) of PAM11 dopaminergic reward cells;
    # dopamine_conc_nm is the simulated extracellular concentration (nM) subject to synthesis & DAT clearance.
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
    active_landmarks: list = field(default_factory=list)

    # Chromatic Photometry Metrics
    cct_duv: float = 0.0
    cct_valid: bool = True

    # Biological E/I spike partition (Dale's Principle)
    excitatory_spikes: int = 0
    inhibitory_spikes: int = 0

    # Active spiking neuron indices across the connectome for 3D point cloud wave
    active_neurons: list = field(default_factory=list)

    # Hemispheric Vision & Bilateral Optomotor Signals
    left_luminance: float = 0.0
    right_luminance: float = 0.0
    hemispheric_asymmetry: float = 0.0
    dna02_left_spikes: int = 0
    dna02_right_spikes: int = 0

    # VNC Thoracic Hexapod Leg Motor Pools & CPG Dynamics
    t1_left_hz: float = 0.0
    t1_right_hz: float = 0.0
    t2_left_hz: float = 0.0
    t2_right_hz: float = 0.0
    t3_left_hz: float = 0.0
    t3_right_hz: float = 0.0
    tripod_phase: float = 0.0


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
            num_r1_r6_left=len(circuits.r1_r6_left) if len(circuits.r1_r6_left) > 0 else 1112,
            num_r1_r6_right=len(circuits.r1_r6_right) if len(circuits.r1_r6_right) > 0 else 2265,
            num_r8_left=len(circuits.r8_left) if len(circuits.r8_left) > 0 else 625,
            num_r8_right=len(circuits.r8_right) if len(circuits.r8_right) > 0 else 704,
            num_looming_lc4=len(circuits.looming_threat_lc4),
        )
        self.motor = MotorBehavioralDecoder()
        self.cpg_phase: float = 0.0

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

        # Bilateral R1-R6 Outer Photoreceptors (Hemispheric Retinotopic Partitioning)
        # NOTE: Biological Drosophila photoreceptors are graded-potential systems that do not fire
        # action potentials. They are simulated here as spiking LIF units with injected currents
        # strictly as an input display adapter to interface with the spiking connectome engine.
        if len(self.circuits.r1_r6_left) > 0 and len(vis_telemetry.r1_r6_left_currents) > 0:
            self.snn.inject_current(
                self.circuits.r1_r6_left,
                vis_telemetry.r1_r6_left_currents[: len(self.circuits.r1_r6_left)],
            )
        if len(self.circuits.r1_r6_right) > 0 and len(vis_telemetry.r1_r6_right_currents) > 0:
            self.snn.inject_current(
                self.circuits.r1_r6_right,
                vis_telemetry.r1_r6_right_currents[: len(self.circuits.r1_r6_right)],
            )

        # Bilateral R8 Inner Chromatic Photoreceptors
        if len(self.circuits.r8_left) > 0 and len(vis_telemetry.r8_left_currents) > 0:
            self.snn.inject_current(
                self.circuits.r8_left,
                vis_telemetry.r8_left_currents[: len(self.circuits.r8_left)],
            )
        if len(self.circuits.r8_right) > 0 and len(vis_telemetry.r8_right_currents) > 0:
            self.snn.inject_current(
                self.circuits.r8_right,
                vis_telemetry.r8_right_currents[: len(self.circuits.r8_right)],
            )

        # Bilateral Optomotor Descending Motor Drive (DNa02 Steering Neurons)
        # Asymmetric visual luminance drives ipsilateral turning (positive phototaxis)
        # Gain 8.0 / 5.0 (was 5.0 / 3.0) for clearer left/right steering differentiation.
        asym = vis_telemetry.hemispheric_asymmetry
        l_steer_drive = float(np.clip(-asym * 8.0 + (vis_telemetry.left_luminance - vis_telemetry.right_luminance) * 5.0, -6.0, 9.0))
        r_steer_drive = float(np.clip(asym * 8.0 + (vis_telemetry.right_luminance - vis_telemetry.left_luminance) * 5.0, -6.0, 9.0))

        if len(self.circuits.dna02_left) > 0 and l_steer_drive != 0.0:
            self.snn.inject_current(
                self.circuits.dna02_left,
                np.full(len(self.circuits.dna02_left), l_steer_drive, dtype=np.float32),
            )
        if len(self.circuits.dna02_right) > 0 and r_steer_drive != 0.0:
            self.snn.inject_current(
                self.circuits.dna02_right,
                np.full(len(self.circuits.dna02_right), r_steer_drive, dtype=np.float32),
            )

        # If looming predator detected, blast current directly into LC4 threat circuit
        # and immediately soft-reset membrane voltages of the broader network to prevent
        # recurrent runaway amplification persisting across subsequent frames.
        if vis_telemetry.looming_threat_detected and len(self.circuits.looming_threat_lc4) > 0:
            self.snn.inject_current(
                self.circuits.looming_threat_lc4,
                vis_telemetry.looming_currents[: len(self.circuits.looming_threat_lc4)],
            )
            # Post-burst soft reset: pull non-refractory neurons 60% of the way back to rest
            # so the looming event is a transient response rather than a permanent state change.
            non_ref = self.snn.refractory_steps == 0
            self.snn.v[non_ref] = (
                self.snn.v_rest * 0.60 + self.snn.v[non_ref] * 0.40
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

        # 3. Read Circuit Spikes — Vectorized biological rate counting
        if snn_telemetry.total_spikes > 0:
            spiking_arr = np.array(list(snn_telemetry.spiking_neuron_indices), dtype=np.int32)
        else:
            spiking_arr = np.empty(0, dtype=np.int32)

        def _count_hits(circuit_idx: np.ndarray) -> int:
            if len(circuit_idx) == 0 or len(spiking_arr) == 0:
                return 0
            return int(np.isin(circuit_idx, spiking_arr).sum())

        def _count_spikes(circuit_idx: np.ndarray) -> int:
            if len(circuit_idx) == 0:
                return 0
            return int(self.snn.last_chunk_spike_counts[circuit_idx].sum())

        pam11_spk = _count_hits(self.circuits.pam11_dopamine_reward)
        threat_spk = _count_hits(self.circuits.looming_threat_lc4)
        kc_spk = _count_hits(self.circuits.kenyon_cells)
        dna02_l_spk = _count_spikes(self.circuits.dna02_left)
        dna02_r_spk = _count_spikes(self.circuits.dna02_right)
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

        # 5. Decode Motor Kinematics (with Sensory-Motor Phototaxis Integration)
        motor_telemetry = self.motor.decode(
            dna02_left_spikes=dna02_l_spk,
            dna02_right_spikes=dna02_r_spk,
            dnp09_forward_spikes=dnp09_spk,
            mdn_reverse_spikes=mdn_spk,
            giant_fiber_spikes=gf_spk,
            visual_asymmetry=vis_telemetry.hemispheric_asymmetry,
            looming_threat=vis_telemetry.looming_threat_detected,
        )

        # 6. VNC Leg Motor Pools & Hexapod Tripod CPG
        dt_s = max(1e-4, duration_ms / 1000.0)
        t1_l_spk = _count_spikes(self.circuits.vnc_t1_left)
        t1_r_spk = _count_spikes(self.circuits.vnc_t1_right)
        t2_l_spk = _count_spikes(self.circuits.vnc_t2_left)
        t2_r_spk = _count_spikes(self.circuits.vnc_t2_right)
        t3_l_spk = _count_spikes(self.circuits.vnc_t3_left)
        t3_r_spk = _count_spikes(self.circuits.vnc_t3_right)

        def _calc_hz(spk: int, pool_size: int) -> float:
            if pool_size <= 0:
                return 0.0
            return float((spk / pool_size) / dt_s)

        t1_l_hz = _calc_hz(t1_l_spk, len(self.circuits.vnc_t1_left))
        t1_r_hz = _calc_hz(t1_r_spk, len(self.circuits.vnc_t1_right))
        t2_l_hz = _calc_hz(t2_l_spk, len(self.circuits.vnc_t2_left))
        t2_r_hz = _calc_hz(t2_r_spk, len(self.circuits.vnc_t2_right))
        t3_l_hz = _calc_hz(t3_l_spk, len(self.circuits.vnc_t3_left))
        t3_r_hz = _calc_hz(t3_r_spk, len(self.circuits.vnc_t3_right))

        # Alternating Tripod CPG Phase Advancement
        # Canonical insect tripod gait: 3.0 to 11.0 Hz stepping frequency proportional to forward drive
        drive_pct = motor_telemetry.forward_drive_pct
        if motor_telemetry.moonwalker_retreat:
            cpg_omega = -2.0 * np.pi * 4.0  # Reverse stepping (rad/s)
        elif drive_pct > 2.0:
            step_freq_hz = 3.0 + (drive_pct / 100.0) * 8.0
            cpg_omega = 2.0 * np.pi * step_freq_hz
        else:
            cpg_omega = 0.0

        self.cpg_phase = float((self.cpg_phase + cpg_omega * dt_s) % (2.0 * np.pi))

        # Asymmetric Optomotor Modulation for Leg Motor Pools
        # Turning left: Right outer legs step faster/wider to pivot left
        # Turning right: Left outer legs step faster/wider to pivot right
        steer = motor_telemetry.steering_deflection
        if steer < -0.05:
            mod = abs(steer)
            t1_r_hz *= (1.0 + 0.45 * mod)
            t2_r_hz *= (1.0 + 0.45 * mod)
            t3_r_hz *= (1.0 + 0.45 * mod)
            t1_l_hz *= max(0.2, 1.0 - 0.30 * mod)
            t2_l_hz *= max(0.2, 1.0 - 0.30 * mod)
            t3_l_hz *= max(0.2, 1.0 - 0.30 * mod)
        elif steer > 0.05:
            mod = abs(steer)
            t1_l_hz *= (1.0 + 0.45 * mod)
            t2_l_hz *= (1.0 + 0.45 * mod)
            t3_l_hz *= (1.0 + 0.45 * mod)
            t1_r_hz *= max(0.2, 1.0 - 0.30 * mod)
            t2_r_hz *= max(0.2, 1.0 - 0.30 * mod)
            t3_r_hz *= max(0.2, 1.0 - 0.30 * mod)

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
            cct_duv=vis_telemetry.cct_duv,
            cct_valid=vis_telemetry.cct_valid,
            looming_threat_detected=vis_telemetry.looming_threat_detected,
            active_landmarks=active_landmarks,
            active_neurons=spiking_arr.tolist(),
            left_luminance=vis_telemetry.left_luminance,
            right_luminance=vis_telemetry.right_luminance,
            hemispheric_asymmetry=vis_telemetry.hemispheric_asymmetry,
            dna02_left_spikes=dna02_l_spk,
            dna02_right_spikes=dna02_r_spk,
            t1_left_hz=t1_l_hz,
            t1_right_hz=t1_r_hz,
            t2_left_hz=t2_l_hz,
            t2_right_hz=t2_r_hz,
            t3_left_hz=t3_l_hz,
            t3_right_hz=t3_r_hz,
            tripod_phase=self.cpg_phase,
        )
