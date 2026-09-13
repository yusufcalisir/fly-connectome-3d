"""Motor kinematics and behavioral decoding from descending neuron spike trains."""

from dataclasses import dataclass

import numpy as np


@dataclass
class MotorTelemetry:
    """Decoded physical motor kinematics and behavioral decisions."""

    steering_deflection: float  # -1.0 (hard left) to +1.0 (hard right)
    forward_drive_pct: float    # 0.0 to 100.0%
    moonwalker_retreat: bool    # True if backing away from threat
    giant_fiber_jump: bool      # True if triggered escape leap
    front_leg_swipe_angle: float# Radian angle for screen scrolling leg swipe
    compass_heading_deg: float  # Decoded Central Complex compass heading (0-360 deg)


class MotorBehavioralDecoder:
    """Decodes descending neuron action potentials into biomechanical fly telemetry."""

    def __init__(self):
        self.smooth_steering = 0.0
        self.smooth_drive = 0.0
        self.heading_deg = 0.0
        self.swipe_phase = 0.0

    def decode(
        self,
        dna02_left_spikes: int,
        dna02_right_spikes: int,
        dnp09_forward_spikes: int,
        mdn_reverse_spikes: int,
        giant_fiber_spikes: int,
        epg_active_index: int = 0,
        total_epg_nodes: int = 16,
        visual_asymmetry: float = 0.0,
        looming_threat: bool = False,
    ) -> MotorTelemetry:
        """Decode descending neuron signals for a 50 ms simulation window."""
        # 1. Bilateral Steering (DNa02) + Sensory Optomotor Asymmetry
        raw_diff = float(dna02_right_spikes - dna02_left_spikes) + visual_asymmetry * 6.0
        inst_steering = np.clip(raw_diff / 5.0, -1.0, 1.0)
        self.smooth_steering = 0.70 * self.smooth_steering + 0.30 * inst_steering

        # 2. Forward Locomotion Drive (DNp09)
        inst_drive = np.clip((dnp09_forward_spikes / 8.0) * 100.0, 0.0, 100.0)
        self.smooth_drive = 0.7 * self.smooth_drive + 0.3 * inst_drive

        # 3. Moonwalker Reverse Retreat (MDN)
        # Sinek korktuğunda veya tehdit algıladığında geriye kaçar
        retreat = mdn_reverse_spikes > 1

        # 4. Giant Fiber Emergency Panic Jump
        # SIMULATION SCOPE & DESIGN SIMPLIFICATION NOTE:
        # This implementation models ONLY the visual looming escape trigger
        # (jump = giant_fiber_spikes > 0 and looming_threat).
        # In biological Drosophila melanogaster, the Giant Fiber (GF) system is a multimodal
        # escape hub that also integrates mechanosensory afferents (antennae Johnston's organ
        # vibrations, tactile bristle deflections, and sudden wind puffs). These mechanosensory
        # modalities are NOT modeled in this visual-only connectome simulation.
        # Consequently, requiring an active visual looming threat for jump execution is a
        # deliberate design and simulation scope simplification to prevent spontaneous
        # recurrent connectome background spikes in GF neurons from triggering unprompted
        # ballistic leaps during static/quiescent conditions, rather than a claim about
        # the complete biological behavior of the fly in the wild.
        jump = (giant_fiber_spikes > 0) and looming_threat

        # 5. Compass Heading (Central Complex Ellipsoid Body EPG ring attractor)
        if total_epg_nodes > 0:
            target_angle = (epg_active_index / total_epg_nodes) * 360.0
            self.heading_deg = (target_angle + self.smooth_steering * 8.0) % 360.0
        else:
            self.heading_deg = (self.heading_deg + self.smooth_steering * 8.0) % 360.0

        # 6. Front Right Leg Screen Swipe Choreography
        if self.smooth_drive > 25.0 and not retreat:
            self.swipe_phase = (self.swipe_phase + 0.15) % (2.0 * np.pi)
            leg_swipe = float(np.sin(self.swipe_phase))
        else:
            leg_swipe = 0.0

        return MotorTelemetry(
            steering_deflection=float(self.smooth_steering),
            forward_drive_pct=float(self.smooth_drive),
            moonwalker_retreat=bool(retreat),
            giant_fiber_jump=bool(jump),
            front_leg_swipe_angle=float(leg_swipe),
            compass_heading_deg=float(self.heading_deg),
        )
